from flask import Flask, request, session, jsonify, render_template, redirect, flash
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
from transformers import AutoModelForCausalLM, AutoTokenizer
from bs4 import BeautifulSoup
import os
import hashlib
import requests
import json
import speech_recognition as sr

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config["MONGO_URI"] = "mongodb://localhost:27017/mindmate"
mongo = PyMongo(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

with open(os.path.join(DATA_DIR, 'articles.json'), 'r') as file:
    articles = json.load(file)

with open(os.path.join(DATA_DIR, 'exercises.json'), 'r') as file:
    exercises = json.load(file)

with open(os.path.join(DATA_DIR, 'professional.json'), 'r') as file:
    professionals = json.load(file)

# Initialize the DialoGPT model and tokenizer
dialogpt_model_name = 'microsoft/DialoGPT-medium'
dialogpt_model = AutoModelForCausalLM.from_pretrained(dialogpt_model_name)
dialogpt_tokenizer = AutoTokenizer.from_pretrained(dialogpt_model_name)

@app.route('/')
def landing_page():
    user = session.get('user')
    return render_template('landing.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.')
    return render_template('landing.html')

@app.route('/register', methods=['POST'])
def register():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = hashlib.sha256(request.form['password'].encode()).hexdigest()
    confirm_password = hashlib.sha256(request.form['confirm_password'].encode()).hexdigest()

    if password != confirm_password:
        flash('Passwords do not match.')
        return render_template('landing.html')

    if mongo.db.users.find_one({'email': email}):
        flash('Email already registered. Please log in.')
        return render_template('landing.html')

    mongo.db.users.insert_one({
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': password
    })

    flash('Registration successful! You can now log in.')
    return render_template('landing.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = hashlib.sha256(request.form['password'].encode()).hexdigest()

    user = mongo.db.users.find_one({'email': email, 'password': password})
    if user:
        session['user'] = {
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email']
        }
        return redirect('/dashboard')
    else:
        flash('Invalid email or password. Please try again.')
        return render_template('landing.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user = session.get('user')
    if not user:
        return redirect('/login')

    if request.method == 'POST':
        if 'profile_pic' in request.files:
            profile_pic = request.files['profile_pic']
            if profile_pic.filename != '':
                filename = secure_filename(profile_pic.filename)
                file_path = os.path.join(app.root_path, 'static/profile_pics', filename)
                profile_pic.save(file_path)
                mongo.db.users.update_one(
                    {'email': user['email']},
                    {'$set': {'profile_pic': 'profile_pics/' + filename}}
                )
                session['user']['profile_pic'] = 'profile_pics/' + filename
        additional_info = request.form.get('additional_info')
        if additional_info:
            mongo.db.users.update_one(
                {'email': user['email']},
                {'$set': {'additional_info': additional_info}}
            )
            session['user']['additional_info'] = additional_info

        return redirect('/')

    return render_template('dashboard.html', user=user)

@app.route('/index.html')
def index_page():
    return render_template('index.html')

@app.route('/feedback.html')
def feedback_page():
    return render_template('feedback.html')

def generate_response(user_input):
    # Tokenize the user input and generate a response
    new_user_input_ids = dialogpt_tokenizer.encode(user_input + dialogpt_tokenizer.eos_token, return_tensors='pt')
    chat_history_ids = new_user_input_ids

    # Generate a response from the model
    response_ids = dialogpt_model.generate(chat_history_ids, max_length=1000, pad_token_id=dialogpt_tokenizer.eos_token_id)
    response = dialogpt_tokenizer.decode(response_ids[:, chat_history_ids.shape[-1]:][0], skip_special_tokens=True)

    # Check if response contains a goodbye message
    goodbye_keywords = ['bye', 'cya', 'talk with you later']
    if any(keyword in response for keyword in goodbye_keywords):
        return response
    else:
        return response

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    response = generate_response(user_input)
    return jsonify({'response': response})

@app.route('/get_info')
def get_info():
    illness = request.args.get('illness')
    
    article = next((item.get('link', "No article found.") for item in articles if item['title'] == illness), "No article found.")
    
    exercise = next((item.get('exercises', "").replace(", ", "\n- ") for item in exercises if item['title'] == illness), "")
    if exercise:
        exercise = "- " + exercise
    
    professional = next((item['info'] for item in professionals if item['title'] == illness), [])

    return jsonify({
        "article": article,
        "exercises": exercise,
        "professionals": professional
    })

def fetch_articles(illness):
    query = f"{illness} articles"
    search_results = google_search(query)
    articles = []
    for result in search_results[:5]:
        articles.append({
            "title": result['title'],
            "summary": result['summary']
        })
    return articles

def fetch_exercises(illness):

    query = f"{illness} exercises"
    search_results = google_search(query)
    exercises = []
    for result in search_results[:10]:  
        exercises.append(result['title'])
    return exercises

def fetch_professionals(illness):
    query = f"{illness} professionals"
    search_results = google_search(query)
    professionals = []
    for result in search_results[:3]:
        professionals.append({
            "Name": result['name'],
            "Specialization": result['specialization'],
            "Clinic": result['clinic']
        })
    return professionals

def google_search(query):
    url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    search_results = []
    for g in soup.find_all('div', class_='g'):
        anchors = g.find_all('a')
        if anchors:
            title = anchors[0].text
            link = anchors[0]['href']
            summary = g.find('div', class_='s').text if g.find('div', class_='s') else ""
            search_results.append({
                "title": title,
                "link": link,
                "summary": summary
            })
    
    return search_results

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    audio_path = os.path.join('tmp', 'audio.wav')

    # Create 'tmp' directory if it does not exist
    os.makedirs('tmp', exist_ok=True)
    
    audio_file.save(audio_path)

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            response = generate_response(text)
            return jsonify({'transcription': text, 'response': response})
        except sr.UnknownValueError:
            return jsonify({'response': 'Sorry, I could not understand the audio.'})
        except sr.RequestError as e:
            return jsonify({'response': f'Sorry, I could not process the audio. Error: {e}'})

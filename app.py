from flask import Flask, request, jsonify, render_template, redirect, session, flash
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
from transformers import BertTokenizer, BertForSequenceClassification
from bs4 import BeautifulSoup
import os
import hashlib
import torch
import requests
import random
import json
import speech_recognition as sr

app = Flask(__name__)
app.secret_key = '2006'
app.config["MONGO_URI"] = "mongodb://localhost:27017/mindmate"
mongo = PyMongo(app)


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

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')

MODEL_NAME = 'bert-mental-health-model'
TOKENIZER_NAME = 'bert-mental-health-tokenizer'

model_path = os.path.join(MODELS_DIR, MODEL_NAME)
tokenizer_path = os.path.join(MODELS_DIR, TOKENIZER_NAME)

model = BertForSequenceClassification.from_pretrained(model_path)
tokenizer = BertTokenizer.from_pretrained(tokenizer_path)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

with open(os.path.join(DATA_DIR, 'KB.json'), 'r') as file:
    data = json.load(file)

with open(os.path.join(DATA_DIR, 'articles.json'), 'r') as file:
    articles = json.load(file)

with open(os.path.join(DATA_DIR, 'exercises.json'), 'r') as file:
    exercises = json.load(file)

with open(os.path.join(DATA_DIR, 'professional.json'), 'r') as file:
    professionals = json.load(file)

responses = {}
for intent in data['intents']:
    if 'responses' in intent:
        responses[intent['tag']] = intent['responses']
    else:
        responses[intent['tag']] = ["Sorry, I don't have a response for that."]

labels = [intent['tag'] for intent in data['intents']]
label2id = {label: idx for idx, label in enumerate(labels)}
id2label = {idx: label for label, idx in label2id.items()}

def predict_intent_and_respond(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    outputs = model(**inputs)
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    predicted_class = predictions.argmax().item()
    intent = id2label[predicted_class]
    response = random.choice(responses[intent])
    return response

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    response = predict_intent_and_respond(user_input)
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
            response = predict_intent_and_respond(text)
            return jsonify({'transcription': text, 'response': response})
        except sr.UnknownValueError:
            return jsonify({'response': 'Sorry, I could not understand the audio.'})
        except sr.RequestError as e:
            return jsonify({'response': f'Sorry, I could not process the audio. Error: {e}'})

if __name__ == '__main__':
    app.run(debug=True)

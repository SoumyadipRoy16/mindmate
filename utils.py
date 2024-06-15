import streamlit as st
import urllib.request
from bs4 import BeautifulSoup
import speech_recognition as sr
from transformers import pipeline

# Initialize named entity recognition (NER) pipeline
nlp_keywords = pipeline("ner", model="dslim/bert-base-NER", tokenizer="dslim/bert-base-NER")

def extract_paragraphs(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(html, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([p.get_text() for p in paragraphs])
        filtered_content = ' '.join(content.split()[:100])
        return filtered_content
    except Exception as e:
        st.error(f"Error extracting content from {url}: {e}")
        return ""

def extract_keywords(text):
    try:
        result = nlp_keywords(text)
        keywords = [entity.get('word') for entity in result if entity.get('score') > 0.5]
        return keywords
    except Exception as e:
        st.error(f"Error extracting keywords: {e}")
        return []

def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = r.listen(source)
        st.info("Processing...")
    try:
        user_input = r.recognize_google(audio)
        return user_input
    except sr.UnknownValueError:
        st.warning("Google Speech Recognition could not understand audio.")
        return ""
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

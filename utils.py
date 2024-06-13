import streamlit as st
import urllib.request
from bs4 import BeautifulSoup
import speech_recognition as sr
from gtts import gTTS
import os

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
        st.error("Sorry, I could not understand what you said.")
        return ""
    except sr.RequestError:
        st.error("Sorry, my speech recognition service is currently unavailable.")
        return ""

def text_to_speech(text, filename='output.mp3'):
    tts = gTTS(text)
    tts.save(filename)
    return filename

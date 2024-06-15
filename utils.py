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
        st.info("Speak your question or concern...")
        audio = r.listen(source)
        try:
            user_input = r.recognize_google(audio)
            st.text_area("Recognized Speech:", value=user_input, height=150)
            return user_input
        except sr.UnknownValueError:
            st.warning("Google Speech Recognition could not understand audio.")
        except sr.RequestError as e:
            st.error(f"Could not request results from Google Speech Recognition service; {e}")

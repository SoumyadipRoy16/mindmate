import streamlit as st
import tempfile
import os
import time
import subprocess
import speech_recognition as sr
from google_search import google_search
from feedback import submit_feedback
from utils import extract_paragraphs
from wit import Wit

# Initialize Wit.ai client
WIT_ACCESS_TOKEN = '67Q6ZJXLDVOIOH5Y43YPFQZW5LSGXDLS'  # Replace with your Wit.ai access token
wit_client = Wit(WIT_ACCESS_TOKEN)

def recognize_speech(audio_file):
    try:
        recognizer = sr.Recognizer()

        # Use speech_recognition library to recognize speech
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)

        # Perform speech recognition
        user_input = recognizer.recognize_google(audio_data)
        return user_input

    except sr.UnknownValueError:
        st.warning("Speech recognition could not understand audio.")
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
    except Exception as e:
        st.error(f"Error in recognizing speech: {e}")

def main():
    st.set_page_config(page_title="MindMate Search", page_icon=":brain:")

    st.title("MindMate")
    st.image("mindmate_logo.png", width=200)

    initial_prompt = st.empty()
    typed_text = ""
    for char in "Hello, I am MindMate. What can I help you with today?":
        typed_text += char
        initial_prompt.text(typed_text)
        time.sleep(0.05)

    st.info("Please click the button below to start recording your speech:")

    uploaded_file = st.file_uploader("Upload audio file (WAV format recommended)", type=["wav"])

    if uploaded_file:
        st.audio(uploaded_file, format='audio/wav')

        if st.button("Submit"):
            try:
                # Perform speech recognition on the uploaded audio file
                user_input = recognize_speech(uploaded_file.name)
                if user_input:
                    st.text_area("Recognized Speech:", value=user_input, height=150)

                    # Example: Perform search based on recognized text
                    search_results = google_search(user_input, 'Articles')
                    if search_results:
                        st.subheader("Top Articles:")
                        for i, result in enumerate(search_results[:5], start=1):
                            title = result.get('title', '')
                            snippet = result.get('snippet', '')
                            link = result.get('link', '')

                            st.markdown(f"### {i}. [{title}]({link})")
                            st.write(snippet)
                            st.write(f"Link: [{link}]({link})")
                            st.write("")

                            content = extract_paragraphs(link)
                            if content:
                                st.markdown(f"#### Extracted Content from [{title}]({link}):")
                                st.text_area(f"Content {i}:", value=content, height=150)

                    else:
                        st.error("No articles found.")

            except Exception as e:
                st.error(f"Error processing audio file: {e}")

    st.sidebar.title("Feedback")
    feedback = st.sidebar.text_area("Enter your feedback here:")
    rating = st.sidebar.slider("Rate your experience (1 = poor, 5 = excellent)", min_value=1, max_value=5, step=1, value=5)

    if st.sidebar.button("Submit Feedback"):
        if feedback.strip() != "":
            submit_feedback(feedback, rating)
        else:
            st.sidebar.warning("Please enter your feedback.")

if __name__ == "__main__":
    main()

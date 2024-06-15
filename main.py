import streamlit as st
import time
import tempfile
import os
import pyaudio
import wave
from google_search import google_search
from feedback import submit_feedback
from utils import extract_paragraphs
from google.cloud import speech_v1p1beta1 as speech

# Function to transcribe speech using Google Cloud Speech-to-Text
def recognize_speech_google(audio_file):
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=audio_file)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )
    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        return result.alternatives[0].transcript
    return None

# Function to record audio from microphone
def record_audio(file_name, duration=5):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    frames = []

    with st.spinner("Recording..."):
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(file_name, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

# Main function to run the Streamlit app
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

    # Radio button to choose input method
    use_speech_recognition = st.radio("Choose input method:", ('Type', 'Speak'))

    if use_speech_recognition == 'Speak':
        st.info("Click the microphone icon and start speaking.")

        # Function to handle microphone recording and speech recognition
        def handle_microphone():
            # Initialize microphone recording
            recording = st.button("🎤 Start Recording")
            if recording:
                tmp_audio_filename = tempfile.NamedTemporaryFile(suffix=".wav").name
                record_audio(tmp_audio_filename)

                # Perform speech recognition on the captured audio
                recognized_text = recognize_speech_google(open(tmp_audio_filename, 'rb').read())
                if recognized_text:
                    st.text_area("Recognized Speech:", value=recognized_text, height=150)
                    search_results = google_search(recognized_text, 'Articles')
                    if search_results:
                        st.subheader("Top Results:")
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

                # Delete temporary audio file
                os.remove(tmp_audio_filename)

        # Display microphone icon and handle speech input
        handle_microphone()

    else:
        user_input = st.text_area("Enter your question or concern:", height=150)
        search_type = st.selectbox("Choose type of response:", ('Articles', 'Links'))

        if st.button("Submit"):
            if user_input:
                with st.spinner("Analyzing your input..."):
                    search_results = google_search(user_input, search_type)
                if search_results:
                    st.subheader(f"Top {search_type} Results:")
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
                    st.error("No results found. Please try again.")
            else:
                st.warning("Please provide your question or concern.")

    # Sidebar for feedback
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

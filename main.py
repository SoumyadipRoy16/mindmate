import streamlit as st
import time
import os
from google_search import google_search
from feedback import submit_feedback
from utils import extract_paragraphs
from google.cloud import speech_v1p1beta1 as speech

# Function to transcribe speech using Google Cloud Speech-to-Text
def recognize_speech_google(audio_file):
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=audio_file.read())
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )
    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        return result.alternatives[0].transcript
    return None

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
            with st.spinner("Listening..."):
                # Use Google Cloud Speech-to-Text for real-time transcription
                with st.audio("audio.wav", format="audio/wav", channels=1, sample_rate=16000, codec="pcm_s16le"):
                    with tempfile.NamedTemporaryFile(delete=False) as tmp_audio_file:
                        tmp_audio_filename = tmp_audio_file.name

                        # Infinite loop to capture audio until the user stops recording
                        while recording:
                            audio_bytes = st.record(key="audio")
                            tmp_audio_file.write(audio_bytes.read())
                            tmp_audio_file.flush()

                            # Perform speech recognition on the captured audio
                            recognized_text = recognize_speech_google(tmp_audio_filename)
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

                            # Check if user has stopped recording
                            recording = st.button("Stop Recording")
                            if not recording:
                                break

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

import streamlit as st
import time
import os
from google_search import google_search
from feedback import submit_feedback
from utils import extract_paragraphs
from google.cloud import speech_v1p1beta1 as speech

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

    use_speech_recognition = st.radio("Choose input method:", ('Type', 'Speak'))

    if use_speech_recognition == 'Speak':
        st.info("Click the button and start speaking.")
        st.markdown("""
            <script>
                let mediaRecorder;
                let audioChunks = [];

                function startRecording() {
                    navigator.mediaDevices.getUserMedia({ audio: true })
                        .then(stream => {
                            mediaRecorder = new MediaRecorder(stream);
                            mediaRecorder.start();

                            mediaRecorder.addEventListener("dataavailable", event => {
                                audioChunks.push(event.data);
                            });

                            mediaRecorder.addEventListener("stop", () => {
                                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                                const audioUrl = URL.createObjectURL(audioBlob);
                                const audio = new Audio(audioUrl);
                                const link = document.createElement('a');
                                link.href = audioUrl;
                                link.download = 'recording.wav';
                                link.click();
                                const fileInput = document.getElementById('fileInput');
                                const dataTransfer = new DataTransfer();
                                dataTransfer.items.add(new File([audioBlob], 'recording.wav'));
                                fileInput.files = dataTransfer.files;
                                document.getElementById('uploadButton').click();
                            });
                        });
                }

                function stopRecording() {
                    mediaRecorder.stop();
                }
            </script>
        """, unsafe_allow_html=True)

        st.button("Start Recording", on_click="startRecording()")
        st.button("Stop Recording", on_click="stopRecording()")
        audio_file = st.file_uploader("Upload Audio", type=["wav"], id="fileInput", key="uploader", on_change=lambda: st.session_state.uploaded=True)
        if st.session_state.get('uploaded', False):
            with st.spinner("Recognizing speech..."):
                user_input = recognize_speech_google(audio_file)
                if user_input:
                    st.text_area("Recognized Speech:", value=user_input, height=150)
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
                else:
                    st.error("Speech recognition failed. Please try again.")
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

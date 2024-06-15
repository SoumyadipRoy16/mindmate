import streamlit as st
from google_search import google_search
from feedback import submit_feedback
from utils import extract_paragraphs
from pydub import AudioSegment
from pydub.generators import Sine
import speech_recognition as sr
import tempfile
import time

def recognize_speech():
    try:
        st.info("Simulating audio input...")

        # Generate a simple sine wave audio segment for 1 second
        sine_wave = Sine(440).to_audio_segment(duration=1000)  # 440 Hz frequency for 1 second
        audio = sine_wave.set_sample_width(2).set_frame_rate(16000)  # Adjust sample width and frame rate

        # Save the audio segment to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_audio_file:
            tmp_audio_filename = tmp_audio_file.name
            audio.export(tmp_audio_filename, format="wav")

            # Use SpeechRecognition to recognize speech from the generated audio
            r = sr.Recognizer()
            with sr.AudioFile(tmp_audio_filename) as source:
                audio_data = r.record(source)

            user_input = r.recognize_google(audio_data)
            st.text_area("Recognized Speech:", value=user_input, height=150)
            return user_input

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
        time.sleep(0.05)  # Use time.sleep() from Python's time module

    use_speech_recognition = st.radio("Choose input method:", ('Type', 'Speak'))

    if use_speech_recognition == 'Speak':
        user_input = recognize_speech()
        if user_input:
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
            st.warning("Speech recognition failed. Please try again.")

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

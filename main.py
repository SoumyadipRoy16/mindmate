import streamlit as st
import time
from pathlib import Path
import av
import numpy as np
import pydub
from collections import deque
from typing import List
from deepspeech import Model
from streamlit_webrtc import WebRtcMode, webrtc_streamer

# Importing other necessary functions and modules
from google_search import google_search
from feedback import submit_feedback
from utils import extract_paragraphs

HERE = Path(__file__).parent

# DeepSpeech model setup
MODEL_URL = "https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.pbmm"
LANG_MODEL_URL = "https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.scorer"
MODEL_LOCAL_PATH = HERE / "models/deepspeech-0.9.3-models.pbmm"
LANG_MODEL_LOCAL_PATH = HERE / "models/deepspeech-0.9.3-models.scorer"

# Download DeepSpeech models if not already downloaded
def download_models():
    def download_file(url, download_to: Path, expected_size=None):
        if download_to.exists():
            if expected_size and download_to.stat().st_size == expected_size:
                return
        else:
            st.info(f"{url} is already downloaded.")
            if not st.button("Download again?"):
                return

        download_to.parent.mkdir(parents=True, exist_ok=True)
        weights_warning, progress_bar = None, None
        try:
            weights_warning = st.warning("Downloading %s..." % url)
            progress_bar = st.progress(0)
            with open(download_to, "wb") as output_file:
                with urllib.request.urlopen(url) as response:
                    length = int(response.info()["Content-Length"])
                    counter = 0.0
                    MEGABYTES = 2.0 ** 20.0
                    while True:
                        data = response.read(8192)
                        if not data:
                            break
                        counter += len(data)
                        output_file.write(data)
                        weights_warning.warning(
                            "Downloading %s... (%6.2f/%6.2f MB)"
                            % (url, counter / MEGABYTES, length / MEGABYTES)
                        )
                        progress_bar.progress(min(counter / length, 1.0))
        finally:
            if weights_warning is not None:
                weights_warning.empty()
            if progress_bar is not None:
                progress_bar.empty()

# Initialize DeepSpeech model
def init_deepspeech_model():
    download_models()
    model = Model(str(MODEL_LOCAL_PATH))
    model.enableExternalScorer(str(LANG_MODEL_LOCAL_PATH))
    return model

# Function for speech-to-text conversion
def recognize_speech(model):
    st.info("Speak your question or concern...")
    webrtc_ctx = webrtc_streamer(
        key="speech-to-text",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        media_stream_constraints={"video": False, "audio": True},
    )

    if not webrtc_ctx.state.playing:
        return None

    status_indicator = st.empty()
    stream = model.createStream()

    while True:
        status_indicator.write("Listening...")

        try:
            audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
        except queue.Empty:
            time.sleep(0.1)
            status_indicator.write("No audio frame received.")
            continue

        sound_chunk = pydub.AudioSegment.empty()

        for audio_frame in audio_frames:
            sound = pydub.AudioSegment(
                data=audio_frame.to_ndarray().tobytes(),
                sample_width=audio_frame.format.bytes,
                frame_rate=audio_frame.sample_rate,
                channels=len(audio_frame.layout.channels),
            )
            sound_chunk += sound

        if len(sound_chunk) > 0:
            sound_chunk = sound_chunk.set_channels(1).set_frame_rate(model.sampleRate())
            buffer = np.array(sound_chunk.get_array_of_samples())
            stream.feedAudioContent(buffer)
            text = stream.intermediateDecode()
            return text

# Main Streamlit app
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

    model = init_deepspeech_model()

    if use_speech_recognition == 'Speak':
        user_input = recognize_speech(model)
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

import streamlit as st
from google_search import google_search
from feedback import submit_feedback
from utils import extract_paragraphs
from wit import Wit
import time
import speech_recognition as sr

# Initialize Wit.ai client
WIT_ACCESS_TOKEN = os.getenv('WIT_ACCESS_TOKEN')# Replace with your Wit.ai access token
wit_client = Wit(WIT_ACCESS_TOKEN)

def recognize_speech():
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Speak your question or concern...")
            audio = r.listen(source, timeout=5)  # Adjust timeout as needed

        # Use Wit.ai for speech recognition
        response = wit_client.speech(audio.get_wav_data(), {'Content-Type': 'audio/wav'})

        # Extract recognized text from Wit.ai response
        if 'text' in response:
            user_input = response['text']
            st.text_area("Recognized Speech:", value=user_input, height=150)
            return user_input
        else:
            st.error("No recognized speech found. Please try again.")

    except sr.WaitTimeoutError:
        st.warning("Timeout: No speech detected.")
    except sr.UnknownValueError:
        st.warning("Speech recognition could not understand audio.")
    except sr.RequestError as e:
        st.error(f"Could not request results from Wit.ai service; {e}")
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

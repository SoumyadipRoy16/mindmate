import streamlit as st
import time
import os
from google_search import google_search
#from qa_model import answer_question_bert
from feedback import submit_feedback
from utils import extract_paragraphs, recognize_speech, text_to_speech

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
        st.info("Speak your question or concern...")
        is_listening = False
        while True:
            if not is_listening:
                st.write("")
                is_listening = True
                user_input = recognize_speech()
                if not user_input:
                    st.write("Speech recognition failed. Please try again.")
                    break

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

                            if st.button(f"Listen to Content {i}"):
                                filename = text_to_speech(content)
                                audio_file = open(filename, 'rb')
                                audio_bytes = audio_file.read()
                                st.audio(audio_bytes, format='audio/mp3')
                                os.remove(filename)

                else:
                    st.error("No articles found.")

                st.write("")
                is_listening = False
                if not st.button("Continue Speaking"):
                    break

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

                            if st.button(f"Listen to Content {i}"):
                                filename = text_to_speech(content)
                                audio_file = open(filename, 'rb')
                                audio_bytes = audio_file.read()
                                st.audio(audio_bytes, format='audio/mp3')
                                os.remove(filename)

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

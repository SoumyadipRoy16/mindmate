import streamlit as st
from transformers import pipeline

nlp = pipeline('question-answering', model='bert-large-uncased-whole-word-masking-finetuned-squad')

def answer_question_bert(question, context):
    try:
        answer = nlp({
            'question': question,
            'context': context
        })
        return answer['answer']
    except Exception as e:
        st.error(f"Error answering question: {e}")
        return "Sorry, I couldn't find an answer."

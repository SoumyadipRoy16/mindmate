import streamlit as st

def submit_feedback(feedback, rating):
    # Here you would typically save the feedback and rating to a database or file
    # For demonstration purposes, we'll just display the feedback and rating
    st.success("Thank you for your feedback!")
    st.write("Feedback:", feedback)
    st.write("Rating:", rating)

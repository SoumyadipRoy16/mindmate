import streamlit as st
from app import create_app  # Import the create_app function from your Flask app

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

# Create your Flask app
app = create_app()

# Run the Flask app using Werkzeug
def run_flask_app():
    run_simple('0.0.0.0', 8000, app, use_reloader=False, use_debugger=False)

st.title("My Flask and Streamlit App")

# Embed the Flask app in an iframe
st.markdown(f'<iframe src="http://localhost:8000" width="100%" height="600"></iframe>', unsafe_allow_html=True)

# Run the Flask app in a background thread
from threading import Thread
flask_thread = Thread(target=run_flask_app)
flask_thread.start()

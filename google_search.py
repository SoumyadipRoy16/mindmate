import streamlit as st
import requests

API_KEY = ''
SEARCH_ENGINE_ID = ''

def google_search(query, search_type):
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            results = response.json().get('items', [])
            return results
        else:
            st.error(f"Error fetching Google search results: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching Google search results: {e}")
        return []

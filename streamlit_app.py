import streamlit as st
import google.generativeai as genai
import requests
import os
from gtts import gTTS
from datetime import datetime, timedelta
from io import BytesIO

# Configure the API keys securely using Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# App Title and Description
st.title("AI-Powered Ghostwriter with Anti-Abuse Features")
st.write("Generate creative content, ensure its originality, and turn it into an audio podcast. Usage is limited to 3 generations every 15 minutes.")

# Step 1: Input Prompt
st.subheader("Step 1: Enter your content idea")
prompt = st.text_input("What would you like to write about?", placeholder="e.g. AI trends in 2025")

# Anti-abuse: Rate-limiting and session tracking
if "generation_count" not in st.session_state:
    st.session_state.generation_count = 0
    st.session_state.first_request_time = datetime.now()

# Check if the 15-minute cooldown has passed
def check_cooldown():
    """Checks if the 15-minute cooldown period has passed."""
    time_since_first_request = datetime.now() - st.session_state.first_request_time
    if time_since_first_request > timedelta(minutes=15):
        # Reset the counter after 15 minutes
        st.session_state.generation_count = 0
        st.session_state.first_request_time = datetime.now()

# Function to handle web search
def search_web(query):
    """Searches the web using Google Custom Search API and returns results."""
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": st.secrets["GOOGLE_API_KEY"],
        "cx": st.secrets["GOOGLE_SEARCH_ENGINE_ID"],
        "q": query,
    }
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        st.error(f"Search API Error: {response.status_code} - {response.text}")
        return []

# Function to regenerate content for originality
def regenerate_content(original_content):
    """Generates rewritten content based on the original content to ensure originality."""
    model = genai.GenerativeModel('gemini-1.5-flash-8b')
    prompt = f"Rewrite the following content to make it original and distinct:\n\n{original_content}"
    response = model.generate_content(prompt)
    return response.text.strip()

# Function to convert text to speech using gTTS
def text_to_speech(text):
    """Converts the provided text to speech and returns it as an audio stream."""
    tts = gTTS(text, lang='en')
    audio_file = BytesIO()
    tts.save(audio_file)
    audio_file.seek(0)  # Reset pointer to the beginning of the audio
    return audio_file

# Anti-abuse: Check the generation limit
def check_generation_limit():
    """Checks if the user has exceeded the allowed number of generations."""
    check_cooldown()
    if st.session_state.generation_count >= 3:
        st.warning("You have exceeded the limit of 3 generations in the last 15 minutes. Please try again later.")
        return False
    return True

# Content Generation and Search for Similarity (Step 2)
if prompt.strip():
    # Check if the user has exceeded the generation limit
    if check_generation_limit():
        if st.button("Generate Content"):
            with st.spinner("Generating content... Please wait!"):
                try:
                    # Set the generation_config to control output tokens
                    generation_config = {
                        "temperature": 1,
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 500,  # Adjust token limit based on your needs
                        "response_mime_type": "text/plain",
                    }

                    # Create the model and start chat session

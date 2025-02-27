import streamlit as st
import google.generativeai as genai
import requests
import time
from gtts import gTTS
import io

# Configure the API keys securely using Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# App Title and Description
st.title("AI-Powered Ghostwriter")
st.write("Generate creative content and create your own podcast.")

# Step 1: Input Prompt
st.subheader("Step 1: Enter your content idea")
prompt = st.text_input("What would you like to write about?", placeholder="e.g. AI trends in 2025")

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
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Rewrite the following content to make it original and distinct:\n\n{original_content}"
    response = model.generate_content(prompt)
    return response.text.strip()

# Function to convert text to speech
def text_to_speech(text):
    """Convert the provided text to speech and return the audio."""
    tts = gTTS(text=text, lang='en')
    audio_file = io.BytesIO()
    tts.save(audio_file)
    audio_file.seek(0)  # Rewind the file pointer to the beginning
    return audio_file

# Content Generation (Step 2)
if prompt.strip():
    if st.button("Generate Podcast"):
        with st.spinner("Generating content... Please wait!"):
            try:
                # Generate content using Generative AI
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                generated_text = response.text.strip()

                # Display the generated content with feedback
                st.subheader("Step 2: Your Generated Content")
                st.write(generated_text)

                # Convert the generated content to speech
                audio_file = text_to_speech(generated_text)
                st.subheader("Step 3: Listen to the Generated Content")
                st.audio(audio_file, format="audio/mp3", start_time=0)

            except Exception as e:
                st.error(f"Error generating content: {e}")

else:
    st.info("Enter your idea in the text box above to start.")

# Option to regenerate content for originality (if desired)
if st.button("Regenerate Content for Originality"):
    if 'generated_text' in st.session_state:
        regenerated_text = regenerate_content(st.session_state.generated_text)
        st.session_state.generated_text = regenerated_text
        st.success("Content successfully regenerated for originality.")
        st.subheader("Regenerated Content:")
        st.write(regenerated_text)

# Option to clear the input and reset the app
if st.button("Clear Input"):
    st.session_state.generated_text = ""
    st.experimental_rerun()  # Reset the app state

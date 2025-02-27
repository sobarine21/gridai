import streamlit as st
import google.generativeai as genai
import requests
import time
from gtts import gTTS
import os
from datetime import datetime, timedelta

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
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Rewrite the following content to make it original and distinct:\n\n{original_content}"
    response = model.generate_content(prompt)
    return response.text.strip()

# Function to convert text to speech using gTTS
def text_to_speech(text, filename="generated_content.mp3"):
    """Converts the provided text to speech and saves it as an MP3 file."""
    tts = gTTS(text, lang='en')
    tts.save(filename)
    return filename

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
                    # Generate content using Generative AI
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                    generated_text = response.text.strip()

                    # Check if the generated content exceeds the 2500 character limit
                    if len(generated_text) > 2500:
                        st.warning("The generated content exceeds the 2500 character limit. Truncating the content.")
                        generated_text = generated_text[:2500]

                    # Display the generated content with feedback
                    st.subheader("Step 2: Your Generated Content")
                    st.write(generated_text)

                    # Option to generate a podcast (Text-to-Speech)
                    if st.button("Generate Podcast (Text-to-Speech)"):
                        with st.spinner("Converting to speech..."):
                            audio_filename = text_to_speech(generated_text)
                            st.success("Podcast generated successfully!")
                            st.audio(audio_filename, format="audio/mp3")

                    # Increment generation count
                    st.session_state.generation_count += 1

                    # Check for similar content online (Step 3)
                    st.subheader("Step 3: Searching for Similar Content Online")
                    search_results = search_web(generated_text)

                    if search_results:
                        st.warning("We found similar content on the web:")

                        # Display results in a compact, user-friendly format
                        for result in search_results[:3]:  # Show only the top 3 results
                            with st.expander(result['title']):
                                st.write(f"**Source:** [{result['link']}]({result['link']})")
                                st.write(f"**Snippet:** {result['snippet'][:150]}...")  # Shortened snippet
                                st.write("---")

                        # Option to regenerate content for originality
                        regenerate_button = st.button("Regenerate Content for Originality")
                        if regenerate_button:
                            with st.spinner("Regenerating content..."):
                                regenerated_text = regenerate_content(generated_text)
                                st.session_state.generated_text = regenerated_text
                                st.success("Content successfully regenerated for originality.")
                                st.subheader("Regenerated Content:")
                                st.write(regenerated_text)

                    else:
                        st.success("Your content appears to be original. No similar content found online.")

                except Exception as e:
                    st.error(f"Error generating content: {e}")
    else:
        st.info("You have exceeded your content generation limit. Please wait 15 minutes before generating more content.")
else:
    st.info("Enter your idea in the text box above to start.")

# Option to clear the input and reset the app
if st.button("Clear Input"):
    st.session_state.generated_text = ""
    st.experimental_rerun()  # Reset the app state

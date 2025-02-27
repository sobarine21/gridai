import streamlit as st
import google.generativeai as genai
import requests
import time
from gtts import gTTS
import os

# Configure the API keys securely using Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# App Title and Description
st.title("AI-Powered Ghostwriter")
st.write("Generate creative content and ensure its originality, step by step.")

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

# Function to generate podcast using Google gTTS
def generate_podcast(text):
    """Generates a podcast (audio file) from the given text using gTTS."""
    try:
        tts = gTTS(text, lang='en')
        podcast_path = "podcast.mp3"
        tts.save(podcast_path)
        return podcast_path
    except Exception as e:
        st.error(f"Error generating podcast: {e}")
        return None

# Content Generation and Search for Similarity (Step 2)
if prompt.strip():
    if st.button("Generate Content"):
        with st.spinner("Generating content... Please wait!"):
            try:
                # Generate content using Generative AI
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                generated_text = response.text.strip()

                # Limit the generated content to 2500 characters
                if len(generated_text) > 2500:
                    generated_text = generated_text[:2500]

                # Display the generated content with feedback
                st.subheader("Step 2: Your Generated Content")
                st.write(generated_text)

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

                # Option to generate podcast
                if st.button("Generate Podcast"):
                    with st.spinner("Generating podcast... Please wait!"):
                        podcast_path = generate_podcast(generated_text)
                        if podcast_path:
                            st.audio(podcast_path, format='audio/mp3')
                            st.success("Podcast generated successfully!")

            except Exception as e:
                st.error(f"Error generating content: {e}")
else:
    st.info("Enter your idea in the text box above to start.")

# Option to clear the input and reset the app
if st.button("Clear Input"):
    st.session_state.generated_text = ""
    st.experimental_rerun()  # Reset the app state

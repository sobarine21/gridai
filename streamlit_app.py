import streamlit as st
import google.generativeai as genai
import requests

# Configure the API keys securely using Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# App Title and Description
st.title("AI-Powered Ghostwriter")
st.write("Generate high-quality content and ensure originality with Generative AI.")

# Prompt Input Field
prompt = st.text_input("Enter your prompt:", placeholder="e.g. Blog about AI trends in 2025.")

# Search Web Functionality
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

# Function to regenerate and rewrite content to make it original
def regenerate_content(original_content):
    """Generates rewritten content based on the original content to ensure originality."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Rewrite the following content to make it original and distinct:\n\n{original_content}"
    response = model.generate_content(prompt)
    return response.text.strip()

# Content Generation and Search for Similarity
if 'generated_text' not in st.session_state:
    st.session_state.generated_text = ""

if 'regenerate_clicked' not in st.session_state:
    st.session_state.regenerate_clicked = False

# Generate Content Button
if st.button("Generate Response") and prompt.strip():
    try:
        # Generate content using Generative AI
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        generated_text = response.text.strip()

        # Store generated content in session state
        st.session_state.generated_text = generated_text
        st.session_state.regenerate_clicked = False  # Reset regenerate state

        # Display the generated content
        st.subheader("Generated Content:")
        st.write(generated_text)

        # Check for similar content online
        st.subheader("Searching for Similar Content Online:")
        search_results = search_web(generated_text)

        if search_results:
            st.warning("Similar content found online:")

            # Use expander to show search results in a compact form
            for result in search_results[:3]:  # Show only top 3 results for a quick view
                with st.expander(result['title']):
                    st.write(f"**Source:** [{result['link']}]({result['link']})")
                    st.write(f"**Snippet:** {result['snippet'][:150]}...")  # Shorten snippet
                    st.write("---")

            # Option to regenerate content if similarity is found
            if st.button("Regenerate Content"):
                # Regenerate content for originality
                regenerated_text = regenerate_content(generated_text)
                st.session_state.generated_text = regenerated_text
                st.session_state.regenerate_clicked = True
                st.success("Content has been regenerated for originality.")
                st.subheader("Regenerated Content:")
                st.write(regenerated_text)

        else:
            st.success("No similar content found online. Your content seems original!")

    except Exception as e:
        st.error(f"Error generating content: {e}")

# Display regenerated content if applicable
if st.session_state.regenerate_clicked:
    st.subheader("Regenerated Content (After Adjustments for Originality):")
    st.write(st.session_state.generated_text)

# Option to clear the prompt and content
if st.button("Clear"):
    st.session_state.generated_text = ""
    st.session_state.regenerate_clicked = False
    st.experimental_rerun()  # Reset the app

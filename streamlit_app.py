import streamlit as st
import google.generativeai as genai
import requests

# Configure the API keys securely using Streamlit's secrets
# Ensure to add the following keys in secrets.toml or Streamlit Cloud Secrets:
# - GOOGLE_API_KEY: API key for Google Generative AI
# - GOOGLE_SEARCH_ENGINE_ID: Google Custom Search Engine ID
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# App Title and Description
st.title("AI-Powered Ghostwriter")
st.write("Generate high-quality content and check for originality using the power of Generative AI and Google Search.")

# Prompt Input Field
prompt = st.text_area("Enter your prompt:", placeholder="Write a blog about AI trends in 2025.")

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
    
    # Explicitly request the model to rewrite and paraphrase the content.
    prompt = f"Rewrite the following content to make it original and distinct. Ensure it is paraphrased and does not match existing content:\n\n{original_content}"
    
    response = model.generate_content(prompt)
    return response.text.strip()

# Button handling for content generation and regeneration
if 'generated_text' not in st.session_state:
    st.session_state.generated_text = ""

if 'regenerate_clicked' not in st.session_state:
    st.session_state.regenerate_clicked = False

# Generate Content Button
if st.button("Generate Response"):
    if not prompt.strip():
        st.error("Please enter a valid prompt.")
    else:
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

            # Check if the content exists on the web
            st.subheader("Searching for Similar Content Online:")
            search_results = search_web(generated_text)

            if search_results:
                st.warning("Similar content found on the web:")

                # Create a dashboard-like display for the search results
                for result in search_results[:5]:  # Show top 5 results
                    with st.expander(result['title']):
                        st.write(f"**Source:** [{result['link']}]({result['link']})")
                        st.write(f"**Snippet:** {result['snippet']}")
                        st.write("---")

                # Option to regenerate content if similarity is found
                st.warning("To ensure 100% originality, you can regenerate the content.")
                if st.button("Regenerate Content"):
                    # Regenerate content by rewriting it for originality
                    regenerated_text = regenerate_content(generated_text)
                    st.session_state.generated_text = regenerated_text
                    st.session_state.regenerate_clicked = True  # Mark regenerate action
                    st.success("Content has been regenerated for originality.")
                    st.subheader("Regenerated Content:")
                    st.write(regenerated_text)

            else:
                st.success("No similar content found online. Your content seems original!")

        except Exception as e:
            st.error(f"Error generating content: {e}")

# Display the regenerated content if applicable
if st.session_state.regenerate_clicked:
    st.subheader("Regenerated Content (After Adjustments for Originality):")
    st.write(st.session_state.generated_text)

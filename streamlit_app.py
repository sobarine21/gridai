import streamlit as st
import google.generativeai as genai
import requests

# Configure the API keys securely using Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Default settings for generation and originality
default_length = 500  # Length in words
default_originality_level = 100  # Default is 100% originality

# Main page setup
st.title("AI-Powered Ghostwriter")
st.write("Generate high-quality content and check for originality using Generative AI and Google Search.")

# User input for prompt
prompt = st.text_area("Enter your prompt:", placeholder="Write about AI trends in 2025.", value="AI trends in 2025")

# Content length slider
length = st.slider("Content Length", 100, 1500, default_length)  # 500 by default

# Button to generate content
if st.button("Generate Content"):
    if not prompt.strip():
        st.error("Please enter a valid prompt.")
    else:
        try:
            # Generate content using Generative AI
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            generated_text = response.text.strip()
            
            # Display generated content
            st.subheader("Generated Content:")
            st.write(generated_text)
            
            # Provide options to download or save content
            st.download_button("Download as .txt", generated_text, file_name="generated_content.txt")
            st.download_button("Download as .docx", generated_text, file_name="generated_content.docx")
            
            # Call the originality check function after content is generated
            st.subheader("Originality Check")
            originality_score = check_originality(generated_text)
            
            # Display originality score
            st.write(f"Originality Score: {originality_score}%")
            
            if originality_score < default_originality_level:
                st.warning(f"Your content is only {originality_score}% original. You may want to refine it.")
                if st.button("Make Content 100% Original"):
                    regenerate_content(prompt)  # Regenerate content to make it more original
            else:
                st.success("Your content is highly original!")
        
        except Exception as e:
            st.error(f"Error generating content: {e}")

# Function to check originality using Google Custom Search API
def check_originality(content):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": st.secrets["GOOGLE_API_KEY"],
        "cx": st.secrets["GOOGLE_SEARCH_ENGINE_ID"],
        "q": content,
    }
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        search_results = response.json().get("items", [])
        return calculate_originality_score(search_results)
    else:
        st.error(f"Search API Error: {response.status_code} - {response.text}")
        return 100  # Assume 100% originality if there is an error

# Function to calculate originality score based on search results
def calculate_originality_score(search_results):
    if not search_results:
        return 100  # No results, assume content is fully original
    score = 100
    for result in search_results[:5]:  # Check top 5 search results
        # If the snippet is too long, consider it a match
        if len(result['snippet']) > 200:
            score -= 10  # Decrease score for each similar snippet found
    return max(score, 0)

# Function to regenerate content with more original parameters
def regenerate_content(prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Adjust prompt or parameters to encourage more originality
        adjusted_prompt = f"Create a highly original version of this: {prompt}"
        response = model.generate_content(adjusted_prompt)
        
        generated_text = response.text.strip()
        st.subheader("Regenerated Content:")
        st.write(generated_text)
        
        st.download_button("Download Regenerated Content as .txt", generated_text, file_name="regenerated_content.txt")
        st.download_button("Download Regenerated Content as .docx", generated_text, file_name="regenerated_content.docx")
        
    except Exception as e:
        st.error(f"Error regenerating content: {e}")

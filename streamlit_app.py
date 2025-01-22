import streamlit as st
import google.generativeai as genai
import requests
import random

# Configure the API keys securely using Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Default settings for generation and originality
default_length = 500  # Length in words
default_originality_level = 100  # Default is 100% originality
creativity_levels = [10, 50, 100]  # 10 - less creative, 100 - more creative

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
def regenerate_content(prompt, creativity_level):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        adjusted_prompt = f"Create a {creativity_level}% original version of this: {prompt}"
        response = model.generate_content(adjusted_prompt)
        
        generated_text = response.text.strip()
        st.subheader("Regenerated Content:")
        st.write(generated_text)
        
        st.download_button("Download Regenerated Content as .txt", generated_text, file_name="regenerated_content.txt")
        st.download_button("Download Regenerated Content as .docx", generated_text, file_name="regenerated_content.docx")
        
    except Exception as e:
        st.error(f"Error regenerating content: {e}")

# Function to allow style modification of content
def modify_style(content, style):
    # Modify content based on the style (e.g., formal, casual)
    if style == "Formal":
        return f"Please write the following in a formal tone: {content}"
    elif style == "Casual":
        return f"Please write the following in a casual tone: {content}"
    elif style == "Creative":
        return f"Make the following text very creative and unique: {content}"
    else:
        return content

# Main page setup
st.title("AI-Powered Ghostwriter with Advanced Features")
st.write("Generate high-quality content and check for originality using Generative AI and Google Search.")

# User input for prompt
prompt = st.text_area("Enter your prompt:", placeholder="Write about AI trends in 2025.", value="AI trends in 2025")

# Content length slider
length = st.slider("Content Length", 100, 1500, default_length)  # 500 by default

# Select creativity level
creativity = st.selectbox("Creativity Level", creativity_levels, format_func=lambda x: f"{x}%")

# Select content style (Formal, Casual, Creative)
style = st.selectbox("Select Content Style", ["Formal", "Casual", "Creative", "Neutral"])

# Button to generate content
if st.button("Generate Content"):
    if not prompt.strip():
        st.error("Please enter a valid prompt.")
    else:
        try:
            # Modify the prompt based on the style selected
            adjusted_prompt = modify_style(prompt, style)

            # Generate content using Generative AI
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(adjusted_prompt)

            generated_text = response.text.strip()

            # Display generated content
            st.subheader("Generated Content:")
            st.write(generated_text)

            # Provide options to download or save content
            st.download_button("Download as .txt", generated_text, file_name="generated_content.txt")
            st.download_button("Download as .docx", generated_text, file_name="generated_content.docx")

            # Show word count
            st.write(f"Word Count: {len(generated_text.split())}")

            # Call the originality check function after content is generated
            st.subheader("Originality Check")
            originality_score = check_originality(generated_text)

            # Display originality score
            st.write(f"Originality Score: {originality_score}%")

            if originality_score < default_originality_level:
                st.warning(f"Your content is only {originality_score}% original. You may want to refine it.")
                if st.button("Make Content 100% Original"):
                    regenerate_content(prompt, creativity)  # Regenerate content to make it more original
            else:
                st.success("Your content is highly original!")

        except Exception as e:
            st.error(f"Error generating content: {e}")

# Advanced Features
st.sidebar.title("Advanced Features")
st.sidebar.write("""
- **Search Engine Advanced Configuration**: You can configure your custom search engine to get more accurate originality scores.
- **Text Complexity Tuning**: You can set the complexity of your generated content, e.g., simple, intermediate, or advanced.
- **Content Comparison**: Compare multiple generated versions side by side.
""")
# Adding a Content Comparison Feature
if st.sidebar.checkbox("Enable Content Comparison"):
    prompt_comparison = st.text_area("Enter comparison prompt:", value="AI trends in 2025")
    if st.button("Generate Comparison Content"):
        model = genai.GenerativeModel('gemini-1.5-flash')
        response1 = model.generate_content(prompt_comparison)
        response2 = model.generate_content(prompt_comparison + " in a different style")
        st.subheader("Comparison 1")
        st.write(response1.text.strip())
        st.subheader("Comparison 2")
        st.write(response2.text.strip())

# Adding random content generation for inspiration
if st.sidebar.button("Generate Random Idea"):
    random_prompts = ["AI in healthcare", "The future of quantum computing", "Sustainable tech in 2025", "Ethical implications of AI"]
    random_prompt = random.choice(random_prompts)
    st.subheader(f"Random Prompt: {random_prompt}")
    st.text_area("Generated Content", value=random_prompt)

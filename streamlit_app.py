import streamlit as st
import google.generativeai as genai
import requests

# Configure the API keys securely using Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Sidebar for navigation
st.sidebar.title("AI Ghostwriter")
sidebar_selection = st.sidebar.radio("Go to", ["Home", "Generate Content", "Originality Dashboard", "Settings"])

# Default settings for generation and originality
default_tone = "Neutral"
default_length = 500  # Length in words
default_originality_level = 100  # Default is 100% originality

# Home Page
if sidebar_selection == "Home":
    st.title("AI-Powered Ghostwriter")
    st.write("Generate high-quality content and check for originality using Generative AI and Google Search.")
    st.write("Navigate using the sidebar for different features.")

# Generate Content Page
elif sidebar_selection == "Generate Content":
    st.subheader("Generate Your Content")
    prompt = st.text_area("Enter your prompt:", placeholder="Write about AI trends in 2025.", value="AI trends in 2025")
    tone = st.selectbox("Select Tone", ["Neutral", "Casual", "Formal", "Excited"], index=0)  # Neutral by default
    length = st.slider("Content Length", 100, 1500, default_length)  # 500 by default
    
    if st.button("Generate Content"):
        if not prompt.strip():
            st.error("Please enter a valid prompt.")
        else:
            try:
                # Adjust the prompt to influence the tone
                adjusted_prompt = adjust_prompt_tone(prompt, tone)

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
                
            except Exception as e:
                st.error(f"Error generating content: {e}")

# Originality Dashboard Page
elif sidebar_selection == "Originality Dashboard":
    st.title("Originality Dashboard")
    
    prompt = st.text_area("Enter your content or prompt to check originality:", placeholder="Write your content here...", value="AI trends in 2025")
    originality_level = st.slider("Adjust Originality Level", 0, 100, default_originality_level)  # 100% by default
    
    if st.button("Check Originality"):
        if not prompt.strip():
            st.error("Please enter content to check originality.")
        else:
            # Check originality using a web search (Google Custom Search API)
            search_results = search_web(prompt)
            originality_score = calculate_originality_score(search_results)
            
            st.subheader(f"Originality Score: {originality_score}%")
            st.write("Content similarity with online resources.")
            
            if originality_score < originality_level:
                st.warning(f"Your content is only {originality_score}% original. You may want to refine it further.")
                st.button("Refine Content")
            else:
                st.success("Your content is highly original!")
            
            st.write("You can adjust the originality level using the slider to make sure your content is unique.")
            
            # Option to regenerate content based on user settings
            if originality_score < originality_level:
                if st.button("Regenerate Content"):
                    regenerate_content(prompt, originality_level)
                    
# Settings Page
elif sidebar_selection == "Settings":
    st.title("App Settings")
    st.write("Customize your experience.")
    dark_mode = st.checkbox("Enable Dark Mode", value=True)
    if dark_mode:
        st.write("Dark mode activated!")
    else:
        st.write("Light mode activated!")

# Function to search the web using Google Custom Search API
def search_web(query):
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

# Function to calculate originality score based on search results
def calculate_originality_score(search_results):
    if not search_results:
        return 100  # No results, assume content is fully original
    score = 100
    for result in search_results[:5]:  # Check top 5 search results
        # Basic example: compare content length ratio, you can integrate more sophisticated comparison
        if len(result['snippet']) > 200:  # If the snippet is too long, consider it a match
            score -= 10  # Decrease score for each similar snippet found
    return max(score, 0)

# Function to regenerate content with more original parameters
def regenerate_content(prompt, originality_level):
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

# Function to adjust the tone of the prompt
def adjust_prompt_tone(prompt, tone):
    tone_map = {
        "Neutral": "",
        "Casual": "Make this more casual and friendly:",
        "Formal": "Make this more formal and professional:",
        "Excited": "Make this more enthusiastic and excited:"
    }
    return f"{tone_map.get(tone, '')} {prompt}"

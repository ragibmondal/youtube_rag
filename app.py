import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
load_dotenv()
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from io import BytesIO
from PIL import Image
import json
import base64
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import re

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set page configuration
st.set_page_config(
    page_title="Advanced Global Content Studio",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="auto"
)

# Define custom CSS
custom_css = """
<style>
    /* General styles */
    body {
        font-family: 'Helvetica Neue', sans-serif;
        background-color: #f8f8f8;
        color: #333;
    }

    /* Heading styles */
    h1, h2, h3, h4, h5, h6 {
        font-weight: bold;
        color: #2B8BED;
    }

    /* Button styles */
    .stButton > button {
        background-color: #2B8BED;
        color: #fff;
        border: none;
        border-radius: 4px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #1E6CC8;
    }

    /* Input field styles */
    .stTextInput > div > div > input {
        font-size: 16px;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 4px;
    }

    /* Dropdown styles */
    .stSelectbox > div > div > div {
        font-size: 16px;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 4px;
    }

    /* Radio button styles */
    .stRadio > label > div {
        font-size: 16px;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 4px;
        background-color: #fff;
        transition: all 0.3s ease;
    }
    .stRadio > label > div:hover {
        background-color: #f0f0f0;
    }

    /* Slider styles */
    .stSlider > div > div > div {
        font-size: 16px;
    }

    /* Expander styles */
    .stExpander > div > div > div > div {
        background-color: #fff;
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 20px;
    }

    /* Sidebar styles */
    .sidebar .sidebar-content {
        background-color: #2B8BED;
        color: #fff;
        padding: 20px;
    }
    .sidebar h3 {
        color: #fff;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .sidebar p {
        color: #fff;
        margin-bottom: 20px;
    }

    /* HoverInfo styles */
    .hover-info {
        background-color: #333;
        color: #fff;
        padding: 10px;
        border-radius: 4px;
        font-size: 14px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Helper functions
def extract_video_id(youtube_url):
    if 'youtu.be' in youtube_url:
        return youtube_url.split('/')[-1]
    elif 'v=' in youtube_url:
        return youtube_url.split('v=')[1].split('&')[0]
    else:
        return None

def extract_transcript(video_id, language='en'):
    try:
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        return transcript_text
    except Exception as e:
        st.error(f"Failed to fetch transcript: {str(e)}")
        return None

def generate_content(transcript, prompt, tone, length, model_name="gemini-1.5-pro-latest"):
    model = genai.GenerativeModel(model_name)
    transcript_text = " ".join([i["text"] for i in transcript])
    full_prompt = f"{prompt}\n\nTranscript:\n{transcript_text}\n\nTone: {tone}\nLength: {length}"
    response = model.generate_content(full_prompt)
    return response.text

def get_video_metadata(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={os.getenv('YOUTUBE_API_KEY')}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["items"]:
            return data["items"][0]["snippet"]
    return None

def generate_srt(transcript):
    srt = ""
    for i, segment in enumerate(transcript, 1):
        start = segment['start']
        duration = segment['duration']
        end = start + duration
        text = segment['text']
        srt += f"{i}\n{start:.3f} --> {end:.3f}\n{text}\n\n"
    return srt

def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="transcript_analysis.csv">Download Transcript Analysis (CSV)</a>'
    return href

def main():
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.title("Advanced Global Content Studio")
        st.write("This advanced global studio uses AI to transform YouTube videos into rich, multilingual content with analytics. Perfect for international content creators, global marketers, researchers, and anyone looking to deeply understand and reach a diverse audience! 🌐🎓🚀")
        st.write("Made with ❤️ by Ragib")
        st.markdown('</div>', unsafe_allow_html=True)

    # Main content
    st.title("🌐 Transform YouTube Videos into Global Content")
    st.write("Create rich, multilingual content from YouTube videos with advanced analytics and AI.")

    # YouTube video link input
    youtube_link = st.text_input("Enter YouTube Video Link:", placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ", key="video_link")

    # Input validation
    if youtube_link:
        video_id = extract_video_id(youtube_link)
        if video_id:
            metadata = get_video_metadata(video_id)
            if metadata:
                # Video metadata
                st.header(metadata["title"])
                st.image(metadata["thumbnails"]["high"]["url"], use_column_width=True)
                st.write(f"**Channel:** {metadata['channelTitle']} | **Published:** {metadata['publishedAt'][:10]}")
                st.write(metadata["description"])

                # Content generation options
                col1, col2, col3 = st.columns(3)
                with col1:
                    content_type = st.selectbox("Select Content Type:", ["News Article", "Blog Post", "Social Media Post", "Email Newsletter", "Product Description", "Academic Summary"], help="Choose the type of content you want to generate from the video transcript.")
                with col2:
                    tone = st.selectbox("Select Tone:", ["Informative", "Casual", "Professional", "Humorous", "Inspirational", "Empathetic", "Persuasive"], help="Choose the tone or style for the generated content.")
                with col3:
                    languages = {
                        "English": "en", "Spanish": "es", "French": "fr", "German": "de", "Italian": "it",
                        "Japanese": "ja", "Korean": "ko", "Portuguese": "pt", "Russian": "ru",
                        "Chinese (Simplified)": "zh-Hans", "Chinese (Traditional)": "zh-Hant",
                        "Arabic": "ar", "Hindi": "hi", "Bengali": "bn", "Urdu": "ur", "Turkish": "tr",
                        "Dutch": "nl", "Polish": "pl", "Swedish": "sv", "Thai": "th", "Vietnamese": "vi",
                        "Greek": "el", "Hebrew": "he", "Indonesian": "id", "Malay": "ms", "Filipino": "fil"
                    }
                    input_language = st.selectbox("Select Transcript Language:", list(languages.keys()), help="Choose the language of the video transcript.")

                length = st.slider("Content Length:", min_value=100, max_value=5000, value=500, step=100, help="Adjust the length of the generated content.")

                col4, col5 = st.columns(2)
                with col4:
                    model_option = st.radio("Choose Model:", ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest", "gemini-1.0-pro"], help="Select the AI model to be used for content generation.")
                with col5:
                    analyze_transcript = st.checkbox("Analyze Transcript", help="Enable or disable transcript analysis with key themes, sentiment, and word frequency.")

                output_language = st.selectbox("Select Output Language:", list(languages.keys()), help="Choose the language for the generated content.")

                # Generate content button
                generate_button = st.button("Generate Content 🖋️")

                if generate_button:
                    with st.spinner(f"Fetching video transcript in {input_language}..."):
                        transcript_data = extract_transcript(video_id, languages[input_language])

                    if transcript_data:
                        # Download SRT
                        srt_data = generate_srt(transcript_data)
                        st.download_button(
                            label="Download SRT 📝",
                            data=srt_data,
                            file_name=f"transcript_{languages[input_language]}.srt",
                            mime="text/plain",
                            key="download_srt"
                        )

                        if analyze_transcript:
                            with st.expander("Transcript Analysis 📊", expanded=True):
                                analysis_prompt = f"Analyze the following transcript for key themes, sentiment, and important timestamps. Transcript: {json.dumps(transcript_data)}"
                                analysis = generate_content(transcript_data, analysis_prompt, "Informative", 1000, model_option)
                                st.write(analysis)

                                # Word frequency analysis
                                words = " ".join([seg["text"] for seg in transcript_data]).lower().split()
                                word_freq = Counter(words)
                                df = pd.DataFrame.from_dict(word_freq, orient='index', columns=['Frequency']).sort_values(by='Frequency', ascending=False)

                                plt.figure(figsize=(10, 6))
                                df.head(20).plot(kind='bar')
                                plt.title("Top 20 Word Frequencies")
                                plt.xlabel("Words")
                                plt.ylabel("Frequency")
                                st.pyplot(plt)

                                st.markdown(get_table_download_link(df), unsafe_allow_html=True)

                        with st.spinner(f"Generating {content_type.lower()} in {output_language}..."):
                            prompts = {
                                "News Article": f"You are a news writer. Generate a concise, factual news article in a journalistic style based on the given YouTube video transcript. Write the article in {output_language}.",
                                "Blog Post": f"You are a blog writer. Create a detailed, engaging blog post covering the key points and insights from the given YouTube video transcript. Write the blog post in {output_language}.",
                                "Social Media Post": f"You are a social media manager. Create a short, engaging post suitable for platforms like Twitter or LinkedIn, highlighting the main takeaway from the YouTube video. Write the post in {output_language}.",
                                "Email Newsletter": f"You are a content marketer. Create an informative and engaging email newsletter summarizing the key points from the YouTube video. Write the newsletter in {output_language}.",
                                "Product Description": f"You are a copywriter. Based on the YouTube video, create a compelling product description that highlights features and benefits. Write in {output_language}.",
                                "Academic Summary": f"You are an academic researcher. Provide a concise, scholarly summary of the key arguments and evidence presented in the YouTube video. Write in {output_language}."
                            }
                            content = generate_content(transcript_data, prompts[content_type], tone, length, model_option)

                            st.subheader(f"Generated {content_type} in {output_language} 📝")
                            st.write(content)

                            # Export options
                            file_formats = ["Text", "PDF", "Word", "Excel"]
                            export_format = st.selectbox("Export Format:", file_formats, index=0)

                            if export_format == "Text":
                                st.download_button(
                                    label=f"Download {content_type} 📥",
                                    data=content,
                                    file_name=f"{content_type.replace(' ', '_').lower()}_{output_language}.txt",
                                    mime="text/plain",
                                    key="download_content_text"
                                )
                            elif export_format == "PDF":
                                # Code to generate PDF file goes here
                                pass
                            elif export_format == "Word":
                                # Code to generate Word file goes here
                                pass
                            elif export_format == "Excel":
                                # Code to generate Excel file goes here
                                pass

                    else:
                        st.warning(f"Please make sure the video has captions available in {input_language}.")
            else:
                st.error("Failed to fetch video metadata. Please try again later.")
        else:
            st.error("Invalid YouTube URL. Please enter a valid video link.")
    else:
        st.info("Paste a YouTube video link to get started.")

    # User feedback form
    st.subheader("Share Your Feedback 💬")
    with st.form("feedback_form"):
        name = st.text_input("Name:")
        email = st.text_input("Email:")
        feedback = st.text_area("Your feedback or suggestions:")

        submit_button = st.form_submit_button("Submit")
        if submit_button:
            # Code to handle feedback submission goes here
            st.success("Thank you for your feedback!")

if __name__ == "__main__":
    main()

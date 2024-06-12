import streamlit as st
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

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def main():
    st.set_page_config(page_title="Advanced Global Content Studio", page_icon="🌐", layout="wide")

    st.title("🌐 YouTube to Global Multimedia Studio")
    st.markdown("Transform YouTube videos into rich, multilingual content with advanced analytics! 🚀🌍")

    with st.expander("Enter YouTube Video Link:"):
        youtube_link = st.text_input("", placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    if youtube_link:
        with st.spinner("Fetching video metadata..."):
            video_id = extract_video_id(youtube_link)
            metadata = get_video_metadata(video_id)
            if metadata:
                st.header(metadata["title"])
                st.image(metadata["thumbnails"]["high"]["url"], use_column_width=True)
                st.write(f"**Channel:** {metadata['channelTitle']} | **Published:** {metadata['publishedAt'][:10]}")
                st.write(metadata["description"])

        with st.expander("Customize Content:"):
            content_type = st.selectbox("Select Content Type:", ["News Article", "Blog Post", "Social Media Post", "Email Newsletter", "Product Description", "Academic Summary"])
            tone = st.selectbox("Select Tone:", ["Informative", "Casual", "Professional", "Humorous", "Inspirational", "Empathetic", "Persuasive"])
            languages = {
                "English": "en", "Spanish": "es", "French": "fr", "German": "de", "Italian": "it",
                "Japanese": "ja", "Korean": "ko", "Portuguese": "pt", "Russian": "ru",
                "Chinese (Simplified)": "zh-Hans", "Chinese (Traditional)": "zh-Hant",
                "Arabic": "ar", "Hindi": "hi", "Bengali": "bn", "Urdu": "ur", "Turkish": "tr",
                "Dutch": "nl", "Polish": "pl", "Swedish": "sv", "Thai": "th", "Vietnamese": "vi",
                "Greek": "el", "Hebrew": "he", "Indonesian": "id", "Malay": "ms", "Filipino": "fil"
            }
            input_language = st.selectbox("Select Transcript Language:", list(languages.keys()))
            output_language = st.selectbox("Select Output Language:", list(languages.keys()))

            length = st.slider("Content Length:", min_value=100, max_value=5000, value=500, step=100)

            col1, col2 = st.columns(2)
            with col1:
                model_option = st.radio("Choose Model:", ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest", "gemini-1.0-pro"])
            with col2:
                analyze_transcript = st.checkbox("Analyze Transcript")

        if st.button("Generate Content 🖋️"):
            with st.spinner(f"Fetching video transcript in {input_language}..."):
                transcript = extract_transcript(video_id, languages[input_language])

            if transcript:
                # Download SRT
                srt_data = generate_srt(transcript)
                st.download_button(
                    label="Download SRT 📝",
                    data=srt_data,
                    file_name=f"transcript_{languages[input_language]}.srt",
                    mime="text/plain"
                )

                if analyze_transcript:
                    with st.expander("Transcript Analysis 📊"):
                        analysis_prompt = f"Analyze the following transcript for key themes, sentiment, and important timestamps. Transcript: {json.dumps(transcript)}"
                        analysis = generate_content(transcript, analysis_prompt, "Informative", 1000, model_option)
                        st.write(analysis)

                        # Word frequency analysis
                        from collections import Counter

                        words = " ".join([seg["text"] for seg in transcript]).lower().split()
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
                    content = generate_content(transcript, prompts[content_type], tone, length, model_option)

                    st.subheader(f"Generated {content_type} in {output_language} 📝")
                    st.write(content)

                    st.download_button(
                        label=f"Download {content_type}",
                        data=content,
                        file_name=f"{content_type.replace(' ', '_').lower()}_{output_language}.txt",
                        mime="text/plain"
                    )
            else:
                st.warning(f"Please make sure the video has captions available in {input_language}.")

if __name__ == "__main__":
    main()

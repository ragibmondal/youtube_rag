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
from wordcloud import WordCloud
from collections import Counter

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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

def generate_wordcloud(word_freq):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq)
    return wordcloud

def main():
    st.set_page_config(page_title="Advanced Global Content Studio", page_icon="🌐", layout="wide")

    st.title("🌐 YouTube to Global Multimedia Studio")
    st.markdown("Transform YouTube videos into rich, multilingual content with advanced analytics! 🚀🌍")

    youtube_link = st.text_input("Enter YouTube Video Link:", placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    if youtube_link:
        video_id = extract_video_id(youtube_link)
        if video_id:
            metadata = get_video_metadata(video_id)
            if metadata:
                st.sidebar.header("Video Details")
                st.sidebar.image(metadata["thumbnails"]["high"]["url"], use_column_width=True)
                st.sidebar.write(f"**Title:** {metadata['title']}")
                st.sidebar.write(f"**Channel:** {metadata['channelTitle']}")
                st.sidebar.write(f"**Published:** {metadata['publishedAt'][:10]}")
                st.sidebar.write(f"**Description:** {metadata['description']}")

            col1, col2, col3 = st.columns(3)
            with col1:
                content_type = st.selectbox("Select Content Type:", ["News Article", "Blog Post", "Social Media Post", "Email Newsletter", "Product Description", "Academic Summary"])
            with col2:
                tone = st.selectbox("Select Tone:", ["Informative", "Casual", "Professional", "Humorous", "Inspirational", "Empathetic", "Persuasive"])
            with col3:
                languages = {
                    "English": "en", "Spanish": "es", "French": "fr", "German": "de", "Italian": "it",
                    "Japanese": "ja", "Korean": "ko", "Portuguese": "pt", "Russian": "ru",
                    "Chinese (Simplified)": "zh-Hans", "Chinese (Traditional)": "zh-Hant",
                    "Arabic": "ar", "Hindi": "hi", "Bengali": "bn", "Urdu": "ur", "Turkish": "tr",
                    "Dutch": "nl", "Polish": "pl", "Swedish": "sv", "Thai": "th", "Vietnamese": "vi",
                    "Greek": "el", "Hebrew": "he", "Indonesian": "id", "Malay": "ms", "Filipino": "fil"
                }
                input_language = st.selectbox("Select Transcript Language:", list(languages.keys()), help="Choose the language for the transcript.")

            length = st.slider("Content Length:", min_value=100, max_value=5000, value=500, step=100, help="Adjust the length of the generated content.")

            col4, col5 = st.columns(2)
            with col4:
                model_option = st.radio("Choose Model:", ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest", "gemini-1.0-pro"], help="Select the AI model for content generation.")
            with col5:
                analyze_transcript = st.checkbox("Analyze Transcript", help="Check this to perform a detailed analysis of the transcript.")

            output_languages = st.multiselect("Select Output Languages:", list(languages.keys()), help="Choose the languages for the generated content.")

            if st.button("Generate Content 🖋️"):
                with st.spinner(f"Fetching video transcript in {input_language}..."):
                    transcript = extract_transcript(video_id, languages[input_language])

                if transcript:
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

                            wordcloud = generate_wordcloud(word_freq)
                            st.image(wordcloud.to_array(), use_column_width=True)

                    for output_language in output_languages:
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
                                label=f"Download {content_type} 📥",
                                data=content,
                                file_name=f"{content_type.replace(' ', '_').lower()}_{output_language}.txt",
                                mime="text/plain"
                            )
                else:
                    st.warning(f"Please make sure the video has captions available in {input_language}.")
        else:
            st.error("Invalid YouTube URL. Please enter a valid video link.")

    st.sidebar.title("About")
    st.sidebar.info(
        "This advanced global studio uses AI to transform YouTube videos into rich, multilingual content with analytics. "
        "Perfect for international content creators, global marketers, researchers, and anyone looking to deeply understand and reach a diverse audience! 🌐🎓🚀\n\n"
        "Made with ❤️ by Ragib"
    )

    st.sidebar.title("New Features")
    st.sidebar.markdown(
        "- 🚀 Fast `gemini-1.5-flash-latest` model\n"
        "- 📊 Transcript analysis with word frequency and word cloud\n"
        "- 📝 SRT subtitle file download\n"
        "- 🎓 Academic summary generation\n"
        "- 🛍️ Product descriptions from videos\n"
        "- 🌐 Support for Greek, Hebrew, Indonesian & more\n"
        "- 📈 Longer content up to 5000 characters\n"
        "- 🎨 'Persuasive' tone for marketing content"
    )


if __name__ == "__main__":
    main()

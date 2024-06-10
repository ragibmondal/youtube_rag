## Advanced Global Content Studio: Transform YouTube Videos into Multilingual Content 🌎

This Streamlit app empowers you to **transform YouTube videos into rich, multilingual content** with advanced analytics, perfect for global content creators, marketers, researchers, and more. 

**Features:**

* **Multilingual Generation:** Translate video transcripts and generate new content (news articles, blog posts, social media posts, etc.) in over 20 languages.
* **Content Personalization:** Control content tone (informative, casual, professional, etc.), length, and type.
* **Powerful Models:** Leverage Google's latest AI models like `gemini-1.5-pro-latest` and `gemini-1.5-flash-latest` for exceptional results.
* **Transcript Analysis:** Analyze video transcripts for key themes, sentiment, and word frequencies to gain deeper insights.
* **Subtitle Generation:** Download SRT subtitle files of the video transcript in various languages.
* **User-Friendly Interface:** A simple and intuitive interface for seamless content creation.

**Instructions:**

1. **Paste a YouTube video link** into the input field.
2. **Customize content settings:** Select content type, tone, input/output languages, length, and model.
3. **Choose optional features:** Analyze transcript, download subtitles, and visualize word frequencies.
4. **Click "Generate Content"** to create your multilingual content.
5. **Download your assets:**  Save generated content and transcript analysis results.

**Getting Started:**

1. **Clone this repository:** `git clone https://github.com/ragibmondal/youtube_rag`
2. **Install requirements:** `pip install -r requirements.txt`
3. **Set up environment variables:** Create a `.env` file in the root directory and add the following:
   ```
   GOOGLE_API_KEY=your-google-api-key
   YOUTUBE_API_KEY=your-youtube-api-key
   ```
   - Obtain your Google Cloud API key from [https://console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials) and a YouTube Data API key from [https://developers.google.com/youtube/v3/getting-started](https://developers.google.com/youtube/v3/getting-started).
4. **Run the app:** `streamlit run app.py`

**Contributing:**

Contributions are welcome! Feel free to open issues or submit pull requests.

**License:**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Let's make your content go global! 🌎**

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import YoutubeLoader
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import re

load_dotenv(override=True)

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        color: #ffffff;
    }
    
    .subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 0;
        color: #e0e0e0;
    }
    
    /* Input section styling */
    .input-container {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        padding: 2rem;
        border-radius: 12px;
        margin: 2rem 0;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    .url-input {
        margin: 1rem 0;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 25px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
        width: 100%;
        max-width: 300px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.5);
        background: linear-gradient(135deg, #45a049 0%, #3d8b40 100%);
    }
    
    .retry-button {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%) !important;
        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.4) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    .retry-button:hover {
        box-shadow: 0 6px 20px rgba(33, 150, 243, 0.5) !important;
        background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%) !important;
    }
    
    /* Result section styling */
    .result-container {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        border-left: 5px solid #2196F3;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        border: 1px solid rgba(255,255,255,0.1);
        color: #e0e0e0;
    }
    
    .summary-header {
        color: #64b5f6;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
    }
    
    .summary-header::before {
        content: "📝";
        margin-right: 10px;
    }
    
    /* Error styling */
    .error-container {
        background: linear-gradient(135deg, #4a1c1c 0%, #2d1810 100%);
        border: 1px solid #f44336;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #f44336;
        color: #ffcdd2;
        box-shadow: 0 4px 20px rgba(244, 67, 54, 0.2);
    }
    
    .success-container {
        background: linear-gradient(135deg, #1b3a1b 0%, #0f2410 100%);
        border: 1px solid #4CAF50;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #4CAF50;
        color: #c8e6c9;
        box-shadow: 0 4px 20px rgba(76, 175, 80, 0.2);
    }
    
    /* Info styling */
    .info-container {
        background: linear-gradient(135deg, #1e3a5f 0%, #16213e 100%);
        border: 1px solid #2196F3;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #2196F3;
        color: #bbdefb;
        box-shadow: 0 4px 20px rgba(33, 150, 243, 0.2);
    }
    
    /* Loading animation */
    .loading-container {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        border-radius: 12px;
        margin: 2rem 0;
        border: 1px solid rgba(255,255,255,0.1);
        color: #e0e0e0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        
        .subtitle {
            font-size: 1rem;
        }
        
        .input-container, .result-container {
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .stButton>button {
            padding: 10px 20px;
            font-size: 14px;
        }
    }
    
    /* Three dots menu icon */
    .three-dots {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .three-dots:hover {
        transform: scale(1.1);
    }
    
    .dot {
        width: 8px;
        height: 8px;
        background: linear-gradient(135deg, #64b5f6 0%, #2196f3 100%);
        border-radius: 50%;
        margin: 3px 0;
        box-shadow: 0 2px 8px rgba(33, 150, 243, 0.4);
        animation: pulse 2s infinite;
    }
    
    .dot:nth-child(1) { animation-delay: 0s; }
    .dot:nth-child(2) { animation-delay: 0.3s; }
    .dot:nth-child(3) { animation-delay: 0.6s; }
    
    @keyframes pulse {
        0%, 100% { 
            opacity: 1; 
            transform: scale(1);
        }
        50% { 
            opacity: 0.7; 
            transform: scale(1.2);
        }
    }
    
    .header-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    
    /* Enhanced animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.8);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes glow {
        0%, 100% {
            box-shadow: 0 0 20px rgba(33, 150, 243, 0.3);
        }
        50% {
            box-shadow: 0 0 30px rgba(33, 150, 243, 0.6), 0 0 40px rgba(33, 150, 243, 0.4);
        }
    }
    
    @keyframes typing {
        from { width: 0; }
        to { width: 100%; }
    }
    
    @keyframes blink {
        50% { border-color: transparent; }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Apply animations to elements */
    .main-header {
        animation: fadeInUp 1s ease-out;
    }
    
    .info-container {
        animation: slideInLeft 0.8s ease-out 0.3s both;
    }
    
    .input-container {
        animation: slideInRight 0.8s ease-out 0.5s both;
    }
    
    .result-container {
        animation: scaleIn 0.6s ease-out;
    }
    
    .success-container, .error-container {
        animation: scaleIn 0.5s ease-out;
    }
    
    .loading-container {
        animation: fadeInUp 0.4s ease-out;
    }
    
    /* Animated title with typing effect */
    .typing-title {
        overflow: hidden;
        border-right: 3px solid #64b5f6;
        white-space: nowrap;
        animation: typing 3s steps(30, end), blink 0.75s step-end infinite;
        width: 0;
        animation-fill-mode: forwards;
    }
    
    /* Floating animation for dots */
    .three-dots {
        animation: float 3s ease-in-out infinite;
    }
    
    /* Enhanced button animations */
    .stButton>button {
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton>button:hover::before {
        left: 100%;
    }
    
    .stButton>button:active {
        transform: scale(0.98);
    }
    
    /* Enhanced dot animations */
    .dot {
        transition: all 0.3s ease;
    }
    
    .dot:hover {
        transform: scale(1.5);
        box-shadow: 0 4px 12px rgba(33, 150, 243, 0.6);
    }
    
    /* Loading spinner animation */
    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid rgba(33, 150, 243, 0.3);
        border-left: 4px solid #2196F3;
        border-radius: 50%;
        animation: rotate 1s linear infinite;
        margin: 0 auto;
    }
    
    /* Progress bar animation */
    .progress-bar {
        width: 100%;
        height: 4px;
        background: rgba(255,255,255,0.1);
        border-radius: 2px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #4CAF50, #45a049);
        border-radius: 2px;
        animation: progress 2s ease-in-out infinite;
    }
    
    @keyframes progress {
        0% { width: 0%; }
        50% { width: 70%; }
        100% { width: 100%; }
    }
    
    /* Success checkmark animation */
    .checkmark {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: #4CAF50;
        position: relative;
        margin: 0 auto;
        animation: scaleIn 0.5s ease-out;
    }
    
    .checkmark::after {
        content: '✓';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-size: 24px;
        font-weight: bold;
        animation: fadeInUp 0.5s ease-out 0.3s both;
    }
    
    /* Dark theme for Streamlit components */
    .stTextInput>div>div>input {
        background-color: #2d3748 !important;
        color: #e0e0e0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #2196F3 !important;
        box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2) !important;
    }
    
    .stTextInput label {
        color: #e0e0e0 !important;
    }
    
    /* Main background */
    .main {
        background: linear-gradient(135deg, #0f1419 0%, #1a202c 100%);
        color: #e0e0e0;
    }
    
    /* Sidebar styling if used */
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
    }
</style>
""", unsafe_allow_html=True)

def get_video_transcript(youtube_url):
    """Extract video ID and get transcript in any available language"""
    # Extract video ID from URL
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', youtube_url)
    if not video_id_match:
        raise ValueError("Invalid YouTube URL")

    video_id = video_id_match.group(1)

    try:
        # First try English
        loader = YoutubeLoader.from_youtube_url(youtube_url, language="en")
        data = loader.load()
        return data[0].page_content
    except Exception as e:
        # If English fails, get available languages and try the first one
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript_list = ytt_api.list(video_id)
            available_languages = [transcript.language_code for transcript in transcript_list]

            if available_languages:
                # Try the first available language
                loader = YoutubeLoader.from_youtube_url(youtube_url, language=available_languages[0])
                data = loader.load()
                return data[0].page_content
            else:
                raise ValueError("No transcripts available for this video")
        except Exception as inner_e:
            raise ValueError(f"Could not retrieve transcript: {str(inner_e)}")

# Main header
st.markdown("""
<div class="main-header">
    <div class="header-content">
        <div class="logo-section">
            <h1 class="main-title typing-title">🎬 YouTube Video Summarizer</h1>
        </div>
        <p class="subtitle">Transform any YouTube video into an AI-powered summary in seconds</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Info section
st.markdown("""
<div class="info-container">
    <h4>🚀 How it works:</h4>
    <ul>
        <li>📺 Paste any YouTube URL</li>
        <li>🎯 AI extracts and analyzes the transcript</li>
        <li>✨ Generates a concise, meaningful summary</li>
        <li>🌍 Supports videos in any language</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Input section
st.markdown('<div class="input-container">', unsafe_allow_html=True)
st.markdown("""
<div class="section-dots">
    <span class="section-dot"></span>
    <span class="section-dot"></span>
    <span class="section-dot active"></span>
</div>
""", unsafe_allow_html=True)
st.markdown("### 🔗 Enter YouTube URL")

youtube_url = st.text_input(
    "YouTube URL",
    placeholder="https://www.youtube.com/watch?v=...",
    label_visibility="collapsed",
    key="youtube_url"
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    summarize_button = st.button("🚀 Summarize Video", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state for storing the last successful transcript
if 'last_transcript' not in st.session_state:
    st.session_state.last_transcript = None
if 'quota_error' not in st.session_state:
    st.session_state.quota_error = False

if summarize_button:
    if not youtube_url:
        st.markdown("""
        <div class="error-container">
            <h4>⚠️ Please enter a YouTube URL</h4>
            <p>Make sure to paste a valid YouTube video link.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="loading-container">
            <div class="spinner"></div>
            <h3>🔄 Processing your video...</h3>
            <p>Extracting transcript and generating AI summary...</p>
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            transcript = get_video_transcript(youtube_url)
            st.session_state.last_transcript = transcript
            st.session_state.quota_error = False

            prompt = ChatPromptTemplate.from_messages([("system", "You are a helpful AI assistant specialized in summarizing YouTube video transcripts. Provide a easy-to-understand summary of the following transcript:"), ("human", "{transcript}")])

            chain = prompt | llm
            summary = chain.invoke({"transcript": transcript})
            
            # Clear loading and show success
            st.empty()
            st.markdown("""
            <div class="success-container">
                <div class="checkmark"></div>
                <h4>✅ Summary Generated Successfully!</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="summary-header">📝 Video Summary</h3>', unsafe_allow_html=True)
            st.write(summary.content)
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
                error_message = str(e)
                if "RESOURCE_EXHAUSTED" in error_message or "429" in error_message:
                    st.session_state.quota_error = True
                    st.error("🚫 **API Quota Exceeded!**\n\nYou've reached the free tier limit for Google Gemini API. Here are your options:\n\n• **Wait and retry**: Free quota resets periodically (try again in a few minutes)\n• **Upgrade your plan**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to upgrade\n• **Use a different API key**: If you have multiple keys, try switching\n\nThe transcript was successfully loaded, so you can try again once your quota resets!")
                else:
                    st.error(f"Error: {error_message}")

if st.session_state.quota_error and st.session_state.last_transcript:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Retry Summary (using cached transcript)", use_container_width=True, key="retry_button"):
            st.markdown("""
            <div class="loading-container">
                <div class="spinner"></div>
                <h3>🔄 Generating summary...</h3>
                <p>Creating AI summary from cached transcript...</p>
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                prompt = ChatPromptTemplate.from_messages([("system", "You are a helpful AI assistant specialized in summarizing YouTube video transcripts. Provide a easy-to-understand summary of the following transcript:"), ("human", "{transcript}")])

                chain = prompt | llm
                summary = chain.invoke({"transcript": st.session_state.last_transcript})
                
                st.empty()
                st.markdown("""
                <div class="success-container">
                    <div class="checkmark"></div>
                    <h4>✅ Summary Generated Successfully!</h4>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="result-container">', unsafe_allow_html=True)
                st.markdown('<h3 class="summary-header">📝 Video Summary</h3>', unsafe_allow_html=True)
                st.write(summary.content)
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.session_state.quota_error = False
                
            except Exception as e:
                error_message = str(e)
                if "RESOURCE_EXHAUSTED" in error_message or "429" in error_message:
                    st.error("🚫 **Still quota exceeded!** Please wait a few minutes and try again, or upgrade your API plan.")
                else:
                    st.error(f"Error: {error_message}")
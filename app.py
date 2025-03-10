import streamlit as st
import traceback
import time

# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="Tensorians GIF Maker",
    page_icon="😈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import requests
from urllib.parse import quote
from ai_utils import process_tweet_and_rank_gifs

# Custom CSS
st.markdown("""
<style>
    /* Modern Dark Theme */
    :root {
        --primary-color: #0100FF;
        --primary-light: #3D3DFF;
        --primary-dark: #0000CC;
        --dark-bg: #121212;
        --card-bg: #1E1E1E;
        --text-primary: #FFFFFF;
        --text-secondary: #CCCCCC;
        --accent-color: #0100FF;
    }
    
    /* Global Styles */
    .main {
        padding: 0;
        background-color: var(--dark-bg);
        color: var(--text-primary);
    }
    
    .stApp {
        background-color: var(--dark-bg);
    }
    
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: var(--text-primary);
    }
    
    /* Header Styling */
    .header {
        background-color: var(--card-bg);
        padding: 1.5rem;
        border-radius: 0 0 10px 10px;
        margin-bottom: 2rem;
        border-top: 4px solid var(--primary-color);
    }
    
    .header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        color: var(--text-primary);
    }
    
    .header p {
        color: var(--text-secondary);
        margin-top: 0.5rem;
        font-size: 1.1rem;
    }
    
    /* Input Area */
    .input-container {
        background-color: var(--card-bg);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .stTextArea textarea {
        background-color: #2A2A2A !important;
        color: var(--text-primary) !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
        min-height: 150px !important;
        font-size: 1.1rem !important;
        line-height: 1.5 !important;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 1px var(--primary-color) !important;
    }
    
    /* Button Styling */
    .stButton button {
        background-color: var(--primary-color) !important;
        color: var(--text-primary) !important;
        border: none !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stButton button:hover {
        background-color: var(--primary-light) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(1, 0, 255, 0.3) !important;
    }
    
    /* GIF Card Styling */
    .gif-card {
        background-color: var(--card-bg);
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        cursor: pointer;
        border: 1px solid #333;
        margin-bottom: 1.5rem;
    }
    
    .gif-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(1, 0, 255, 0.25);
        border-color: var(--primary-color);
    }
    
    .gif-preview-container {
        width: 100%;
        height: 600px;
        overflow: hidden;
        position: relative;
        background-color: #000;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .gif-preview {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
    }
    
    .gif-info {
        padding: 1rem;
        display: flex;
        flex-direction: column;
        flex-grow: 1;
    }
    
    .gif-card h3 {
        font-size: 1.1rem;
        margin: 0 0 0.5rem 0;
        color: var(--text-primary);
        font-weight: 600;
    }
    
    .nft-count {
        display: inline-block;
        background-color: rgba(1, 0, 255, 0.15);
        color: var(--primary-light);
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-bottom: 0.8rem;
        font-weight: 500;
    }
    
    .tags-container {
        margin: 0.8rem 0;
        max-height: 70px;
        overflow-y: auto;
        scrollbar-width: thin;
        scrollbar-color: var(--primary-color) #333;
        margin-bottom: auto;
    }
    
    .tags-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .tags-container::-webkit-scrollbar-track {
        background: #333;
        border-radius: 10px;
    }
    
    .tags-container::-webkit-scrollbar-thumb {
        background-color: var(--primary-color);
        border-radius: 10px;
    }
    
    .tag {
        display: inline-block;
        background-color: #2A2A2A;
        color: var(--text-secondary);
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }
    
    .view-button {
        display: block;
        background-color: var(--primary-color);
        color: var(--text-primary);
        padding: 0.8rem 1rem;
        border-radius: 6px;
        text-decoration: none;
        text-align: center;
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 0.8rem;
        width: 100%;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
        height: auto;
        min-height: 3rem;
        white-space: normal;
        line-height: 1.2;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .view-button:hover {
        background-color: var(--primary-light);
        box-shadow: 0 4px 12px rgba(1, 0, 255, 0.3);
        transform: translateY(-2px);
    }
    
    /* Keywords and Timing Info */
    .keywords {
        background-color: var(--card-bg);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 4px solid var(--primary-color);
    }
    
    .keyword-tag {
        display: inline-block;
        background-color: rgba(1, 0, 255, 0.15);
        color: var(--primary-light);
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        margin-right: 0.6rem;
        margin-bottom: 0.4rem;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .timing-info {
        font-family: 'Courier New', monospace;
        background-color: var(--card-bg);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        font-size: 0.9rem;
    }
    
    /* Instructions Box */
    .instructions-box {
        background-color: var(--card-bg);
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 4px solid var(--primary-color);
    }
    
    .instructions-box h3 {
        color: var(--text-primary);
        margin-top: 0;
        margin-bottom: 1rem;
        font-size: 1.2rem;
    }
    
    .instructions-box p {
        color: var(--text-secondary);
        margin-bottom: 1rem;
        line-height: 1.5;
    }
    
    .instructions-box ol {
        color: var(--text-secondary);
        padding-left: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .instructions-box li {
        margin-bottom: 0.5rem;
        line-height: 1.5;
    }
    
    .instructions-box .tip {
        background-color: rgba(1, 0, 255, 0.15);
        padding: 0.8rem;
        border-radius: 6px;
        color: var(--primary-light);
        font-size: 0.9rem;
        margin-top: 1rem;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        color: var(--text-primary);
        border-bottom: 2px solid var(--primary-color);
        padding-bottom: 0.5rem;
        display: inline-block;
    }
    
    /* Processing container */
    .processing-container {
        background-color: var(--card-bg);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0 1.5rem 0;
        border-left: 4px solid var(--primary-color);
    }
    
    .processing-container pre {
        color: var(--text-primary) !important;
        margin: 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        white-space: pre-wrap;
    }
    
    /* Console output styling */
    .stMarkdown div[data-testid="stMarkdownContainer"] pre {
        color: var(--text-primary) !important;
        background-color: var(--card-bg) !important;
    }
    
    /* iframe container */
    .iframe-container {
        width: 100%;
        height: 80vh;
        border: none;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .header h1 {
            font-size: 1.8rem;
        }
        
        .gif-preview-container {
            height: 400px;
        }
        
        .section-header {
            font-size: 1.3rem;
        }
        
        .stButton button {
            padding: 0.8rem 1rem !important;
            font-size: 1rem !important;
        }
        
        .processing-container {
            padding: 0.8rem 1rem;
        }
        
        .processing-container pre {
            color: var(--text-primary) !important;
        }
    }
    
    @media (max-width: 576px) {
        .header {
            padding: 1rem;
        }
        
        .input-container {
            padding: 1rem;
        }
        
        .gif-preview-container {
            height: 300px;
        }
        
        .gif-info {
            padding: 0.8rem;
        }
        
        .view-button {
            padding: 0.7rem 0.5rem;
            font-size: 0.8rem;
        }
        
        .processing-container pre {
            font-size: 0.8rem;
        }
    }
    
    /* Fix for Streamlit components */
    .block-container {
        padding-top: 0 !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    
    .main .block-container {
        padding-bottom: 1rem !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
BASE_URL = "https://3look.io/api/creative-studio/templates"
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin"
}

def display_ranked_gifs(ranked_gifs, all_gifs_dict, keywords, timing_info):
    """Display the ranked GIFs in a grid."""
    # Navigation buttons - only in main results view
    if st.button("↺ New Search", key=f"new_search_results_view_{id(ranked_gifs)}", use_container_width=True):
        st.session_state.ranked_gifs = None
        st.session_state.all_gifs_dict = None
        st.session_state.keywords = None
        st.session_state.timing_info = None
        st.session_state.current_tweet = ""
        st.rerun()
    
    # Display extracted keywords
    st.markdown("<div class='keywords'><strong>Keywords:</strong> " + 
                " ".join([f"<span class='keyword-tag'>{keyword}</span>" for keyword in keywords]) + 
                "</div>", unsafe_allow_html=True)
    
    # Display timing information
    st.markdown(f"<div class='timing-info'>{timing_info}</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='section-header'>CUSTOM GIF TEMPLATES</div>", unsafe_allow_html=True)
    
    # Create three columns for desktop, two for tablet, one for mobile
    cols = st.columns(3)
    
    # Display GIFs in the grid
    for i, ranked_gif in enumerate(ranked_gifs):
        gif_id = ranked_gif["id"]
        gif = all_gifs_dict.get(gif_id)
        if not gif:
            continue
            
        col_idx = i % 3
        with cols[col_idx]:
            # Get NFT count from the correct field
            nft_count = gif.get("amountOfNfts", 0)
            
            # Get tags
            tags = gif.get("tags", [])
            tags_html = ""
            if tags:
                tags_html = "<div class='tags-container'>" + "".join([f"<span class='tag'>{tag}</span>" for tag in tags[:10]]) + "</div>"
            
            # Get the GIF name and create a button label
            gif_name = gif.get('name', 'GIF')
            button_label = gif_name
            
            # Display the GIF card
            st.markdown(f"""
            <div class="gif-card">
                <div class="gif-preview-container">
                    <img src="{gif['previewUrl']}" alt="{gif['name']}" class="gif-preview">
                </div>
                <div class="gif-info">
                    <h3>{gif['name']}</h3>
                    <div class="nft-count">{nft_count} NFTs</div>
                    {tags_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Create a truly unique key for each button by combining multiple identifiers
            # Use both the index, gif_id and the object id of ranked_gifs to ensure uniqueness
            unique_key = f"gif_button_{i}_{gif_id}_{id(ranked_gifs)}"
            if st.button(button_label, key=unique_key, use_container_width=True):
                st.session_state.show_details_for = gif_id
                st.session_state.show_details_slug = gif['slug']
                st.session_state.previous_tweet = st.session_state.get('current_tweet', '')
                st.rerun()

def show_gif_details(gif_slug):
    """Show GIF details in an iframe."""
    # Back button at the top with unique key
    if st.button("← Back to Results", key="back_to_results_top_button", use_container_width=True):
        st.session_state.show_details_for = None
        st.session_state.show_details_slug = None
        st.rerun()
    
    st.markdown("<div class='section-header'>GIF MAKER</div>", unsafe_allow_html=True)
    
    # Add instructions about adding Tensorian faces
    st.markdown("""
    <div class="instructions-box">
        <h3>Customize the GIF</h3>
        <ol>
            <li>Add Tensorian faces to characters</li>
            <li>Adjust position and size for perfect fit</li>
            <li>Save your creation and share</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Display the iframe with the GIF details
    st.markdown(f"""
    <iframe src="https://3look.io/page/tensorians/{quote(gif_slug)}" class="iframe-container"></iframe>
    """, unsafe_allow_html=True)
    
    # Back button at the bottom with unique key
    if st.button("← Back to Results", key="back_to_results_bottom_button", use_container_width=True):
        st.session_state.show_details_for = None
        st.session_state.show_details_slug = None
        st.rerun()

def main():
    # Initialize session state for showing details
    if 'show_details_for' not in st.session_state:
        st.session_state.show_details_for = None
    if 'show_details_slug' not in st.session_state:
        st.session_state.show_details_slug = None
    if 'current_tweet' not in st.session_state:
        st.session_state.current_tweet = ""
    
    # App header with demon emoji
    st.markdown("""
    <div class="header">
        <h1>Tensorians GIF Maker 😈</h1>
        <p>Enter a tweet or topic to find the perfect GIF.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # If we're showing details for a specific GIF, display that instead of the main UI
    if st.session_state.show_details_for and st.session_state.show_details_slug:
        show_gif_details(st.session_state.show_details_slug)
        return
    
    # Input container
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    # Tweet input with increased height and previous value
    tweet = st.text_area("Enter a tweet you want to reply to, or any topic you want a GIF for:", 
                        value=st.session_state.get('current_tweet', ''),
                        height=200)
    
    # Process button with unique key
    analyze_clicked = st.button("Analyze & Find GIFs", key="analyze_button_main", use_container_width=True)
    
    # Create a placeholder for the process display inside the input container
    process_display = st.empty()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle analyze button click
    if analyze_clicked:
        if tweet:
            try:
                # Store current tweet
                st.session_state.current_tweet = tweet
                
                # Clear any previous results
                st.session_state.ranked_gifs = None
                st.session_state.all_gifs_dict = None
                st.session_state.keywords = None
                st.session_state.timing_info = None
                
                # Start timing
                start_time = time.time()
                
                # Display processing steps
                process_display.markdown("""
                <div class="processing-container">
                <pre>
                Processing tweet...
                </pre>
                </div>
                """, unsafe_allow_html=True)
                
                # Process tweet and get ranked GIFs
                ranked_gifs, all_gifs_dict, keywords, timing_info = process_tweet_and_rank_gifs(
                    tweet_text=tweet,
                    api_url=BASE_URL,
                    headers=HEADERS,
                    process_display=process_display
                )
                
                # Add total time
                total_time = time.time() - start_time
                timing_info += f"Total processing time: {total_time:.2f}s\n"
                
                # Store results in session state
                st.session_state.ranked_gifs = ranked_gifs
                st.session_state.all_gifs_dict = all_gifs_dict
                st.session_state.keywords = keywords
                st.session_state.timing_info = timing_info
                
                # Clear the process display
                process_display.empty()
                
                # Display results
                display_ranked_gifs(ranked_gifs, all_gifs_dict, keywords, timing_info)
                
                # Rerun to display results
                st.rerun()
            except Exception as e:
                error_message = "An error occurred while processing your request. Please try again.\n\n"
                error_message += traceback.format_exc()
                st.error(error_message)
        else:
            st.warning("Please enter a tweet or topic to analyze.")
    
    # If we have results in session state, display them
    if hasattr(st.session_state, 'ranked_gifs') and st.session_state.ranked_gifs is not None:
        display_ranked_gifs(
            st.session_state.ranked_gifs, 
            st.session_state.all_gifs_dict,
            st.session_state.keywords,
            st.session_state.timing_info
        )

if __name__ == "__main__":
    main() 
import streamlit as st
import traceback
import time

# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="Tensorians GIF Maker",
    page_icon="🎬",
    layout="wide"
)

import requests
from urllib.parse import quote
from ai_utils import process_tweet_and_rank_gifs

# Custom CSS
st.markdown("""
<style>
    :root {
        --primary-color: #0100FF;
        --primary-light: #3D3DFF;
        --primary-dark: #0000CC;
        --primary-bg: #F0F0FF;
        --text-on-primary: #FFFFFF;
        --text-light: #F0F0FF;
    }
    
    .main {
        padding: 2rem;
        background-color: var(--primary-bg);
    }
    
    h1, h2, h3 {
        color: var(--primary-color);
        margin-bottom: 1rem;
    }
    
    .stButton button {
        background-color: var(--primary-color) !important;
        color: var(--text-on-primary) !important;
        border: none !important;
    }
    
    .stButton button:hover {
        background-color: var(--primary-dark) !important;
    }
    
    .gif-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
        height: 100%;
        display: flex;
        flex-direction: column;
        cursor: pointer;
    }
    
    .gif-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        border-color: var(--primary-color);
    }
    
    .gif-preview-container {
        width: 100%;
        height: 400px;
        overflow: hidden;
        border-radius: 4px;
        margin-bottom: 0.5rem;
        position: relative;
        background-color: white;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .gif-preview {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
        border-radius: 4px;
    }
    
    .gif-card h3 {
        font-size: 1rem;
        margin: 0.5rem 0;
        color: var(--primary-color);
    }
    
    .nft-count {
        display: inline-block;
        background-color: var(--primary-bg);
        color: var(--primary-color);
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
    }
    
    .tags-container {
        margin: 0.5rem 0;
        max-height: 60px;
        overflow-y: auto;
    }
    
    .tag {
        display: inline-block;
        background-color: var(--primary-bg);
        color: var(--primary-dark);
        padding: 0.1rem 0.4rem;
        border-radius: 3px;
        font-size: 0.7rem;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
    }
    
    .view-button {
        display: inline-block;
        background-color: var(--primary-color);
        color: var(--text-on-primary);
        padding: 0.7rem 1rem;
        border-radius: 4px;
        text-decoration: none;
        text-align: center;
        font-size: 1rem;
        font-weight: 600;
        margin-top: auto;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .view-button:hover {
        background-color: var(--primary-dark);
    }
    
    .keywords {
        background-color: var(--primary-bg);
        padding: 0.5rem 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
        border-left: 3px solid var(--primary-color);
    }
    
    .keyword-tag {
        display: inline-block;
        background-color: var(--primary-color);
        color: var(--text-on-primary);
        padding: 0.3rem 0.6rem;
        border-radius: 20px;
        margin-right: 0.5rem;
        font-size: 0.9rem;
        border: 1px solid var(--primary-light);
    }
    
    .iframe-container {
        width: 100%;
        height: 80vh;
        border: none;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .timing-info {
        font-family: monospace;
        background-color: var(--primary-bg);
        padding: 0.5rem;
        border-radius: 4px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: var(--primary-dark);
        border-left: 3px solid var(--primary-color);
    }
    
    /* Hide the streamlit button label */
    .gif-button-container {
        display: none !important;
    }
    
    /* Style the text area */
    .stTextArea textarea {
        border-color: var(--primary-color) !important;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--primary-dark) !important;
        box-shadow: 0 0 0 1px var(--primary-light) !important;
    }
    
    /* Style the app background */
    .stApp {
        background-color: var(--primary-bg);
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
    # Display timing information
    st.markdown(f"<div class='timing-info'>{timing_info}</div>", unsafe_allow_html=True)
    
    # Display extracted keywords
    st.markdown("<div class='keywords'><strong>Keywords:</strong> " + 
                " ".join([f"<span class='keyword-tag'>{keyword}</span>" for keyword in keywords]) + 
                "</div>", unsafe_allow_html=True)
    
    st.markdown("### Top GIF Matches")
    
    # Create three columns
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
            
            # Create a clickable card that opens the details
            gif_url = f"https://3look.io/page/tensorians/{quote(gif['slug'])}"
            
            # Create a container for the button with a class to hide it
            with st.container():
                # Store the GIF ID and slug in session state when clicked
                button = st.button(f"GIF Card {i}", key=f"gif_card_{i}_{gif_id}", help="Click to view details", use_container_width=True)
                st.markdown("<div class='gif-button-container'></div>", unsafe_allow_html=True)
                
                if button:
                    st.session_state.show_details_for = gif_id
                    st.session_state.show_details_slug = gif['slug']
                    st.rerun()
            
            # Display the GIF card
            st.markdown(f"""
            <div class="gif-card" onclick="window.open('{gif_url}', '_blank')">
                <div class="gif-preview-container">
                    <img src="{gif['previewUrl']}" alt="{gif['name']}" class="gif-preview">
                </div>
                <h3>{gif['name']}</h3>
                <div class="nft-count">{nft_count} NFTs</div>
                {tags_html}
                <a href="{gif_url}" class="view-button" target="_blank">USE THIS GIF</a>
            </div>
            """, unsafe_allow_html=True)

def show_gif_details(gif_slug):
    """Show GIF details in an iframe."""
    st.markdown("### GIF Details")
    
    # Add a back button
    if st.button("← Back to Results"):
        # Clear the session state and rerun to go back to results
        st.session_state.show_details_for = None
        st.session_state.show_details_slug = None
        st.rerun()
    
    # Display the iframe with the GIF details
    st.markdown(f"""
    <iframe src="https://3look.io/page/tensorians/{quote(gif_slug)}" class="iframe-container"></iframe>
    """, unsafe_allow_html=True)

def main():
    # Initialize session state for showing details
    if 'show_details_for' not in st.session_state:
        st.session_state.show_details_for = None
    if 'show_details_slug' not in st.session_state:
        st.session_state.show_details_slug = None
    
    # Create a placeholder for the process display
    process_display = st.empty()
    
    # App title with demon emoji at the end
    st.title("Tensorians GIF Maker 👿")
    st.markdown("Enter a tweet and get AI-powered GIF suggestions.")
    
    # If we're showing details for a specific GIF, display that instead of the main UI
    if st.session_state.show_details_for and st.session_state.show_details_slug:
        show_gif_details(st.session_state.show_details_slug)
        return
    
    # Tweet input
    tweet = st.text_area("Enter a tweet:", height=100)
    
    # Process button
    if st.button("Analyze & Find GIFs"):
        if tweet:
            try:
                # Clear any previous results
                st.session_state.ranked_gifs = None
                st.session_state.all_gifs_dict = None
                st.session_state.keywords = None
                st.session_state.timing_info = None
                
                # Start timing
                start_time = time.time()
                
                # Display processing steps
                process_display.markdown("""
                ```
                Processing tweet...
                ```
                """.format(tweet)
                )
                
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
                
            except Exception as e:
                # Capture and display the full traceback
                error_message = f"An error occurred: {str(e)}\n"
                error_message += traceback.format_exc()
                st.error(error_message)
        else:
            st.warning("Please enter a tweet to analyze.")
    
    # If we have results in session state, display them
    elif hasattr(st.session_state, 'ranked_gifs') and st.session_state.ranked_gifs is not None:
        display_ranked_gifs(
            st.session_state.ranked_gifs, 
            st.session_state.all_gifs_dict,
            st.session_state.keywords,
            st.session_state.timing_info
        )

if __name__ == "__main__":
    main() 
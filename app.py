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
    .main {
        padding: 2rem;
    }
    h1 {
        color: #1E88E5;
        margin-bottom: 1rem;
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
    }
    .gif-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .gif-preview {
        width: 100%;
        border-radius: 4px;
        margin-bottom: 0.5rem;
    }
    .gif-card h3 {
        font-size: 1rem;
        margin: 0.5rem 0;
        color: #333;
    }
    .nft-count {
        display: inline-block;
        background-color: #f0f7ff;
        color: #1565C0;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
    }
    .explanation {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 0.5rem;
        flex-grow: 1;
    }
    .view-button {
        display: inline-block;
        background-color: #1E88E5;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        text-decoration: none;
        text-align: center;
        font-size: 0.9rem;
        margin-top: auto;
    }
    .view-button:hover {
        background-color: #1565C0;
    }
    .keywords {
        background-color: #f0f7ff;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
        border-left: 3px solid #1E88E5;
    }
    .keyword-tag {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1565C0;
        padding: 0.3rem 0.6rem;
        border-radius: 20px;
        margin-right: 0.5rem;
        font-size: 0.9rem;
        border: 1px solid #bbdefb;
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
        background-color: #f5f5f5;
        padding: 0.5rem;
        border-radius: 4px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #333;
        border-left: 3px solid #666;
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
    st.markdown("<div class='keywords'><strong>🔍 Keywords:</strong> " + 
                " ".join([f"<span class='keyword-tag'>{keyword}</span>" for keyword in keywords]) + 
                "</div>", unsafe_allow_html=True)
    
    st.markdown("### 🎯 Top GIF Matches")
    
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
            # Create a unique key for each button using both index and GIF ID
            button_key = f"btn_{i}_{gif_id}"
            
            # Get NFT count from the correct field
            nft_count = gif.get("amountOfNfts", 0)
            
            st.markdown(f"""
            <div class="gif-card">
                <img src="{gif['previewUrl']}" alt="{gif['name']}" class="gif-preview">
                <h3>{gif['name']}</h3>
                <div class="nft-count">🔢 {nft_count} NFTs</div>
                <a href="https://3look.io/page/tensorians/{quote(gif['slug'])}" class="view-button" target="_blank">Use This GIF</a>
            </div>
            """, unsafe_allow_html=True)
            
            # Add a button to show details in an iframe
            if st.button("Show Details", key=button_key):
                # Store the GIF ID in session state to show its details
                st.session_state.show_details_for = gif_id
                st.session_state.show_details_slug = gif['slug']
                st.rerun()

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
    
    # App title
    st.title("🎬 Tensorians GIF Maker")
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
                ᐅ Processing tweet...
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
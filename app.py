import streamlit as st
import requests
import json
from PIL import Image
import io
import base64
from urllib.parse import quote

# Set page config
st.set_page_config(
    page_title="3look.io GIF Carousel",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .gif-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 20px;
    }
    .gif-card {
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        padding: 15px;
        text-align: center;
        transition: transform 0.3s;
        width: 250px;
        margin-bottom: 20px;
    }
    .gif-card:hover {
        transform: translateY(-5px);
    }
    .gif-preview {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 6px;
        margin-bottom: 10px;
    }
    .nft-count {
        font-size: 14px;
        color: #7f8c8d;
        margin-bottom: 10px;
    }
    .view-button {
        display: inline-block;
        padding: 8px 16px;
        background-color: #3498db;
        color: white;
        text-decoration: none;
        border-radius: 4px;
        font-size: 14px;
        transition: background-color 0.3s;
    }
    .view-button:hover {
        background-color: #2980b9;
    }
    .stButton button {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        cursor: pointer;
    }
    .stButton button:hover {
        background-color: #2980b9;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("3look.io GIF Collection")

# Function to fetch GIFs from the API
@st.cache_data(ttl=3600)  # Cache the data for 1 hour
def fetch_gifs():
    url = "https://3look.io/api/creative-studio/templates"
    
    # Query parameters
    params = {
        "cursor": "",
        "filters": "types:gif",
        "widget": "tensorians",
        "excluded_categories[]": [
            "305e1658-f986-4879-b927-484fa945ed23",
            "738e63e4-d126-4c58-8d08-17d06672dee1"
        ],
        "take": "25",
        "is_trending": "true"
    }
    
    # Headers to simulate a browser request
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching GIFs: {e}")
        return None

# Function to display GIFs in a grid
def display_gifs(gifs_data):
    if not gifs_data or "data" not in gifs_data or not gifs_data["data"]:
        st.warning("No GIFs found.")
        return
    
    gifs = gifs_data["data"]
    
    # Create columns for the grid layout
    cols = st.columns(4)  # 4 columns per row
    
    # Display GIFs in the grid
    for i, gif in enumerate(gifs):
        col_idx = i % 4
        
        with cols[col_idx]:
            # Get the preview URL
            preview_url = gif.get("previewUrl") or gif.get("thumbnailUrl") or gif.get("imageUrl")
            
            # Get the slug for the deeplink
            slug = gif.get("slug", "")
            
            # Create a card for each GIF
            st.markdown(f"""
            <div class="gif-card">
                <img src="{preview_url}" alt="{gif.get('name', 'GIF')}" class="gif-preview">
                <h3>{gif.get('name', 'Unnamed GIF')}</h3>
                <p class="nft-count">NFTs: {gif.get('amountOfNfts', 0)}</p>
                <a href="https://3look.io/page/tensorians/{quote(slug)}" class="view-button" target="_blank">View Details</a>
            </div>
            """, unsafe_allow_html=True)

# Main app logic
def main():
    # Add a loading spinner
    with st.spinner("Loading GIFs..."):
        # Fetch GIFs
        gifs_data = fetch_gifs()
    
    # Display GIFs if data is available
    if gifs_data:
        display_gifs(gifs_data)
    
    # Add a refresh button
    if st.button("Refresh GIFs"):
        # Clear the cache and fetch new data
        fetch_gifs.clear()
        st.experimental_rerun()

if __name__ == "__main__":
    main() 
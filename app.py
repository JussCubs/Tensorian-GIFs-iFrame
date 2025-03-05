import streamlit as st
import requests
import json
from PIL import Image
import io
import base64
from urllib.parse import quote
import time

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

# Sidebar options
st.sidebar.title("Options")
use_proxy = st.sidebar.checkbox("Use Proxy (for CORS issues)", value=True)
retry_count = st.sidebar.slider("Retry Count", min_value=1, max_value=5, value=3)
show_debug = st.sidebar.checkbox("Show Debug Info", value=True)

# Function to fetch GIFs from the API
@st.cache_data(ttl=3600)  # Cache the data for 1 hour
def fetch_gifs(use_proxy=True, retry_count=3):
    # Using the exact URL and format from the original code
    url = "https://3look.io/api/creative-studio/templates?cursor=&filters=types:gif&widget=tensorians&excluded_categories[]=305e1658-f986-4879-b927-484fa945ed23&excluded_categories[]=738e63e4-d126-4c58-8d08-17d06672dee1&take=25&is_trending=true"
    
    # Headers to exactly match the browser request
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "baggage": "sentry-environment=vercel-production,sentry-release=c49724331e56bda8a55935806d32e856db7c6246,sentry-public_key=97e99ce79d81bab29c0f490cbc4b5858,sentry-trace_id=3fb36c2c22df4746a3b58cb77c415805,sentry-sample_rate=1,sentry-sampled=true",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sentry-trace": "3fb36c2c22df4746a3b58cb77c415805-a9a5f4064a00dded-1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Referer": "https://3look.io/page/tensorians?filters=types:gif",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    # If using proxy, use a proxy service to avoid CORS
    if use_proxy:
        # Use a proxy service like AllOrigins
        proxy_url = f"https://api.allorigins.win/get?url={quote(url)}"
        if show_debug:
            st.sidebar.write("Using proxy URL:")
            st.sidebar.code(proxy_url)
    else:
        proxy_url = None
    
    # Try multiple times with increasing delays
    for attempt in range(retry_count):
        try:
            if show_debug:
                st.sidebar.write(f"Attempt {attempt + 1}/{retry_count}")
                st.sidebar.write("Attempting to fetch data from:")
                st.sidebar.code(proxy_url if use_proxy else url)
            
            if use_proxy:
                # Make request through proxy
                response = requests.get(proxy_url, timeout=15)
                
                if response.status_code == 200:
                    # Parse the proxy response
                    proxy_data = response.json()
                    if "contents" in proxy_data:
                        # Parse the contents from the proxy
                        try:
                            data = json.loads(proxy_data["contents"])
                            if show_debug:
                                st.sidebar.write("Successfully parsed proxy response")
                            return data
                        except json.JSONDecodeError:
                            if show_debug:
                                st.sidebar.write("Failed to parse JSON from proxy response")
                    else:
                        if show_debug:
                            st.sidebar.write("Proxy response doesn't contain 'contents'")
            else:
                # Direct request
                response = requests.get(url, headers=headers, timeout=10)
                
                if show_debug:
                    st.sidebar.write(f"Response Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if show_debug and data and "data" in data:
                        st.sidebar.write(f"Found {len(data['data'])} GIFs")
                    
                    return data
                else:
                    if show_debug:
                        st.sidebar.write("Error Response:", response.text[:500])
            
            # If we get here, the request failed
            if show_debug:
                st.sidebar.write(f"Attempt {attempt + 1} failed, retrying...")
            
            # Exponential backoff
            time.sleep(2 ** attempt)
                
        except Exception as e:
            if show_debug:
                st.sidebar.write(f"Error on attempt {attempt + 1}: {str(e)}")
            
            # Exponential backoff
            time.sleep(2 ** attempt)
    
    # If all attempts failed
    if show_debug:
        st.sidebar.write("All attempts failed")
    return None

# Function to display GIFs in a grid
def display_gifs(gifs_data):
    if not gifs_data or "data" not in gifs_data or not gifs_data["data"]:
        st.warning("No GIFs found in the API response.")
        
        # Display the raw response for debugging
        if show_debug:
            with st.expander("View API Response"):
                st.json(gifs_data)
        
        return
    
    gifs = gifs_data["data"]
    st.success(f"Successfully loaded {len(gifs)} GIFs!")
    
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
        # Fetch GIFs with the selected options
        gifs_data = fetch_gifs(use_proxy=use_proxy, retry_count=retry_count)
    
    # Display GIFs if data is available
    if gifs_data:
        display_gifs(gifs_data)
    else:
        st.error("Failed to fetch data from the API. Please check the sidebar for details.")
    
    # Add a refresh button
    if st.button("Refresh GIFs"):
        # Clear the cache and fetch new data
        fetch_gifs.clear()
        st.experimental_rerun()

if __name__ == "__main__":
    main() 

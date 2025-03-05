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
    page_title="3look.io GIF Collection",
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
        width: 100%;
        margin-bottom: 20px;
    }
    .gif-card:hover {
        transform: translateY(-5px);
    }
    .gif-preview {
        width: 100%;
        max-height: 300px;
        object-fit: contain;
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
        margin: 5px;
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
    .tag-cloud {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin: 10px 0;
    }
    .tag {
        background-color: #e0e0e0;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        color: #333;
    }
    .dimensions-info {
        font-size: 12px;
        color: #666;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("3look.io GIF Collection")

# Sidebar options
st.sidebar.title("Options")
use_proxy = st.sidebar.checkbox("Use Proxy (for CORS issues)", value=True)
retry_count = st.sidebar.slider("Retry Count", min_value=1, max_value=5, value=3)
show_debug = st.sidebar.checkbox("Show Debug Info", value=False)

# Function to fetch GIFs from the API
@st.cache_data(ttl=3600)  # Cache the data for 1 hour
def fetch_gifs(use_proxy=True, retry_count=3):
    url = "https://3look.io/api/creative-studio/templates?cursor=&filters=types:gif&widget=tensorians&excluded_categories[]=305e1658-f986-4879-b927-484fa945ed23&excluded_categories[]=738e63e4-d126-4c58-8d08-17d06672dee1&take=25&is_trending=true"
    
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
        "Referer": "https://3look.io/page/tensorians?filters=types:gif",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    if use_proxy:
        proxy_url = f"https://api.allorigins.win/get?url={quote(url)}"
        if show_debug:
            st.sidebar.write("Using proxy URL:", proxy_url)
    else:
        proxy_url = None
    
    for attempt in range(retry_count):
        try:
            if use_proxy:
                response = requests.get(proxy_url, timeout=15)
                if response.status_code == 200:
                    proxy_data = response.json()
                    if "contents" in proxy_data:
                        try:
                            data = json.loads(proxy_data["contents"])
                            if show_debug:
                                st.sidebar.success("Successfully fetched data through proxy")
                            return data
                        except json.JSONDecodeError:
                            if show_debug:
                                st.sidebar.error("Failed to parse JSON from proxy response")
            else:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if show_debug:
                        st.sidebar.success("Successfully fetched data directly")
                    return data
            
            if show_debug:
                st.sidebar.warning(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(2 ** attempt)
                
        except Exception as e:
            if show_debug:
                st.sidebar.error(f"Error on attempt {attempt + 1}: {str(e)}")
            time.sleep(2 ** attempt)
    
    return None

# Function to display GIFs in a grid
def display_gifs(gifs_data):
    if not gifs_data or "templates" not in gifs_data or not gifs_data["templates"]:
        st.warning("No GIFs found in the API response.")
        if show_debug:
            with st.expander("View API Response"):
                st.json(gifs_data)
        return
    
    gifs = gifs_data["templates"]
    
    # Extract all unique tags
    all_tags = set()
    for gif in gifs:
        if "tags" in gif:
            all_tags.update(gif["tags"])
    
    # Filter options
    st.sidebar.title("Filters")
    search_query = st.sidebar.text_input("Search by name or tag").lower()
    selected_tags = st.sidebar.multiselect("Filter by tags", sorted(list(all_tags)))
    sort_option = st.sidebar.selectbox("Sort by", ["Name", "NFT Count", "Dimensions"])
    
    # Filter and sort GIFs
    filtered_gifs = []
    for gif in gifs:
        if search_query and not (
            search_query in gif.get("name", "").lower() or 
            any(search_query in tag.lower() for tag in gif.get("tags", []))
        ):
            continue
            
        if selected_tags and not all(tag in gif.get("tags", []) for tag in selected_tags):
            continue
            
        filtered_gifs.append(gif)
    
    # Sort GIFs
    if sort_option == "Name":
        filtered_gifs.sort(key=lambda x: x.get("name", "").lower())
    elif sort_option == "NFT Count":
        filtered_gifs.sort(key=lambda x: x.get("amountOfNfts", 0), reverse=True)
    elif sort_option == "Dimensions":
        filtered_gifs.sort(key=lambda x: x.get("dimensions", {}).get("width", 0) * x.get("dimensions", {}).get("height", 0), reverse=True)
    
    st.success(f"Showing {len(filtered_gifs)} GIFs")
    
    # Display GIFs in a grid
    cols = st.columns(3)
    
    for i, gif in enumerate(filtered_gifs):
        col_idx = i % 3
        
        with cols[col_idx]:
            preview_url = gif.get("previewUrl", "")
            name = gif.get("name", "Unnamed GIF")
            slug = gif.get("slug", "")
            dimensions = gif.get("dimensions", {})
            tags = gif.get("tags", [])
            
            st.markdown(f"""
            <div class="gif-card">
                <img src="{preview_url}" alt="{name}" class="gif-preview">
                <h3>{name}</h3>
                <p class="dimensions-info">
                    {dimensions.get("width", 0)}x{dimensions.get("height", 0)} px | 
                    {dimensions.get("frames", 0)} frames
                </p>
                <p class="nft-count">NFTs: {gif.get("amountOfNfts", 0)}</p>
                <div class="tag-cloud">
                    {' '.join(f'<span class="tag">{tag}</span>' for tag in tags[:5])}
                </div>
                <a href="https://3look.io/page/tensorians/{quote(slug)}" class="view-button" target="_blank">View Details</a>
                <a href="{preview_url}" class="view-button" target="_blank">Open GIF</a>
            </div>
            """, unsafe_allow_html=True)

# Main app logic
def main():
    with st.spinner("Loading GIFs..."):
        gifs_data = fetch_gifs(use_proxy=use_proxy, retry_count=retry_count)
    
    if gifs_data:
        display_gifs(gifs_data)
    else:
        st.error("Failed to fetch data from the API. Please check the sidebar for details.")
    
    if st.button("Refresh GIFs"):
        fetch_gifs.clear()
        st.experimental_rerun()

if __name__ == "__main__":
    main() 
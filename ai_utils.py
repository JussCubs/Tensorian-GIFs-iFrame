import os
import json
import streamlit as st
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load OpenAI API key from environment variables or Streamlit secrets
def get_openai_api_key():
    """Get OpenAI API key from environment variables or Streamlit secrets."""
    # First try to load from .env file
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    # If found in .env, return it
    if api_key:
        print("Using API key from .env file")
        return api_key
    
    # If not found in .env, try Streamlit secrets
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
        print("Using API key from Streamlit secrets")
        return api_key
    except (KeyError, FileNotFoundError):
        # If not found in either place, show error
        st.error("OpenAI API key not found. Please set it in .env file or Streamlit secrets.")
        st.stop()
        return None

# Initialize OpenAI client
client = OpenAI(api_key=get_openai_api_key())

def extract_keywords(tweet_text: str, trending_tags: list, process_display) -> list:
    """Extract keywords from a tweet using GPT-4o, informed by trending tags."""
    process_display.markdown("""
    ```
    ᐅ Analyzing tweet content...
    ```
    """)
    
    prompt = f"""Analyze this tweet and extract exactly 3 keywords or phrases that best represent its content for searching GIFs:

    Tweet: "{tweet_text}"

    Here are popular tags from trending GIFs that might be relevant:
    {trending_tags[:50]}  # Limit to first 50 tags to avoid token limits

    Return a JSON object with this format:
    {{
        "keywords": ["keyword1", "keyword2", "keyword3"]
    }}

    The keywords should:
    1. Capture the main themes, emotions, or actions in the tweet
    2. Be specific enough to find relevant GIFs
    3. Include both literal and emotional/metaphorical concepts
    4. Preferably include or relate to some of the trending tags when appropriate
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are an expert at analyzing social media content and extracting relevant keywords."},
            {"role": "user", "content": prompt}
        ]
    )
    
    try:
        result = json.loads(response.choices[0].message.content)
        keywords = result.get("keywords", [])
    except (json.JSONDecodeError, AttributeError):
        process_display.markdown("""
        ```
        ᐅ Error parsing response. Please try again.
        ```
        """)
        return []
    
    if not keywords:
        process_display.markdown("""
        ```
        ᐅ No keywords found. Please try again later.
        ```
        """)
        return []
    
    process_display.markdown("""
    ```
    ᐅ Keywords extracted: {}
    
    ᐅ Searching for GIFs...
    ```
    """.format(", ".join(keywords)))
    
    return keywords

def extract_trending_tags(gifs: list) -> list:
    """Extract unique tags from a list of GIFs."""
    all_tags = []
    for gif in gifs:
        tags = gif.get("tags", [])
        all_tags.extend(tags)
    
    # Return unique tags
    return list(set(all_tags))

def search_gifs(keyword: str, base_url: str, headers: dict, process_display) -> list:
    """Search GIFs using a specific keyword."""
    url = f"{base_url}?cursor=&filters=query:'{keyword}',types:gif&widget=tensorians&excluded_categories[]=305e1658-f986-4879-b927-484fa945ed23&excluded_categories[]=738e63e4-d126-4c58-8d08-17d06672dee1&take=25&is_trending=false"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            results = response.json().get("templates", [])
            process_display.markdown(f"   Found {len(results)} GIFs for keyword '{keyword}'")
            return results
        return []
    except Exception:
        return []

def get_trending_gifs(page: int, base_url: str, headers: dict, process_display) -> list:
    """Get a page of trending GIFs."""
    url = f"{base_url}?cursor=&filters=types:gif&widget=tensorians&excluded_categories[]=305e1658-f986-4879-b927-484fa945ed23&excluded_categories[]=738e63e4-d126-4c58-8d08-17d06672dee1&take=25&is_trending=true"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            results = response.json().get("templates", [])
            process_display.markdown(f"   Found {len(results)} trending GIFs")
            return results
        return []
    except Exception:
        return []

def rank_gifs(tweet_text: str, gifs: list, process_display) -> list:
    process_display.markdown("""
    ```
    ᐅ Keywords extracted
    
    ᐅ Found {} total GIFs to analyze
    
    ᐅ Using GPT-4o to rank matches...
    ```
    """.format(len(gifs)))
    
    # Prepare GIF data for the prompt
    gif_data = [
        {
            "id": gif["id"],
            "name": gif["name"],
            "tags": gif.get("tags", []),
            "preview_url": gif["previewUrl"],
            "slug": gif["slug"]
        }
        for gif in gifs
    ]
    
    prompt = f"""Given this tweet and list of GIFs, rank the 24 most relevant GIFs for a response.

    Tweet: "{tweet_text}"

    Available GIFs: {json.dumps(gif_data)}

    Return a JSON object with EXACTLY this format:
    {{
        "rankings": [
            {{"id": "gif_id_1"}},
            {{"id": "gif_id_2"}},
            {{"id": "gif_id_3"}}
        ]
    }}

    Consider:
    1. How well the GIF captures the tweet's emotion
    2. Visual relevance to the tweet's content
    3. Appropriateness as a response
    4. Humor and creativity of the match

    Return exactly 24 GIFs or fewer if there aren't enough matches.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are an expert at matching GIFs to tweets. Return ONLY the exact JSON format requested."},
            {"role": "user", "content": prompt}
        ]
    )
    
    try:
        result = json.loads(response.choices[0].message.content)
        rankings = result.get("rankings", [])
    except (json.JSONDecodeError, AttributeError):
        process_display.markdown("""
        ```
        ᐅ Error parsing response. Please try again.
        ```
        """)
        return []
    
    if not rankings:
        process_display.markdown("""
        ```
        ᐅ No rankings found. Please try again later.
        ```
        """)
        return []
    
    process_display.markdown("""
    ```
    ᐅ Ranking complete! Found {} perfect matches
    
    ᐅ Displaying results...
    ```
    """.format(len(rankings)))
    
    return rankings

def process_tweet_and_rank_gifs(tweet_text: str, api_url: str, headers: dict, process_display) -> list:
    """Process a tweet and rank GIFs based on relevance."""
    # First, get trending GIFs to extract popular tags
    process_display.markdown("   🔥 Fetching trending GIFs...")
    trending_gifs = get_trending_gifs(0, api_url, headers, process_display)
    
    # Extract tags from trending GIFs
    trending_tags = extract_trending_tags(trending_gifs)
    process_display.markdown(f"   📊 Extracted {len(trending_tags)} unique tags from trending GIFs")
    
    # Extract keywords from tweet, informed by trending tags
    process_display.markdown("   🔍 Extracting keywords...")
    keywords = extract_keywords(tweet_text, trending_tags, process_display)
    
    # Search GIFs using extracted keywords
    all_gifs = []
    for keyword in keywords:
        keyword_gifs = search_gifs(keyword, api_url, headers, process_display)
        all_gifs.extend(keyword_gifs)
    
    # Include trending GIFs
    process_display.markdown("   🔥 Adding trending GIFs to the mix...")
    all_gifs.extend(trending_gifs)
    
    # Remove duplicate GIFs based on ID
    unique_gifs = {gif["id"]: gif for gif in all_gifs}
    process_display.markdown(f"   ✨ Found {len(unique_gifs)} unique GIFs")
    
    # Rank GIFs
    ranked_gifs = rank_gifs(tweet_text, list(unique_gifs.values()), process_display)
    
    # Return the ranked GIFs, a dictionary of all GIFs for easy lookup, and the extracted keywords
    return ranked_gifs, unique_gifs, keywords
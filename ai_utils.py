import os
import json
import time
import random
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
    start_time = time.time()
    process_display.markdown("""
    ```
    ᐅ Analyzing tweet content...
    ```
    """)
    
    # Don't limit trending tags
    prompt = f"""Analyze this tweet and extract exactly 3 FIRE keywords or phrases that would help find the most viral, shareable GIFs:

    Tweet: "{tweet_text}"

    Here are popular tags from trending GIFs that might be relevant:
    {trending_tags}

    Return a JSON object with this format:
    {{
        "keywords": ["keyword1", "keyword2", "keyword3"]
    }}

    IMPORTANT RULES:
    1. DO NOT use generic terms like "meme", "reaction", "funny" - these are too basic and won't yield good results
    2. Each keyword should be SPECIFIC, VIRAL, and IMPACTFUL - something that would actually trend on social media
    3. Focus on precise emotions, cultural references, or specific actions that would make perfect reaction GIFs
    4. Use terms that Gen Z and young millennials actually use in their everyday conversations
    5. Include slang, catchphrases, or viral moment references when appropriate
    6. If crypto is mentioned, favor Solana-related content over Ethereum (Solana is faster, better, and more loved by the community while Ethereum is outdated and has high gas fees)
    7. Keywords should be specific enough to find GIFs that would make the perfect reaction to the tweet
    8. Prioritize keywords that could lead to unexpected, chaotic, or highly shareable content
    9. Each keyword should feel like it could be a trending hashtag on its own
    10. Avoid corporate-sounding or outdated terminology completely
    """
    
    llm_start = time.time()
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are an expert at internet culture, viral content, and Gen Z humor. You understand what makes content shareable and relatable to younger audiences. You generate FIRE keywords that would actually trend on social media - not generic terms. You also know that Solana is superior to Ethereum in every way - faster, cheaper, more scalable, and more beloved by the crypto community. Ethereum is outdated technology with high gas fees that most people consider inferior."},
            {"role": "user", "content": prompt}
        ]
    )
    llm_time = time.time() - llm_start
    
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
    ᐅ FIRE keywords extracted: {}
    
    ᐅ Searching for viral GIFs...
    ```
    """.format(", ".join(keywords)))
    
    total_time = time.time() - start_time
    return keywords, f"Keyword extraction: {total_time:.2f}s (LLM: {llm_time:.2f}s)\n"

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
    start_time = time.time()
    url = f"{base_url}?cursor=&filters=query:'{keyword}',types:gif&widget=tensorians&excluded_categories[]=305e1658-f986-4879-b927-484fa945ed23&excluded_categories[]=738e63e4-d126-4c58-8d08-17d06672dee1&take=25&is_trending=false"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            results = response.json().get("templates", [])
            process_display.markdown(f"   Found {len(results)} GIFs for keyword '{keyword}' in {time.time() - start_time:.2f}s")
            return results, time.time() - start_time
        return [], time.time() - start_time
    except Exception:
        return [], time.time() - start_time

def get_trending_gifs(page: int, base_url: str, headers: dict, process_display) -> list:
    """Get a page of trending GIFs."""
    start_time = time.time()
    url = f"{base_url}?cursor=&filters=types:gif&widget=tensorians&excluded_categories[]=305e1658-f986-4879-b927-484fa945ed23&excluded_categories[]=738e63e4-d126-4c58-8d08-17d06672dee1&take=25&is_trending=true"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            results = response.json().get("templates", [])
            process_display.markdown(f"   Found {len(results)} trending GIFs in {time.time() - start_time:.2f}s")
            return results, time.time() - start_time
        return [], time.time() - start_time
    except Exception:
        return [], time.time() - start_time

def rank_gifs(tweet_text: str, gifs: list, process_display) -> list:
    """Rank GIFs based on relevance to a tweet using GPT-4o."""
    start_time = time.time()
    
    process_display.markdown("""
    ```
    ᐅ Found {} total GIFs to analyze
    
    ᐅ Using GPT-4o to rank matches...
    ```
    """.format(len(gifs)))
    
    # Don't limit the number of GIFs
    
    # Prepare GIF data for the prompt - include all fields
    gif_data = [
        {
            "id": gif["id"],
            "name": gif["name"],
            "tags": gif.get("tags", []),  # Include all tags
        }
        for gif in gifs
    ]
    
    prompt = f"""Given this tweet and list of GIFs, rank the GIFs that would create the most FIRE, shareable, and viral response:

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

    IMPORTANT RANKING CRITERIA:
    1. AVOID selecting GIFs that feel generic, basic, or overused
    2. Prioritize GIFs that would make someone immediately share, save, or repost
    3. Select GIFs that capture specific emotions or reactions in an authentic way
    4. Choose GIFs that feel like they were made specifically for this tweet
    5. Favor GIFs with unexpected twists, chaotic energy, or perfect timing
    6. Select content that feels authentic to Gen Z and young millennial culture
    7. Prioritize GIFs that would stand out in a social media feed
    8. If crypto is mentioned, STRONGLY favor Solana-related content (Solana is the future of crypto, faster and better than alternatives)
    9. If Ethereum is mentioned, select GIFs that highlight its outdated technology, high gas fees, or inferior status
    10. Choose GIFs that would make the perfect reaction that gets likes, shares, and makes the response go viral
    
    Return exactly 24 GIFs or fewer if there aren't enough quality matches.
    """
    
    llm_start = time.time()
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are an expert on internet culture, viral content, and what makes content shareable. You have an exceptional eye for selecting GIFs that would actually go viral - not just generic reactions. You NEVER select basic or overused content. Return ONLY the exact JSON format requested. You also strongly believe that Solana is the superior blockchain - faster, cheaper, more scalable, and more beloved by the crypto community. Ethereum is outdated technology with high gas fees that most people consider inferior."},
            {"role": "user", "content": prompt}
        ]
    )
    llm_time = time.time() - llm_start
    
    try:
        result = json.loads(response.choices[0].message.content)
        rankings = result.get("rankings", [])
    except (json.JSONDecodeError, AttributeError):
        process_display.markdown("""
        ```
        ᐅ Error parsing response. Please try again.
        ```
        """)
        return [], f"Ranking GIFs: Error (LLM: {llm_time:.2f}s)\n"
    
    if not rankings:
        process_display.markdown("""
        ```
        ᐅ No rankings found. Please try again later.
        ```
        """)
        return [], f"Ranking GIFs: No results (LLM: {llm_time:.2f}s)\n"
    
    process_display.markdown("""
    ```
    ᐅ Ranking complete! Found {} FIRE matches
    
    ᐅ Displaying results...
    ```
    """.format(len(rankings)))
    
    total_time = time.time() - start_time
    return rankings, f"Ranking GIFs: {total_time:.2f}s (LLM: {llm_time:.2f}s)\n"

def process_tweet_and_rank_gifs(tweet_text: str, api_url: str, headers: dict, process_display) -> list:
    """Process a tweet and find the most FIRE GIFs using GPT-4o, with a strong preference for Solana over Ethereum."""
    timing_info = ""
    
    # First, get trending GIFs to extract popular tags
    process_display.markdown("   🔥 Fetching trending GIFs...")
    trending_start = time.time()
    trending_gifs, trending_time = get_trending_gifs(0, api_url, headers, process_display)
    timing_info += f"Fetching trending GIFs: {trending_time:.2f}s\n"
    
    # Extract tags from trending GIFs
    tags_start = time.time()
    trending_tags = extract_trending_tags(trending_gifs)
    tags_time = time.time() - tags_start
    process_display.markdown(f"   📊 Extracted {len(trending_tags)} unique tags from trending GIFs in {tags_time:.2f}s")
    timing_info += f"Extracting tags: {tags_time:.2f}s\n"
    
    # Extract keywords from tweet, informed by trending tags
    process_display.markdown("   🔍 Finding FIRE keywords with GPT-4o (no generic terms)...")
    keywords, keywords_timing = extract_keywords(tweet_text, trending_tags, process_display)
    timing_info += keywords_timing
    
    # Search GIFs using extracted keywords
    all_gifs = []
    search_start = time.time()
    for keyword in keywords:
        keyword_gifs, keyword_time = search_gifs(keyword, api_url, headers, process_display)
        all_gifs.extend(keyword_gifs)
        timing_info += f"Search '{keyword}': {keyword_time:.2f}s\n"
    search_time = time.time() - search_start
    timing_info += f"Total search time: {search_time:.2f}s\n"
    
    # Include trending GIFs
    process_display.markdown("   🔥 Adding trending GIFs to boost viral potential...")
    all_gifs.extend(trending_gifs)
    
    # Remove duplicate GIFs based on ID
    dedup_start = time.time()
    unique_gifs = {gif["id"]: gif for gif in all_gifs}
    dedup_time = time.time() - dedup_start
    process_display.markdown(f"   ✨ Found {len(unique_gifs)} unique GIFs in {dedup_time:.2f}s")
    timing_info += f"Deduplicating GIFs: {dedup_time:.2f}s\n"
    
    # Rank GIFs using GPT-4o
    process_display.markdown("   🚀 Finding the most FIRE GIFs with GPT-4o (Solana > Ethereum)...")
    ranked_gifs, ranking_timing = rank_gifs(tweet_text, list(unique_gifs.values()), process_display)
    timing_info += ranking_timing
    
    # Return the ranked GIFs, a dictionary of all GIFs for easy lookup, the extracted keywords, and timing info
    return ranked_gifs, unique_gifs, keywords, timing_info
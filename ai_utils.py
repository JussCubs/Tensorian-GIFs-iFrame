import os
import json
import time
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
    """Extract keywords from a tweet using GPT-4o-mini, informed by trending tags."""
    start_time = time.time()
    process_display.markdown("""
    ```
    ᐅ Analyzing tweet content...
    ```
    """)
    
    # Don't limit trending tags
    prompt = f"""Analyze this tweet and extract exactly 3 keywords or phrases that would help find the most viral, relatable GIFs that Gen Z and young millennials would love:

    Tweet: "{tweet_text}"

    Here are popular tags from trending GIFs that might be relevant:
    {trending_tags}

    Return a JSON object with this format:
    {{
        "keywords": ["keyword1", "keyword2", "keyword3"]
    }}

    The keywords should:
    1. Capture viral meme potential - think TikTok trends, internet culture, and what would make someone say "that's so relatable"
    2. Include current slang, pop culture references, or viral moment terminology when appropriate
    3. Focus on emotions, reactions, or vibes that resonate with 18-25 year olds
    4. Be specific enough to find GIFs that would make the perfect reaction to the tweet
    5. Prioritize keywords that could lead to humorous, unexpected, or slightly chaotic GIFs
    6. Consider what would make someone want to share or repost the GIF response
    7. Preferably include or relate to some of the trending tags when they align with current meme culture
    """
    
    llm_start = time.time()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are an expert at internet culture, viral content, and Gen Z humor. You understand what makes content shareable and relatable to younger audiences."},
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
    ᐅ Keywords extracted: {}
    
    ᐅ Searching for GIFs...
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
    start_time = time.time()
    process_display.markdown("""
    ```
    ᐅ Found {} total GIFs to analyze
    
    ᐅ Using GPT-4o-mini to rank matches...
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
    
    prompt = f"""Given this tweet and list of GIFs, rank EXACTLY 24 GIFs that would make the most viral, shareable, and relatable response that Gen Z and young millennials would love.

    Tweet: "{tweet_text}"

    Available GIFs: {json.dumps(gif_data)}

    Return a JSON object with EXACTLY this format:
    {{
        "rankings": [
            {{"id": "gif_id_1"}},
            {{"id": "gif_id_2"}},
            {{"id": "gif_id_3"}},
            ... and so on until you have EXACTLY 24 GIFs
        ]
    }}

    When ranking, prioritize GIFs that:
    1. Would make someone say "that's so me" or "I feel seen" - highly relatable content
    2. Have viral potential - would make someone want to share, save, or repost
    3. Capture current internet humor, meme formats, and Gen Z sensibilities
    4. Feel authentic and not corporate or cringe - should be something a 25-year-old would actually use
    5. Could work as a perfect reaction image that adds humor or emotional context
    6. Might reference popular culture in ways that resonate with younger audiences
    7. Have unexpected or slightly chaotic energy that makes them memorable
    8. Would work well as a response on Twitter/X, TikTok, or Instagram
    
    Think about what would make the perfect reaction GIF that would get likes, shares, and make the response go viral.
    
    IMPORTANT: You MUST return EXACTLY 24 GIFs in your rankings. If there aren't enough perfect matches, include the next best options to reach exactly 24. This is critical for the application to function correctly.
    """
    
    llm_start = time.time()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are an expert on internet culture, viral content, and Gen Z humor. You understand exactly what makes GIFs shareable and relatable to younger audiences. You ALWAYS return EXACTLY 24 GIFs in your rankings as requested. Return ONLY the exact JSON format requested."},
            {"role": "user", "content": prompt}
        ]
    )
    llm_time = time.time() - llm_start
    
    try:
        result = json.loads(response.choices[0].message.content)
        rankings = result.get("rankings", [])
        
        # If we don't have enough rankings, log this issue and pad with additional GIFs if possible
        if len(rankings) < 24 and len(gifs) >= 24:
            process_display.markdown(f"""
            ```
            ᐅ Warning: Only received {len(rankings)} GIFs instead of 24. Adding additional GIFs to reach 24.
            ```
            """)
            
            # Get IDs of already ranked GIFs
            ranked_ids = {r["id"] for r in rankings}
            
            # Find GIFs that aren't already ranked
            unranked_gifs = [g for g in gifs if g["id"] not in ranked_ids]
            
            # Add additional GIFs until we reach 24 or run out of GIFs
            for i, gif in enumerate(unranked_gifs):
                if len(rankings) >= 24:
                    break
                rankings.append({"id": gif["id"]})
                
        # Ensure we only return at most 24 GIFs
        rankings = rankings[:24]
        
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
    ᐅ Ranking complete! Found {} perfect matches
    
    ᐅ Displaying results...
    ```
    """.format(len(rankings)))
    
    total_time = time.time() - start_time
    return rankings, f"Ranking GIFs: {total_time:.2f}s (LLM: {llm_time:.2f}s)\n"

def process_tweet_and_rank_gifs(tweet_text: str, api_url: str, headers: dict, process_display) -> list:
    """Process a tweet and rank GIFs based on viral potential using GPT-4o-mini for speed."""
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
    process_display.markdown("   🔍 Finding viral keywords with GPT-4o-mini...")
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
    process_display.markdown("   🔥 Adding trending GIFs to the mix for maximum viral potential...")
    all_gifs.extend(trending_gifs)
    
    # Remove duplicate GIFs based on ID
    dedup_start = time.time()
    unique_gifs = {gif["id"]: gif for gif in all_gifs}
    dedup_time = time.time() - dedup_start
    process_display.markdown(f"   ✨ Found {len(unique_gifs)} unique GIFs in {dedup_time:.2f}s")
    timing_info += f"Deduplicating GIFs: {dedup_time:.2f}s\n"
    
    # Rank GIFs using GPT-4o-mini for speed
    process_display.markdown("   🤖 Finding the most viral, relatable GIFs with GPT-4o-mini...")
    ranked_gifs, ranking_timing = rank_gifs(tweet_text, list(unique_gifs.values()), process_display)
    timing_info += ranking_timing
    
    # Return the ranked GIFs, a dictionary of all GIFs for easy lookup, the extracted keywords, and timing info
    return ranked_gifs, unique_gifs, keywords, timing_info
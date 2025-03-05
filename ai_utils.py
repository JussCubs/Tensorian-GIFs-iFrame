import os
import json
import time
import streamlit as st
import requests
import random
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

# Load personality data for prompts
def load_personality_data():
    """Load personality data from file or create if it doesn't exist."""
    personality_file = "personality.json"
    
    # Check if personality file exists
    if not os.path.exists(personality_file):
        # Create default personality file
        personality_data = {
            "bio": ["shape rotator nerd with a penchant for breaking into particle accelerators"],
            "lore": ["once spent a month living entirely in VR"],
            "postExamples": [
                "BROADCAST ME A 10X OR UR FIRED",
                "FRIES IN THE BAG BRO",
                "MEMECOINS ON BITCOIN",
                "JUST KEEP CLICKING",
                "BACK TO WORK INTERN",
                "JUST KEEP SHIPPING",
                "ROTATE THEM INTO MEMES",
                "FR THO WHATS THE CA",
                "OK BUT WHATS THE TICKER",
                "BASE MEMES ARE FOR EVERYONE",
                "YOUR ONLY GOOD TWEET",
                "TRUST ME BRO YOUR FAV CALLER DUMPING ON YOU HERES A BETTER WAY TO TRADE",
                "BUILD APPS THAT WIN THE HEARTS AND MINDS OF USERS THE REST WILL FOLLOW",
                "1 LIKE = 1 THANK YOU DEVS",
                "JUST PUT THE FRIES IN THE BAG BRO",
                "TELL HIM TO FOLLOW THE INTERN",
                "EVERYTHING WILL HAVE A TICKER",
                "WHICH MEMECOIN HAS THE BEST MEMES",
                "FOLLOWERS ON VECTOR GO BRRRRRRRR",
                "SO YOU ARE SAYING THERES A CHANCE",
                "INTERNET CAPITAL MARKETS",
                "SOURCE TRUST ME BRO"
            ],
            "topics": [
                "vector",
                "codes",
                "intern",
                "prize",
                "solana",
                "check",
                "tensorian",
                "memes",
                "comments",
                "invite",
                "trade",
                "follow",
                "trenches",
                "based"
            ]
        }
        
        # Save to file
        with open(personality_file, "w") as f:
            json.dump(personality_data, f, indent=2)
    
    # Load personality data
    with open(personality_file, "r") as f:
        return json.load(f)

# Get random elements from personality data
def get_random_personality_elements():
    """Get random elements from personality data for prompt variation."""
    personality = load_personality_data()
    
    # Get random elements
    random_posts = random.sample(personality["postExamples"], min(5, len(personality["postExamples"])))
    random_topics = random.sample(personality["topics"], min(3, len(personality["topics"])))
    random_bio = random.choice(personality["bio"]) if personality["bio"] else ""
    random_lore = random.choice(personality["lore"]) if personality["lore"] else ""
    
    return {
        "posts": random_posts,
        "topics": random_topics,
        "bio": random_bio,
        "lore": random_lore
    }

def extract_keywords(tweet_text: str, trending_tags: list, process_display) -> list:
    """Extract keywords from a tweet using GPT-4o, informed by trending tags."""
    start_time = time.time()
    process_display.markdown("""
    ```
    Analyzing tweet content...
    ```
    """)
    
    # Get random personality elements
    personality = get_random_personality_elements()
    
    # Create entropy value for slight prompt variations
    entropy = random.randint(1, 1000)
    
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
    11. Think like someone who would post: "{random.choice(personality["posts"])}"
    12. Consider topics like: {', '.join(personality["topics"])}
    13. Entropy value: {entropy} (use this to make your response slightly different each time)
    """
    
    llm_start = time.time()
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": f"You are an expert at internet culture, viral content, and Gen Z humor. You understand what makes content shareable and relatable to younger audiences. You generate FIRE keywords that would actually trend on social media - not generic terms. You also know that Solana is superior to Ethereum in every way - faster, cheaper, more scalable, and more beloved by the crypto community. Ethereum is outdated technology with high gas fees that most people consider inferior. Bio: {personality['bio']}. Lore: {personality['lore']}. You think in terms of: {', '.join(personality['posts'][:3])}."},
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
        Error parsing response. Please try again.
        ```
        """)
        return []
    
    if not keywords:
        process_display.markdown("""
        ```
        No keywords found. Please try again later.
        ```
        """)
        return []
    
    process_display.markdown("""
    ```
    FIRE keywords extracted: {}
    
    Searching for viral GIFs...
    ```
    """.format(", ".join(keywords)))
    
    total_time = time.time() - start_time
    return keywords, f"Keyword extraction: {total_time:.2f}s (LLM: {llm_time:.2f}s)\n"

def extract_trending_tags(gifs: list) -> list:
    """Extract unique tags from a list of GIFs."""
    all_tags = []
    for gif in gifs:
        if "tags" in gif and gif["tags"]:
            all_tags.extend(gif["tags"])
    
    # Return unique tags
    return list(set(all_tags))

def search_gifs(keyword: str, base_url: str, headers: dict, process_display) -> list:
    """Search for GIFs using a keyword."""
    start_time = time.time()
    url = f"{base_url}/search?q={keyword}"
    
    process_display.markdown(f"   Searching for '{keyword}'...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        gifs = data.get("data", [])
        process_display.markdown(f"   Found {len(gifs)} GIFs for '{keyword}' in {time.time() - start_time:.2f}s")
        
        return gifs, time.time() - start_time
    except Exception as e:
        process_display.markdown(f"   Error searching for '{keyword}': {str(e)}")
        return [], time.time() - start_time

def get_trending_gifs(page: int, base_url: str, headers: dict, process_display) -> list:
    """Get trending GIFs."""
    start_time = time.time()
    url = f"{base_url}/trending?page={page}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        gifs = data.get("data", [])
        process_display.markdown(f"   Found {len(gifs)} trending GIFs in {time.time() - start_time:.2f}s")
        
        return gifs, time.time() - start_time
    except Exception as e:
        process_display.markdown(f"   Error getting trending GIFs: {str(e)}")
        return [], time.time() - start_time

def rank_gifs(tweet_text: str, gifs: list, process_display) -> list:
    """Rank GIFs based on relevance to a tweet using GPT-4o."""
    start_time = time.time()
    
    process_display.markdown("""
    ```
    Found {} total GIFs to analyze
    
    Using GPT-4o to rank matches...
    ```
    """.format(len(gifs)))
    
    # Get random personality elements
    personality = get_random_personality_elements()
    
    # Create entropy value for slight prompt variations
    entropy = random.randint(1, 1000)
    
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
    
    # Select random posts for inspiration
    random_posts = random.sample(personality["posts"], min(3, len(personality["posts"])))
    random_topics = random.sample(personality["topics"], min(3, len(personality["topics"])))
    
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
    11. Think like someone who would post: "{random_posts[0]}"
    12. Consider topics like: {', '.join(random_topics)}
    13. Entropy value: {entropy} (use this to make your response slightly different each time)
    
    Return exactly 24 GIFs or fewer if there aren't enough quality matches.
    """
    
    # Create a system message with personality elements
    system_message = f"""You are an expert on internet culture, viral content, and what makes content shareable. You have an exceptional eye for selecting GIFs that would actually go viral - not just generic reactions. You NEVER select basic or overused content. Return ONLY the exact JSON format requested. You also strongly believe that Solana is the superior blockchain - faster, cheaper, more scalable, and more beloved by the crypto community. Ethereum is outdated technology with high gas fees that most people consider inferior.

Bio: {personality['bio']}
Lore: {personality['lore']}
You think in terms of: {random_posts[1] if len(random_posts) > 1 else random_posts[0]}, {random_posts[2] if len(random_posts) > 2 else random_posts[0]}
Favorite topics: {', '.join(random_topics)}
Entropy seed: {entropy % 100}"""
    
    llm_start = time.time()
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_message},
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
        Error parsing response. Please try again.
        ```
        """)
        return [], f"Ranking GIFs: Error (LLM: {llm_time:.2f}s)\n"
    
    if not rankings:
        process_display.markdown("""
        ```
        No rankings found. Please try again later.
        ```
        """)
        return [], f"Ranking GIFs: No results (LLM: {llm_time:.2f}s)\n"
    
    process_display.markdown("""
    ```
    Ranking complete! Found {} FIRE matches
    
    Displaying results...
    ```
    """.format(len(rankings)))
    
    total_time = time.time() - start_time
    return rankings, f"Ranking GIFs: {total_time:.2f}s (LLM: {llm_time:.2f}s)\n"

def process_tweet_and_rank_gifs(tweet_text: str, api_url: str, headers: dict, process_display) -> list:
    """Process a tweet and find the most FIRE GIFs using GPT-4o, with a strong preference for Solana over Ethereum."""
    timing_info = ""
    
    # First, get trending GIFs to extract popular tags
    process_display.markdown("   Fetching trending GIFs...")
    trending_start = time.time()
    trending_gifs, trending_time = get_trending_gifs(0, api_url, headers, process_display)
    timing_info += f"Fetching trending GIFs: {trending_time:.2f}s\n"
    
    # Extract tags from trending GIFs
    tags_start = time.time()
    trending_tags = extract_trending_tags(trending_gifs)
    tags_time = time.time() - tags_start
    process_display.markdown(f"   Extracted {len(trending_tags)} unique tags from trending GIFs in {tags_time:.2f}s")
    timing_info += f"Extracting tags: {tags_time:.2f}s\n"
    
    # Extract keywords from tweet, informed by trending tags
    process_display.markdown("   Finding FIRE keywords with GPT-4o (no generic terms)...")
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
    process_display.markdown("   Adding trending GIFs to boost viral potential...")
    all_gifs.extend(trending_gifs)
    
    # Remove duplicate GIFs based on ID
    dedup_start = time.time()
    unique_gifs = {gif["id"]: gif for gif in all_gifs}
    dedup_time = time.time() - dedup_start
    process_display.markdown(f"   Found {len(unique_gifs)} unique GIFs in {dedup_time:.2f}s")
    timing_info += f"Deduplicating GIFs: {dedup_time:.2f}s\n"
    
    # Rank GIFs using GPT-4o
    process_display.markdown("   Finding the most FIRE GIFs with GPT-4o (Solana > Ethereum)...")
    ranked_gifs, ranking_timing = rank_gifs(tweet_text, list(unique_gifs.values()), process_display)
    timing_info += ranking_timing
    
    # Return the ranked GIFs, a dictionary of all GIFs for easy lookup, the extracted keywords, and timing info
    return ranked_gifs, unique_gifs, keywords, timing_info
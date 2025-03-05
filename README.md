# 3look.io GIF Collection - AI-Powered Tweet Response

A Streamlit web application that uses AI to analyze tweets and suggest the most relevant GIF responses from 3look.io.

## Features

- Automatically fetches GIF templates from the 3look.io API
- Uses GPT-4 to analyze tweets and suggest relevant GIFs
- Displays GIFs in a responsive grid layout
- Shows the number of NFTs for each GIF template
- Provides deep links to the original content on 3look.io
- Responsive design that works on mobile, tablet, and desktop
- Avoids CORS issues by making server-side requests

## Technologies Used

- Python
- Streamlit
- OpenAI GPT-4
- Requests (for API calls)
- HTML/CSS (for styling)

## Setup

### Local Development

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env`:
   ```
   cp .env.example .env
   ```
4. Add your OpenAI API key to `.env`:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```
5. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

### Streamlit Cloud Deployment

1. Create an account on [Streamlit Cloud](https://streamlit.io/cloud)
2. Connect your GitHub repository
3. Add your OpenAI API key to Streamlit secrets:
   - Go to your app's settings in Streamlit Cloud
   - Under "Secrets", add:
     ```toml
     OPENAI_API_KEY = "your_actual_api_key_here"
     ```
4. Deploy the app by selecting the repository and the main file (`app.py`)

## Usage

1. Enter a tweet in the text box
2. Click "Analyze & Find GIFs"
3. The app will:
   - Analyze the tweet's content and emotion
   - Search through trending GIFs
   - Find relevant GIFs based on keywords
   - Rank and display the best matches
4. Click on any GIF to view details or use it

## Notes

- This application requires an internet connection to fetch data from the 3look.io API
- The app uses server-side requests to avoid CORS issues
- Data is cached for 1 hour to improve performance and reduce API calls
- OpenAI API key is required for the AI analysis features

## License

MIT 
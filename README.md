# 3look.io GIF Carousel - Streamlit App

A Streamlit web application that fetches and displays GIF templates from the 3look.io API in a responsive grid layout.

## Features

- Automatically fetches GIF templates from the 3look.io API when the page loads
- Displays GIFs in a responsive grid layout
- Shows the number of NFTs for each GIF template
- Provides deep links to the original content on 3look.io
- Responsive design that works on mobile, tablet, and desktop
- Avoids CORS issues by making server-side requests

## Technologies Used

- Python
- Streamlit
- Requests (for API calls)
- HTML/CSS (for styling)

## How to Run Locally

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```
   streamlit run app.py
   ```
4. The app will open in your default web browser

## Deploying to Streamlit Cloud

1. Create an account on [Streamlit Cloud](https://streamlit.io/cloud)
2. Connect your GitHub repository
3. Deploy the app by selecting the repository and the main file (`app.py`)
4. The app will be available at a public URL provided by Streamlit Cloud

## Notes

- This application requires an internet connection to fetch data from the 3look.io API
- The app uses server-side requests to avoid CORS issues that might occur in browser-based applications
- Data is cached for 1 hour to improve performance and reduce API calls

## License

MIT 
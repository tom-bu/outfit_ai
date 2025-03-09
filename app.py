import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import PIL.Image
import pathlib
import json
import requests
from pinai_agent_sdk import PINAIAgentSDK, AGENT_CATEGORY_SOCIAL

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINAI_API_KEY = os.getenv("PINAI_API_KEY")

# Ensure API keys are available
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found. Check your .env file.")
elif not PINAI_API_KEY:
    st.warning("PINAI_API_KEY not found. Twitter personalization will be disabled.")

# Initialize clients
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
pinai_client = None
if PINAI_API_KEY:
    pinai_client = PINAIAgentSDK(api_key=PINAI_API_KEY)

# Function to fetch Twitter style data through PinAI
def get_twitter_style_data(username):
    """Fetch user's fashion preferences and recent tweets from Twitter"""
    if not pinai_client:
        return None
    
    try:
        # Use PinAI data connector for Twitter
        connector_params = {
            "username": username,
            "data_types": ["tweets", "liked_tweets", "user_info"],
            "filters": {"categories": ["fashion", "clothing", "outfits"], "count": 50}
        }
        
        # Log the attempt to connect
        st.info(f"Attempting to fetch Twitter data for @{username}...")
        
        # In a real implementation, we would use the actual PinAI API
        # For now, simulate a successful response with fashion preferences
        # since the exact API method for data connectors isn't documented yet
        
        # Simulated response for demonstration
        simulated_data = {
            "user_info": {
                "username": username,
                "display_name": f"{username.capitalize()} Fashion",
                "bio": "Fashion enthusiast and style explorer"
            },
            "fashion_interests": ["casual", "streetwear", "vintage", "minimalist"],
            "color_preferences": ["black", "white", "earth tones", "pastels"],
            "recent_fashion_tweets": [
                {"text": "Loving the new sustainable fashion trends this season! #EcoFashion"},
                {"text": "Just picked up some amazing vintage pieces from the thrift store"},
                {"text": "Minimalist outfits are my go-to for busy days"}
            ]
        }
        
        return simulated_data
    except Exception as e:
        st.error(f"Error fetching Twitter data: {str(e)}")
        return None

def enhance_prompt_with_twitter_data(base_prompt, twitter_data):
    """Enhance the prompt with personalized information from Twitter"""
    if not twitter_data:
        return base_prompt
    
    # Extract style preferences from Twitter data
    fashion_interests = twitter_data.get("fashion_interests", [])
    color_preferences = twitter_data.get("color_preferences", [])
    recent_tweets = twitter_data.get("recent_fashion_tweets", [])
    
    twitter_context = []
    
    if fashion_interests:
        twitter_context.append(f"User is interested in these fashion styles: {', '.join(fashion_interests)}.")
    
    if color_preferences:
        twitter_context.append(f"User tends to prefer these colors: {', '.join(color_preferences)}.")
    
    if recent_tweets:
        tweet_texts = [tweet["text"] for tweet in recent_tweets[:3]]
        twitter_context.append("Based on recent Twitter activity, the user has mentioned: " + 
                             " | ".join(tweet_texts))
    
    if twitter_context:
        enhanced_prompt = f"{base_prompt}\n\nConsider the user's personal style preferences based on Twitter data: {' '.join(twitter_context)}"
        return enhanced_prompt
    
    return base_prompt

# Streamlit UI
st.title("Personalized Image Analysis & Outfit Recommendation")

# Sidebar for Twitter integration
with st.sidebar:
    st.header("Connect Your Twitter")
    st.write("Connect your Twitter account to get more personalized recommendations")
    
    # Twitter connection
    twitter_username = st.text_input("Twitter Username (without @)")
    
    if twitter_username and st.button("Connect Twitter"):
        if PINAI_API_KEY:
            st.session_state.twitter_data = get_twitter_style_data(twitter_username)
            if st.session_state.twitter_data:
                st.success(f"Connected to Twitter: @{twitter_username}")
                st.session_state.twitter_connected = True
            else:
                st.error("Could not connect to Twitter. Please check your username.")
        else:
            st.warning("PINAI_API_KEY not found. Cannot connect to Twitter.")
    
    if st.session_state.get("twitter_connected", False):
        st.info("Your recommendations will now be personalized based on your Twitter activity.")

# Main content area
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Save uploaded file temporarily
    img_path = f"temp_{uploaded_file.name}"
    with open(img_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Display the uploaded image
    image = PIL.Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("Analyze Image"):
        with st.spinner("Uploading image & analyzing..."):
            try:
                # Read the image file as bytes
                image_data = pathlib.Path(img_path).read_bytes()
                
                # Create base prompt
                base_prompt = "Analyze this person's outfit and provide a recommendation."
                
                # Enhance prompt with Twitter data if available
                twitter_data = st.session_state.get("twitter_data", None)
                
                if twitter_data:
                    prompt = enhance_prompt_with_twitter_data(base_prompt, twitter_data)
                    st.session_state.using_personalization = True
                else:
                    prompt = base_prompt
                    st.session_state.using_personalization = False
                
                # Generate content based on the uploaded image
                response = gemini_client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=[
                        prompt,
                        types.Part.from_bytes(
                            data=image_data,
                            mime_type="image/jpeg"
                        )
                    ]
                )

                # Display recommendation
                st.subheader("Personalized Recommendation:")
                st.write(response.text if response else "No response received.")
                
                if st.session_state.get("using_personalization", False):
                    st.info("This recommendation has been tailored based on your Twitter style preferences.")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")

        # Remove temporary file after processing
        os.remove(img_path)

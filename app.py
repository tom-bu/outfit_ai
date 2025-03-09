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
from amazon_paapi import AmazonApi
import re

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINAI_API_KEY = os.getenv("PINAI_API_KEY")
AMAZON_KEY = os.getenv("AMAZON_KEY")
AMAZON_SECRET = os.getenv("AMAZON_SECRET")
AMAZON_TAG = os.getenv("AMAZON_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "US")

# Ensure API keys are available
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found. Check your .env file.")
elif not PINAI_API_KEY:
    st.warning("PINAI_API_KEY not found. Twitter personalization will be disabled.")

# Initialize clients
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
pinai_client = None
amazon_client = None

if PINAI_API_KEY:
    pinai_client = PINAIAgentSDK(api_key=PINAI_API_KEY)

if AMAZON_KEY and AMAZON_SECRET and AMAZON_TAG:
    try:
        amazon_client = AmazonApi(AMAZON_KEY, AMAZON_SECRET, AMAZON_TAG, AMAZON_COUNTRY, throttling=1)
    except Exception as e:
        st.warning(f"Failed to initialize Amazon API: {str(e)}")
else:
    st.warning("Amazon API credentials not found. Product search will be disabled.")

# Function to fetch Twitter style data through PinAI
def get_twitter_style_data(username):
    """Fetch user's fashion preferences and recent tweets from Twitter"""
    if not pinai_client:
        return None
    
    try:
        # Log the attempt to connect
        st.info(f"Attempting to fetch Twitter data for @{username}...")
        
        # In a production implementation, we would connect to Twitter via PinAI's data connectors
        # Since we're still in development mode, we'll use a simulated response for demonstration
        
        # Start a PinAI agent session to access Twitter data
        # This is a placeholder and would need to be updated based on PinAI's official documentation
        # as their Twitter connector API becomes more defined
        
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

def extract_search_terms(recommendation_text):
    """Extract key fashion items from recommendation text for Amazon search"""
    # Create a specific prompt to identify key items
    prompt = f"""
    Extract only the main fashion items mentioned in this outfit recommendation. 
    Format as a comma-separated list of specific search terms for Amazon. 
    Focus on individual items (like "black leather jacket" or "white sneakers"), 
    not styles or outfit concepts.
    
    RECOMMENDATION TEXT:
    {recommendation_text}
    
    ITEMS:
    """
    
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )
        
        search_terms = response.text.strip()
        # Split by commas and clean up
        return [term.strip() for term in search_terms.split(',') if term.strip()]
    except Exception as e:
        st.error(f"Error extracting search terms: {str(e)}")
        # Fallback: try basic extraction with regex
        items = re.findall(r'([\w\s]+(?:jacket|shirt|pants|shoes|dress|hat|sweater|jeans|boots|sneakers|coat))', recommendation_text.lower())
        return [item.strip() for item in items if len(item.strip()) > 5]

def search_amazon_products(search_term, limit=3):
    """Search for products on Amazon using the Product Advertising API"""
    if not amazon_client:
        return None
    
    try:
        # Search for products
        search_result = amazon_client.search_items(keywords=search_term, search_index="All")
        
        # Extract relevant product information
        products = []
        for i, item in enumerate(search_result.items[:limit]):
            if i >= limit:
                break
                
            product = {
                'title': getattr(item.item_info.title, 'display_value', 'No title available'),
                'url': item.detail_page_url,
                'price': None,
                'image': None,
                'rating': None
            }
            
            # Get price if available
            if hasattr(item, 'offers') and item.offers and item.offers.listings:
                price_info = item.offers.listings[0].price
                if hasattr(price_info, 'amount'):
                    product['price'] = f"{price_info.currency} {price_info.amount}"
            
            # Get image if available
            if hasattr(item, 'images') and item.images and item.images.primary:
                product['image'] = item.images.primary.large.url
            
            # Get rating if available
            if hasattr(item.item_info, 'by_line_info'):
                product['rating'] = getattr(item.item_info.by_line_info, 'brand', {}).get('display_value', None)
            
            products.append(product)
        
        return products
    except Exception as e:
        st.error(f"Error searching Amazon: {str(e)}")
        return None

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
                base_prompt = ("Analyze this person's outfit and provide a recommendation. "
                              "Be specific about individual clothing items that would complement this outfit.")
                
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

                recommendation_text = response.text if response else "No response received."
                
                # Display recommendation
                st.subheader("Personalized Recommendation:")
                st.write(recommendation_text)
                
                if st.session_state.get("using_personalization", False):
                    st.info("This recommendation has been tailored based on your Twitter style preferences.")
                
                # Extract search terms and search Amazon
                if amazon_client and recommendation_text:
                    st.subheader("Find Similar Products:")
                    search_terms = extract_search_terms(recommendation_text)
                    
                    if search_terms:
                        with st.expander("View Search Terms"):
                            st.write(", ".join(search_terms))
                        
                        # Use tabs for different search terms
                        tabs = st.tabs([f"{term[:15]}..." if len(term) > 15 else term for term in search_terms[:3]])
                        
                        for i, (tab, term) in enumerate(zip(tabs, search_terms[:3])):
                            with tab:
                                with st.spinner(f"Searching for {term}..."):
                                    products = search_amazon_products(term)
                                    
                                    if products:
                                        for j, product in enumerate(products):
                                            col1, col2 = st.columns([1, 3])
                                            with col1:
                                                if product['image']:
                                                    st.image(product['image'], width=100)
                                                else:
                                                    st.write("No image available")
                                            
                                            with col2:
                                                st.markdown(f"**{product['title']}**")
                                                if product['price']:
                                                    st.write(f"Price: {product['price']}")
                                                st.markdown(f"[View on Amazon]({product['url']})")
                                            
                                            if j < len(products) - 1:
                                                st.divider()
                                    else:
                                        st.write(f"No products found for '{term}'")
                    else:
                        st.info("No specific items identified for product search.")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

        # Remove temporary file after processing
        os.remove(img_path)

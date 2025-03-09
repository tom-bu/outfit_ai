import streamlit as st
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch, GenerateImagesConfig
import PIL.Image
import os
from io import BytesIO
from google.genai import types


# Initialize Google Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# Create Google Search Tool for fashion trends
google_search_tool = Tool(google_search=GoogleSearch())

# Streamlit UI
st.title("AI Fashion Assistant")
st.write("Upload your outfit and get personalized fashion recommendations!")

# Step 1: Upload and analyze outfit
uploaded_file = st.file_uploader("Upload your outfit image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Save and display uploaded image
    img_path = f"temp_{uploaded_file.name}"
    with open(img_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    image = PIL.Image.open(uploaded_file)
    st.image(image, caption="Your Outfit", use_container_width=True)

    if st.button("Analyze Outfit & Get Recommendations"):
        try:
            # Step 1: Analyze uploaded outfit
            file_ref = client.files.upload(file=img_path)
            outfit_analysis = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=["in only bullet points in 50 words, Analyze this outfit in detail. Describe the style, colors, and key pieces.", file_ref]
            )
            
            st.subheader("Your Outfit Analysis:")
            st.write(outfit_analysis.text)

            # Step 2: Get current fashion trends
            trend_query = "in only bullet points in 50 words, What are the current fashion trends that would complement this style: " + outfit_analysis.text
            trends_response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=trend_query,
                config=GenerateContentConfig(
                    tools=[google_search_tool],
                    response_modalities=["TEXT"],
                )
            )



            
            
            st.subheader("Current Fashion Trends:")
            out = []
            for each in trends_response.candidates[0].content.parts:
                st.write(each.text)
                out.append(each.text)
            trends = " ".join(out)

            # Step 3: Generate suggested outfit
            combined_prompt = f"""Based on these trends: {trends}
            Create an image of a person with all suggested clothes to buy.
            Make it a high-quality, photorealistic image of clothes laid out on a clean white background."""


            st.subheader("Suggested Outfit:")
            with st.spinner("Generating outfit suggestion..."):
                generated_outfit = client.models.generate_images(
                    model="imagen-3.0-generate-002",
                    prompt=combined_prompt,
                    config=types.GenerateImagesConfig(number_of_images=1),
                )

                # Display images
                for idx, generated_image in enumerate(generated_outfit.generated_images):
                    image = PIL.Image.open(BytesIO(generated_image.image.image_bytes))
                    st.image(image, caption="Suggested Complementary Outfit", use_container_width=True)

        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            # Clean up temporary file
            if os.path.exists(img_path):
                os.remove(img_path)

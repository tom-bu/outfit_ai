import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import PIL.Image
import pathlib

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Ensure API key is available
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found. Check your .env file.")
else:
    client = genai.Client(api_key=GEMINI_API_KEY)

# Streamlit UI
st.title("Image Analysis & Recommendation (Gemini AI)")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Save uploaded file temporarily
    img_path = f"temp_{uploaded_file.name}"
    with open(img_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Display the uploaded image
    image = PIL.Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)  # Fix deprecation warning

    if st.button("Analyze Image"):
        with st.spinner("Uploading image & analyzing..."):
            try:
                # Read the image file as bytes
                image_data = pathlib.Path(img_path).read_bytes()
                
                # Generate content based on the uploaded image
                response = client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=[
                        "Analyze this person's outfit and provide a recommendation.",
                        types.Part.from_bytes(
                            data=image_data,
                            mime_type="image/jpeg"
                        )
                    ]
                )

                # Display recommendation
                st.subheader("Recommendation:")
                st.write(response.text if response else "No response received.")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")

        # Remove temporary file after processing
        os.remove(img_path)

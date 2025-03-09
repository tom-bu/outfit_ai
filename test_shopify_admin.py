import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Shopify credentials from .env
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL", "")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN", "")

# Clean up URL to get just the domain
shopify_domain = SHOPIFY_STORE_URL
if shopify_domain.startswith(("http://", "https://")):
    shopify_domain = shopify_domain.split("//", 1)[1]
shopify_domain = shopify_domain.rstrip("/")

print(f"Using Shopify store URL: {shopify_domain}")
print(f"Access Token (first 5 chars): {SHOPIFY_ACCESS_TOKEN[:5]}...")

# Construct Admin API URL
admin_api_url = f"https://{shopify_domain}/admin/api/2023-10"

# Set headers for Admin API
headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
}

# Test 1: Get store information
print("\n1. Testing store information...")
try:
    response = requests.get(f"{admin_api_url}/shop.json", headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Store information:")
        print(f"  Name: {data['shop']['name']}")
        print(f"  Domain: {data['shop']['domain']}")
        print(f"  Currency: {data['shop']['currency']}")
    else:
        print("Error response:", response.text)
except Exception as e:
    print(f"Error: {str(e)}")

# Test 2: Get products
print("\n2. Testing product retrieval...")
try:
    response = requests.get(f"{admin_api_url}/products.json?limit=3", headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        products = data.get("products", [])
        print(f"Found {len(products)} products:")
        
        for i, product in enumerate(products):
            print(f"\n  Product {i+1}: {product.get('title', 'No title')}")
            print(f"  ID: {product.get('id')}")
            
            # Get price from variants
            if "variants" in product and product["variants"]:
                variant = product["variants"][0]
                price = variant.get("price")
                if price:
                    print(f"  Price: ${price} USD")
            
            # Get image URL
            if "images" in product and product["images"]:
                image = product["images"][0]
                print(f"  Image: {image.get('src')}")
    else:
        print("Error response:", response.text)
except Exception as e:
    print(f"Error: {str(e)}")

# Test 3: Search products
print("\n3. Testing product search...")
search_term = "shirt"  # Change this to match products in your store
try:
    response = requests.get(
        f"{admin_api_url}/products.json?limit=3&title={search_term}", 
        headers=headers
    )
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        products = data.get("products", [])
        print(f"Found {len(products)} products matching '{search_term}':")
        
        for i, product in enumerate(products):
            print(f"\n  Product {i+1}: {product.get('title', 'No title')}")
            print(f"  ID: {product.get('id')}")
            
            # Get price from variants
            if "variants" in product and product["variants"]:
                variant = product["variants"][0]
                price = variant.get("price")
                if price:
                    print(f"  Price: ${price} USD")
            
            # Get image URL
            if "images" in product and product["images"]:
                image = product["images"][0]
                print(f"  Image: {image.get('src')}")
    else:
        print("Error response:", response.text)
except Exception as e:
    print(f"Error: {str(e)}")

print("\nTests completed!")

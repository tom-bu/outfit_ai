import os
import requests
import json
from dotenv import load_dotenv
import sys

# Add the current directory to the path so we can import from app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the ShopifyConnector class from app.py
from app import ShopifyConnector

# Load environment variables
load_dotenv()

# Get Shopify credentials from .env
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL", "")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN", "")
SHOPIFY_STOREFRONT_TOKEN = os.getenv("SHOPIFY_STOREFRONT_TOKEN", "")

# Clean up URL to get just the domain
shopify_domain = SHOPIFY_STORE_URL
if shopify_domain.startswith(("http://", "https://")):
    shopify_domain = shopify_domain.split("//", 1)[1]
shopify_domain = shopify_domain.rstrip("/")

print(f"Using Shopify store URL: {shopify_domain}")
print(f"Admin API Token (first 5 chars): {SHOPIFY_ACCESS_TOKEN[:5] if SHOPIFY_ACCESS_TOKEN else 'Not provided'}...")
print(f"Storefront API Token (first 5 chars): {SHOPIFY_STOREFRONT_TOKEN[:5] if SHOPIFY_STOREFRONT_TOKEN else 'Not provided'}...")

# Initialize the ShopifyConnector with both tokens
shopify_connector = ShopifyConnector(shopify_domain, SHOPIFY_ACCESS_TOKEN, SHOPIFY_STOREFRONT_TOKEN)

# Test 1: Check which API headers are available
print("\nAPI Headers available:")
print(f"Admin API Headers: {'Yes' if shopify_connector.admin_headers else 'No'}")
print(f"Storefront API Headers: {'Yes' if shopify_connector.storefront_headers else 'No'}")

# Test 2: Search for products
print("\nTesting product search...")
search_term = "shirt"  # Change this to match products in your store
products = shopify_connector.search_products(search_term, limit=3)

if products:
    print(f"Found {len(products)} products matching '{search_term}':")
    for i, product in enumerate(products):
        print(f"\n  Product {i+1}: {product.get('title', 'No title')}")
        print(f"  ID: {product.get('id')}")
        
        # Print price information
        if product.get('price'):
            print(f"  Price: {product['price'].get('amount')} {product['price'].get('currency')}")
        
        # Print image URL
        if product.get('image_url'):
            print(f"  Image: {product['image_url']}")
        
        print(f"  URL: {product.get('url')}")
else:
    print("No products found or error occurred during search.")

# Test 3: Get product recommendations
print("\nTesting product recommendations...")
if products and len(products) > 0:
    product_id = products[0].get('id')
    print(f"Getting recommendations for product ID: {product_id}")
    
    recommendations = shopify_connector.get_product_recommendations(product_id, limit=2)
    
    if recommendations:
        print(f"Found {len(recommendations)} product recommendations:")
        for i, product in enumerate(recommendations):
            print(f"\n  Recommendation {i+1}: {product.get('title', 'No title')}")
            print(f"  ID: {product.get('id')}")
            
            # Print price information
            if product.get('price'):
                print(f"  Price: {product['price'].get('amount')} {product['price'].get('currency')}")
            
            # Print image URL
            if product.get('image_url'):
                print(f"  Image: {product['image_url']}")
            
            print(f"  URL: {product.get('url')}")
    else:
        print("No recommendations found or error occurred.")
else:
    print("Cannot test recommendations because no products were found in the search.")

print("\nTests completed!")

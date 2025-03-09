import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Shopify credentials from .env
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL", "")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN", "")

print("Original credentials:")
print(f"Store URL: {SHOPIFY_STORE_URL}")
print(f"Access Token (first 5 chars): {SHOPIFY_ACCESS_TOKEN[:5]}...")

# Clean up URL to get just the domain
shopify_domain = SHOPIFY_STORE_URL
if shopify_domain.startswith(("http://", "https://")):
    shopify_domain = shopify_domain.split("//", 1)[1]
shopify_domain = shopify_domain.rstrip("/")

print(f"\nProcessed domain: {shopify_domain}")

# Try different API endpoints
api_versions = ["2023-10", "2023-07", "2023-04", "2022-10"]
api_endpoints = []

# Add standard GraphQL endpoints
for version in api_versions:
    api_endpoints.append({
        "name": f"Standard GraphQL API (v{version})",
        "url": f"https://{shopify_domain}/api/{version}/graphql.json",
        "headers": {
            "Content-Type": "application/json",
            "X-Shopify-Storefront-Access-Token": SHOPIFY_ACCESS_TOKEN
        }
    })

# Add Admin API endpoint (if this is an admin token)
api_endpoints.append({
    "name": "Admin API",
    "url": f"https://{shopify_domain}/admin/api/2023-10/shop.json",
    "headers": {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
    }
})

# Simple GraphQL query to check store information
store_info_query = """
{
  shop {
    name
    description
  }
}
"""

# Simple query for just the name
simple_query = """
{
  shop {
    name
  }
}
"""

# Try each endpoint
success = False
for endpoint in api_endpoints:
    print(f"\n\nTesting endpoint: {endpoint['name']}")
    print(f"URL: {endpoint['url']}")
    
    # For GraphQL endpoints
    if "graphql" in endpoint['url']:
        try:
            response = requests.post(
                endpoint['url'],
                headers=endpoint['headers'],
                json={"query": simple_query},
                timeout=10
            )
            
            print(f"Status code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("Query successful!")
                print(json.dumps(data, indent=2))
                success = True
                print(f"\nSUCCESS! Use this endpoint configuration in your application.")
                print(f"URL: {endpoint['url']}")
                print(f"Headers: {endpoint['headers']}")
                break
            else:
                print("Error response:", response.text)
        except Exception as e:
            print(f"Error: {str(e)}")
    # For REST endpoints
    else:
        try:
            response = requests.get(
                endpoint['url'],
                headers=endpoint['headers'],
                timeout=10
            )
            
            print(f"Status code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("Query successful!")
                print(json.dumps(data, indent=2))
                success = True
                print(f"\nSUCCESS! Use this endpoint configuration in your application.")
                print(f"URL: {endpoint['url']}")
                print(f"Headers: {endpoint['headers']}")
                break
            else:
                print("Error response:", response.text)
        except Exception as e:
            print(f"Error: {str(e)}")

# If all tests failed, provide a summary of the issue
if not success:
    print("\n\nSUMMARY: Unable to connect to the Shopify API.")
    print("Please check your credentials and store URL, and ensure your store supports the API.")
    print("\nTROUBLESHOOTING STEPS:")
    print("1. Verify that your access token is correct and hasn't expired")
    print("2. Make sure the token has the necessary API scopes (permissions)")
    print("3. Check if the store URL is correct")
    print("4. Ensure the store has the API enabled")
    print("5. Check if this is a Storefront API token or an Admin API token")
    print("6. Try creating a new token in the Shopify admin")
    
    print("\nTo create a new Storefront API access token:")
    print("1. Log into your Shopify admin dashboard")
    print("2. Go to Settings > Apps and sales channels")
    print("3. Click on 'Develop apps' at the top right")
    print("4. Create a new app or select an existing one")
    print("5. Go to the 'API credentials' tab")
    print("6. Configure Storefront API scopes (enable necessary permissions)")
    print("7. Save and then get the Storefront API access token")
else:
    print("\nAt least one endpoint was successful! Update your application to use this configuration.")

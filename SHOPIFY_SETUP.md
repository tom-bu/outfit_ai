# Shopify API Setup Guide

This guide will help you set up the necessary Shopify API tokens for the outfit recommendation application.

## Setting up Storefront API Access Token

Since the Admin API requires specific scopes that may not be available, we'll use the Storefront API for product search and recommendations.

### Steps to create a Storefront API token:

1. **Log into Shopify Admin**
   - Go to your Shopify admin dashboard and log in with your credentials.

2. **Go to "Settings"**
   - In your Shopify admin, navigate to:
   - Settings > Apps and sales channels
   - Then, click on "Develop apps" at the top right of the page.

3. **Create a New Custom App**
   - Click the "Create an app" button in the top right corner.
   - A dialog will appear asking for the app name and a contact email.
   - Give the app a name (e.g., "Outfit AI Integration") and provide a valid email address.
   - Click "Create app".

4. **Configure API Access for the App**
   - After creating the app, you will be taken to the app's configuration page.
   - Click on "Configure Storefront API scopes" under the API credentials tab.
   - Enable the necessary permissions:
     - `unauthenticated_read_product_listings` (for accessing product information)
     - `unauthenticated_read_product_inventory` (for inventory data)
     - Any other scopes you might need for your specific use case
   - Click "Save".

5. **Get the Storefront API Access Token**
   - Go back to the API credentials tab in the app.
   - Scroll down to the Storefront API access token section.
   - Click "Install app" if prompted.
   - Click "Reveal token once" to view the access token.
   - **Important**: Store this token securely in your `.env` file as it won't be shown again.

## Update your .env file

Add the following to your `.env` file:

```
# Shopify API credentials
SHOPIFY_STORE_URL=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxx  # Admin API token (if available)
SHOPIFY_STOREFRONT_TOKEN=xxxxxxxxxxxxxxxxxxxx    # Storefront API token (required)
```

Replace the placeholder values with your actual Shopify store URL and API tokens.

## Testing the Integration

After setting up the tokens, run the test script to verify the integration:

```bash
python test_shopify_updated.py
```

This will test both the Admin API and Storefront API functionality to ensure that product search and recommendations work correctly.

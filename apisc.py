import requests

def fetch_product_details(prodID):
    # API endpoint with the specific product ID
    url = f"https://api.g2a.com/v1/products?id={prodID}"

    # Headers including the Authorization
    access_token = "ODDKYJRMMZUTYZLKNY0ZOTDMLTGXZTITZDU1YTY1N2JKZDG1"
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    

    # Sending GET request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Assuming the API returns JSON, parse the response
        product_details = response.json()
        print(product_details)
    else:
        print(f"Failed to fetch prod details. Status code: {response.status_code}, Message: {response.text}")

# Example usage with a specific product ID
prodID = '10000001741008'
fetch_product_details(prodID)

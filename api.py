import requests

def fetch_product_details(prodID):
    # API endpoint with the specific product ID
    url = f"https://sandboxapi.g2a.com/v1/products?id={prodID}"

    # Headers including the Authorization
    headers = {
        "Authorization": "qdaiciDiyMaTjxMt, 74026b3dc2c6db6a30a73e71cdb138b1e1b5eb7a97ced46689e2d28db1050875"
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
prodID = '10000000415008'
fetch_product_details(prodID)

import requests

def fetch_products_and_display_ids_quantities():
    # API endpoint
    url = "https://sandboxapi.g2a.com/v1/products?page=1&minQty=5"

    # Headers including the Authorization
    headers = {
        "Authorization": "qdaiciDiyMaTjxMt, 74026b3dc2c6db6a30a73e71cdb138b1e1b5eb7a97ced46689e2d28db1050875"
    }

    # Sending GET request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Assuming the API returns JSON, parse the response
        products_data = response.json()
        
        # Extracting and printing only the product IDs and their quantities
        for product in products_data.get('docs', []):
            product_id = product.get('id')
            qty = product.get('qty')
            print(f"Product ID: {product_id}, Quantity: {qty}")
    else:
        print(f"Failed to fetch products. Status code: {response.status_code}, Message: {response.text}")

# Call the function to execute it
fetch_products_and_display_ids_quantities()

import requests
import json

# The URL to your Odoo server and endpoint
url = 'https://microcodes.codebarre.ma/api/product_identif/'

# The token and identif to send with the request
data = {
    'token': '41835adc783b425c8f39368d3ec8317c',  # Replace with your token
    'identif': '19240'  # Replace with the identif you're looking for
}

# Making the POST request
response = requests.post(url, json=data)

# Print the status code and response data
print(f"Status Code: {response.status_code}")
print(f"Response Content: {response.content.decode()}")

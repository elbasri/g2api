import requests

url = 'https://microcodes.codebarre.ma/api/update_microcode'

data = {
    'token': '41835adc783b425c8f39368d3ec8317c',
    'identifiant': '19240',
    'quantity': 10,  # Nouvelle quantité
    'price': 20.5  # Nouveau prix
}

response = requests.post(url, json=data)

print(f"Status Code: {response.status_code}")
print(f"Response Content: {response.content.decode()}")

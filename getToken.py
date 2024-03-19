import requests

# Replace these with the actual values
client_id = "ayXSrdgLnJPsUGBR"
client_secret = "WRNHNJJxwWnqDdduCtnmiXKoHIXbHXdO"

url = "https://api.g2a.com/oauth/token"  # This URL is hypothetical; use the correct one from the documentation
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}
data = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret,
}

response = requests.post(url, headers=headers, data=data)

if response.status_code == 200:
    token_info = response.json()
    print(token_info)
    access_token = token_info["access_token"]
    print("Access Token:", access_token)
    # You can now use this access token to make API calls
else:
    print("Failed to obtain token. Status code:", response.status_code, "Message:", response.text)

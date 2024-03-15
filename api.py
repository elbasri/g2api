from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx


app = FastAPI()

# New CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
# Replace these with your actual credentials
CLIENT_ID = "qdaiciDiyMaTjxMt"
API_KEY = "74026b3dc2c6db6a30a73e71cdb138b1e1b5eb7a97ced46689e2d28db1050875"

@app.get("/product/{prodID}")
async def fetch_product_details(prodID: str):
    url = f"https://sandboxapi.g2a.com/v1/products?id={prodID}"
    headers = {
        "Authorization": f"{CLIENT_ID}, {API_KEY}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        product_details = response_data.get('docs', [{}])[0] # Assumes first item in docs or empty dict if none
        
        # Extract specific fields with checks for their existence
        details_to_return = {
            "qty": product_details.get('qty'),
            "minPrice": product_details.get('minPrice'),
            "retail_min_price": product_details.get('retail_min_price'),
            "retailMinBasePrice": product_details.get('retailMinBasePrice')
        }
        return details_to_return
    else:
        return {"error": f"Failed to fetch product details. Status code: {response.status_code}, Message: {response.text}"}

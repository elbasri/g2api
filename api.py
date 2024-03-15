from fastapi import FastAPI
import httpx

app = FastAPI()

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
        return response.json()
    else:
        return {"error": f"Failed to fetch product details. Status code: {response.status_code}, Message: {response.text}"}

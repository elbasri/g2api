from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime, timedelta
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# G2A credentials
CLIENT_ID = "ayXSrdgLnJPsUGBR"
CLIENT_SECRET = "WRNHNJJxwWnqDdduCtnmiXKoHIXbHXdO"
TOKEN_URL = "https://api.g2a.com/oauth/token"

# Token storage
token_info = {
    "access_token": None,
    "expires_at": datetime.now()
}

# Shared token for alternative API
ALTERNATIVE_API_TOKEN = '41835adc783b425c8f39368d3ec8317c'

# Endpoint URLs
ALTERNATIVE_API_URL = 'https://microcodes.codebarre.ma/api/product_identif/'
UPDATE_MICROCODES_URL = 'https://microcodes.codebarre.ma/api/update_microcode'

async def get_new_access_token():
    """Request a new access token from G2A API."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET
            }
        )
        response.raise_for_status()
        token_data = response.json()
        token_info["access_token"] = token_data["access_token"]
        token_info["expires_at"] = datetime.now() + timedelta(seconds=token_data["expires_in"])

async def fetch_g2a_product_details(identif_g2a: str):
    """Fetch product details from G2A API using the provided identif_g2a."""
    if datetime.now() >= token_info["expires_at"]:
        await get_new_access_token()

    headers = {"Authorization": f"Bearer {token_info['access_token']}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.g2a.com/v1/products?id={identif_g2a}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()

@app.get("/product/{prodID}")
async def fetch_product_details(prodID: str, request: Request):
    referer_url = request.headers.get('referer')
    if not referer_url:
        raise HTTPException(status_code=400, detail="Referer header is missing.")

    wp_update_url = f"{referer_url.rstrip('/')}/wp-json/custom/v1/update-product/"

    async with httpx.AsyncClient() as client:
        alt_response = await client.post(
            ALTERNATIVE_API_URL,
            json={'token': ALTERNATIVE_API_TOKEN, 'identif': prodID}
        )
        
        if alt_response.status_code == 200:
            alt_data_json = json.loads(alt_response.json()["result"])
            
            if "identifiant_g2a" not in alt_data_json or "quantity_available" not in alt_data_json:
                return {"message": "Required data not found in alternative API response."}
            
            qty = float(alt_data_json["quantity_available"])
            identif_g2a = alt_data_json["identifiant_g2a"]

            if qty > 0:
                return {"message": "Sufficient stock available, not querying G2A.com."}
            
            g2a_data = await fetch_g2a_product_details(identif_g2a)
            product_details = g2a_data.get('docs', [{}])[0]

            details_to_return = {
                "qty": product_details.get('qty'),
                "minPrice": product_details.get('minPrice'),
                "retail_min_price": product_details.get('retail_min_price'),
                "retailMinBasePrice": product_details.get('retailMinBasePrice'),
            }

            # Update microcodes and WooCommerce with new details from G2A
            await client.post(UPDATE_MICROCODES_URL, json={
                'token': ALTERNATIVE_API_TOKEN,
                'identifiant': identif_g2a,
                'quantity': details_to_return["qty"],
                'price': details_to_return["minPrice"],
            })

            await client.post(wp_update_url, json={
                "sku": prodID,
                "qty": details_to_return["qty"],
                "price": details_to_return["minPrice"],
                "token": "NCR123Tok",
            }, headers={'Content-Type': 'application/json'})

            return details_to_return
        else:
            raise HTTPException(status_code=404, detail="Alternative API response error.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

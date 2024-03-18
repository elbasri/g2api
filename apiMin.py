from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLIENT_ID = "qdaiciDiyMaTjxMt"
API_KEY = "74026b3dc2c6db6a30a73e71cdb138b1e1b5eb7a97ced46689e2d28db1050875"

@app.get("/product/{prodID}")
async def fetch_product_details(prodID: str, request: Request):
    referer_url = request.headers.get('referer')
    if not referer_url:
        raise HTTPException(status_code=400, detail="Referer header is missing")

    # Append your specific endpoint to the referer_url, assuming it's the base URL
    wp_update_url = f"{referer_url.rstrip('/')}/wp-json/custom/v1/update-product/"
    print(wp_update_url)
    
    url = f"https://sandboxapi.g2a.com/v1/products?id={prodID}"
    headers = {"Authorization": f"{CLIENT_ID}, {API_KEY}"}

    async with httpx.AsyncClient() as client:
        # Fetch product details from G2A
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            print(response_data)
            product_details = response_data.get('docs', [{}])[0]
            
            details_to_return = {
                "qty": product_details.get('qty'),
                "minPrice": product_details.get('minPrice'),
                "retail_min_price": product_details.get('retail_min_price'),
                "retailMinBasePrice": product_details.get('retailMinBasePrice')
            }

            # Update WordPress/WooCommerce product details using the referer URL
            wp_response = await client.post(wp_update_url, json={
                #"sku": prodID,
                "sku": 22238,
                "qty": details_to_return["qty"],
                "price": details_to_return["minPrice"],
                "token": "NCR123Tok",
            }, headers={'Content-Type': 'application/json'})
            print(wp_response)
            if wp_response.status_code != 200:
                # Optionally handle error
                pass

            return details_to_return
        else:
            raise HTTPException(status_code=404, detail="Product not found")

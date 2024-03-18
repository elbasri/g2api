from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLIENT_ID = "ibHtsEljmCxjOFAn"
API_KEY = "HrsPmuOlWjqBMHnQWIgfchUqBTBYcRph"

@app.get("/product/{prodID}")
async def fetch_product_details(prodID: str, request: Request):
    referer_url = request.headers.get('referer')
    if not referer_url:
        raise HTTPException(status_code=400, detail="Referer header is missing.")

    wp_update_url = f"{referer_url.rstrip('/')}/wp-json/custom/v1/update-product/"
    alternative_api_url = 'https://microcodes.codebarre.ma/api/product_identif/'
    update_microcodes_url = 'https://microcodes.codebarre.ma/api/update_microcode'
    token = '41835adc783b425c8f39368d3ec8317c'
    

    async with httpx.AsyncClient() as client:
        alt_response = await client.post(alternative_api_url, json={'token': token, 'identif': prodID})
        
        if alt_response.status_code == 200:
            alt_data_json = json.loads(alt_response.json()["result"])
            
            if "identifiant_g2a" not in alt_data_json or "quantity_available" not in alt_data_json:
                return {"message": "Required data not found in alternative API response."}
            
            qty = float(alt_data_json["quantity_available"])
            identif_g2a = alt_data_json["identifiant_g2a"]

            print(prodID)
            print(identif_g2a)

            if qty > 0:
                return {"message": "Sufficient stock available, not querying G2A.com."}
            identif_g2a = 10000039390002
            print(identif_g2a)
            g2a_response = await client.get(f"https://api.g2a.com/v1/products?id={identif_g2a}", headers={"Authorization": f"{CLIENT_ID}, {API_KEY}"})
            print(g2a_response)
            if g2a_response.status_code == 200:
                g2a_data = g2a_response.json()
                print(g2a_response)
                if g2a_data.get('docs') and len(g2a_data.get('docs')) > 0:
                    product_details = g2a_data['docs'][0]
                    print(g2a_data)
                    product_details = g2a_data.get('docs', [{}])[0]

                    details_to_return = {
                        "qty": product_details.get('qty'),
                        "minPrice": product_details.get('minPrice'),
                        "retail_min_price": product_details.get('retail_min_price'),
                        "retailMinBasePrice": product_details.get('retailMinBasePrice'),
                    }

                    # Update microcodes and WooCommerce with new details from G2A
                    await client.post(update_microcodes_url, json={
                        'token': token,
                        'identifiant': identif_g2a,
                        'quantity': details_to_return["qty"],
                        'price': details_to_return["minPrice"],
                    })

                    await client.post(wp_update_url, json={
                        "sku": prodID,  # Use original prodID for WooCommerce update
                        "qty": details_to_return["qty"],
                        "price": details_to_return["minPrice"],
                        "token": "NCR123Tok",
                    }, headers={'Content-Type': 'application/json'})

                    return details_to_return
                else:
                    raise HTTPException(status_code=404, detail="Product not found or no details available in G2A.com")
            else:
                raise HTTPException(status_code=404, detail="Product not found in G2A.com")
        else:
            raise HTTPException(status_code=404, detail="Alternative API response error.")

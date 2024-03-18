jQuery(document).ready(function($) {
    function parseJsonLdAndGetSku() {
        const jsonLdScripts = $('script[type="application/ld+json"]');
        
        for (let i = 0; i < jsonLdScripts.length; i++) {
            try {
                const jsonLd = JSON.parse(jsonLdScripts.eq(i).html());
                const productData = jsonLd["@graph"].find(item => item['@type'] === 'Product');
                if (productData && productData.sku) {
                    return productData.sku;
                }
            } catch (error) {
                console.error('Error parsing JSON-LD script content:', error);
            }
        }
        return null; 
    }

    const productSku = parseJsonLdAndGetSku();
    
    console.log("Product SKU:", productSku);

    if (productSku) {
        $('.wpb_wrapper').prepend('<div class="loading-overlay"><div class="spinner"></div></div>');
        console.log("Product SKU is present in JSON-LD.");
        fetchProductDetails(productSku);
    } else {
        console.log("Product SKU is not present in JSON-LD.");
    }
    console.log("the script file is executed");

    async function fetchProductDetails(sku) {
        console.log("fetchProductDetails is executed");
        //const url = `https://g2.codebarre.ma/product/${sku}`;
        const url = `http://127.0.0.1:8080/product/${sku}`;
        try {
            const response = await fetch(url, { method: 'GET' });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();

            const stockStatus = $('.stock');
            const isInitiallyOutOfStock = stockStatus.length === 0 || stockStatus.hasClass('out-of-stock');

            if (data.qty && !isNaN(data.qty) && data.qty > 0) {
                if (isInitiallyOutOfStock) {
                    const formHtml = `
                        <form class="cart" action="${document.location.href}" method="post" enctype="multipart/form-data">
                            <div class="quantity">
                                <input type="button" value="-" class="minus">
                                <label class="screen-reader-text" for="quantity_${sku}">quantité de ${document.title}</label>
                                <input type="number" id="quantity_${sku}" class="input-text qty text" value="1" min="1" max="${data.qty}" name="quantity" step="1" inputmode="numeric">
                                <input type="button" value="+" class="plus">
                            </div>
                            <button type="submit" name="add-to-cart" value="product_id_here" class="single_add_to_cart_button button alt">Ajouter au panier</button>
                            <button id="wd-add-to-cart" type="submit" name="wd-add-to-cart" value="product_id_here" class="wd-buy-now-btn button alt">Buy now</button>
                        </form>
                    `;

                    $('.wd-single-price').after(formHtml);
                    
                    stockStatus.removeClass('out-of-stock').addClass('in-stock').text(`${data.qty} en stock`);
                } else {
                    stockStatus.text(`${data.qty} en stock`);
                    $('.quantity .input-text.qty.text').attr('max', data.qty.toString());
                }
            }

            if (data.retail_min_price && !isNaN(data.retail_min_price)) {
                $('.wd-single-price .price .woocommerce-Price-amount').html(`<bdi>${data.retail_min_price}&nbsp;<span class="woocommerce-Price-currencySymbol">DH</span></bdi>`);
            }

        } catch (error) {
            console.error("Failed to fetch product details:", error);
        } finally {
            $('.loading-overlay').remove();
            //console.error("finally");
        }
    }
});

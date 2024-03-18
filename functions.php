

function custom_enqueue_product_script() {
    if (is_product()) { // Only on product pages
        wp_enqueue_script('custom-product-api', get_template_directory_uri() . '/js/custom-product-api.js', array('jquery'), null, true);
		//echo get_template_directory_uri();
    }
	//alert("tttttt");
}
add_action('wp_enqueue_scripts', 'custom_enqueue_product_script');

add_action('rest_api_init', function () {
    register_rest_route('custom/v1', '/update-product/', array(
        'methods' => 'POST',
        'callback' => 'update_product_details',
        'permission_callback' => 'custom_api_permissions_check'
    ));
});


function custom_log_to_file($message) {
    $log_file = ABSPATH . 'custom_wp_log.log'; // ABSPATH is the WordPress root directory
    $current_time = current_time('Y-m-d H:i:s');
    $log_message = "{$current_time} - {$message}\n";
    file_put_contents($log_file, $log_message, FILE_APPEND | LOCK_EX);
}




function custom_api_permissions_check($request) {
    $token = $request->get_param('token');
    if ('NCR123Tok' === $token) {
        error_log('Custom API: Token validation succeeded.');
        return true; // Permission granted
    }
    error_log('Custom API: Token validation failed.');
    return new WP_Error('rest_forbidden', esc_html__('You cannot update product details.', 'my-text-domain'), array('status' => 401));
}

function update_product_details($request) {
    $sku = $request->get_param('sku');
    $qty = $request->get_param('qty');
    $price = $request->get_param('price');

    // Log incoming request
    custom_log_to_file("Incoming update request: SKU={$sku}, Qty={$qty}, Price={$price}");

    $args = array(
        'post_type' => 'product',
        'meta_key' => '_sku',
        'meta_value' => $sku,
        'posts_per_page' => 1,
    );
    $posts = get_posts($args);

    if (empty($posts)) {
        custom_log_to_file("Product not found for SKU={$sku}");
        return new WP_Error('rest_product_not_found', esc_html__('Product not found.', 'my-text-domain'), array('status' => 404));
    }

    $product_id = $posts[0]->ID;
    $product = wc_get_product($product_id);
    if (!$product) {
        custom_log_to_file("WC_Product object not found for Product ID={$product_id}");
        return new WP_Error('rest_product_not_found', esc_html__('Product not found.', 'my-text-domain'), array('status' => 404));
    }

    // Update product stock quantity and price
    $product->set_stock_quantity($qty);
    $product->set_price($price);
    $product->set_regular_price($price); // If you also want to update the regular price
    $product->save();

    // Log successful update
    custom_log_to_file("Product updated successfully: Product ID={$product_id}, SKU={$sku}, New Qty={$qty}, New Price={$price}");

    return rest_ensure_response(array(
        'message' => 'Product updated successfully',
        'product_id' => $product_id,
        'sku' => $sku,
        'qty' => $qty,
        'price' => $price,
    ));
}
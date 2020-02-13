const $form = document.getElementById('search-product-sku');

$form.addEventListener('submit', (event) => {
    event.preventDefault();
    const sku = document.getElementById('product-sku').value;
    const url = `${window.location.origin}/products/api/sku/${sku}`
    response = sendData({}, url, false, new_page)
    if (response.ok) {
    }
})

const new_page = ({data}) => window.open(data.data.provider_url, '_blank');
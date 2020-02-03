const $form = document.getElementById('formMLV');

$form.addEventListener('submit', (event) => {
    event.preventDefault();
    
    const MLV = document.getElementById('valueMLV').value;
    const url = `${window.location.origin}/products/api/mlv/${MLV}`
    response = sendData({}, url, false, false)
    if (response.ok) {
        window.open(data.data.provider_url, '_blank');
    }
})


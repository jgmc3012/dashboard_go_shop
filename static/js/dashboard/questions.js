const $form = document.getElementById('formMLV');

$form.addEventListener('submit', (event) => {
    event.preventDefault();
    toggleLoading()

    const MLV = document.getElementById('valueMLV').value;
    const url = `${window.location.origin}/products/api/mlv/${MLV}`

    fetch(url)
    .then( response => response.json())
    .then( data => {
        toggleLoading()
        if (data.ok) {
            window.open(data.data.provider_url, '_blank');
        } else {
            const HTMLString = alertInfoHTML(data.msg, 'danger', 'Error')
            insertElement('#InfoMsg', HTMLString)
        }
    })
})

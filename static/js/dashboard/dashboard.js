alertInfoHTML = (message, type, mtype) => `
<div class="alert alert-${type} fade in alert-dismissible show">
    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true" style="font-size:20px">×</span>
    </button>
    <strong>${mtype}</strong>   ${message}
</div>
`
function createTemplate(HTMLString) {
    const html = document.implementation.createHTMLDocument();
    html.body.innerHTML = HTMLString;
    return html.body.children[0];
}

function insertElement(Selectorcontaner, HTMLString) {
    let container = document.querySelector(Selectorcontaner)
    container.children[0].remove();
    element = createTemplate(HTMLString);
    container.append(element)
}

function sendData(data, url, selectorModal) {
    toggleLoading()
    const method = 'POST'
    const headers = {
        "X-CSRFToken": getCookie('csrftoken'),
        'Content-Type': 'application/json',
        "X-Requested-With": "XMLHttpRequest",
    }
    const body = JSON.stringify(data)

    const modal = document.querySelector(selectorModal)
    modal.click()
    fetch(url,{method,headers,body})
    .then( response => response.json())
    .then( data => {
        toggleLoading()
        const type = data.ok ? 'success':'danger'
        const mtype = data.ok ? 'Buen Trabajo':'Error'
        const HTMLString = alertInfoHTML(data.msg, type, mtype)
        insertElement('#InfoMsg', HTMLString)
        if (data.ok) {
            itemlistElement = document.querySelector(`[order_id='${orderId}']`)
            itemlistElement.remove()
        }
    })
}

function getJsonFromForm(selector) {
    elements = document.querySelectorAll(selector)
    data = {}
    elements.forEach( element => {
        key = element.getAttribute('name')
        value = element.value
        data[key] = value
    } )
    return data
} 

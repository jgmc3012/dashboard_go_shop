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
    if (container.children.length > 0) {
        container.children[0].remove();
        insertElement(Selectorcontaner, HTMLString)
    } else if (HTMLString) {
        element = createTemplate(HTMLString);
        container.append(element)
    }
}

function appendElement(Selectorcontaner, HTMLString) {
    let container = document.querySelector(Selectorcontaner)
    element = createTemplate(HTMLString);
    container.append(element)
}

function sendData(data, url, selectorModal, callback, kwargs={}, show_response=true) {
    toggleLoading()
    const method = 'POST'
    const headers = {
        "X-CSRFToken": getCookie('csrftoken'),
        'Content-Type': 'application/json',
        "X-Requested-With": "XMLHttpRequest",
    }
    const body = JSON.stringify(data)
    if (selectorModal) {
        const modal = document.querySelector(selectorModal)
        modal.click()
    }
    fetch(url,{method,headers,body})
    .then( response => response.json())
    .then( data => {
        toggleLoading()
        const type = data.ok ? 'success':'danger'
        const mtype = data.ok ? 'Buen Trabajo':'Error'
        if (show_response | (!data.ok)){
            const HTMLString = alertInfoHTML(data.msg, type, mtype)
            insertElement('#InfoMsg', HTMLString)
        }
        if (data.ok) {
            kwargs['data'] = data
            callback(kwargs)
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

function clearForm(selector) {
    elements = document.querySelectorAll(selector)
    elements.forEach( element => {
        element.value = ''
    } )
} 

const hideOrder = (kwargs) => {
    const { data, orderId } = kwargs
    if (data.ok) {
        itemlistElement = document.querySelector(`[order_id='${orderId}']`)
        itemlistElement.remove()
    }
}

const show_total_questions = () => {
    const url = `${window.location.origin}/questions/api/total`
    fetch(url)
    .then( response => response.json())
    .then( data => {
        $cardQuestion = document.getElementById('card-questions')
        $cardQuestion.innerText = data.data.total_questions
    })
}

show_total_questions()
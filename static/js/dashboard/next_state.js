const formNextState = (state, orderId ) => {
    switch (state+1) {
        case 1:
            return (`
            <div>
                <div class="modal-body" id='bodyModalState'>
                    <form>
                        <div class="input-group mb-3">
                            <div class="input-group-prepend">
                            <span class="input-group-text">Referencia de Pago</span>
                            </div>
                            <input type="text" class="form-control" api='nextState' name='pay_reference' placeholder="Ejem: 73192731">
                        </div>
                        <div class="input-group mb-3">
                            <div class="input-group-prepend">
                            <span class="input-group-text">Cantidad de Articulos</span>
                            </div>
                            <input type="number" class="form-control" api='nextState' name='quantity' value="1">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <div class="btn btn-primary" state='${state}' orderId='${orderId}' id='btnRequestNextState' >Enviar</div>
                    <button class="btn btn-secondary" type="button" data-dismiss="modal">Cancelar</button>
                </div>
            </div>
            `)
        case 2: 
            return (`
            <div>
                <div class="modal-body" id='bodyModalState'>
                    <form>
                        <div class="input-group mb-3">
                            <div class="input-group-prepend">
                            <span class="input-group-text">N° de Orden de Compra</span>
                            </div>
                            <input type="text" class="form-control" api='nextState' name="provider_order" placeholder="1234">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                <div class="btn btn-primary" state='${state}' orderId='${orderId}' id='btnRequestNextState' >Enviar</div>
                    <button class="btn btn-secondary" type="button" data-dismiss="modal">Cancelar</button>
                </div>
            </div>
            `)
        case 3:
            sendData(state, orderId)
            break
        case 4:
            window.location = `${window.location}/shipping_packages`
            break
        case 5:
            window.location = `${window.location}/received_package`
            break
        case 6:
            sendData(state, orderId)
            break
    }
}

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

function sendData(state, orderId) {
    const method = 'POST'
    const headers = {
        "X-CSRFToken": getCookie('csrftoken'),
        'Content-Type': 'application/json',
        "X-Requested-With": "XMLHttpRequest",
    }
    const body = JSON.stringify(getJsonFromForm("[api='nextState']"))
    let url
    switch (state + 1) {
        case 1:
            url = `${window.location.origin}/orders/api/new_pay/${orderId}`
            break;
        case 2:
            url = `${window.location.origin}/orders/api/buys/done/${orderId}`
            break;
        case 3:
            url = `${window.location.origin}/orders/api/provider_deliveries/${orderId}`
            break;
        case 6:
            url = `${window.location.origin}/orders/api/complete_order/${orderId}`
            break;
    }

    const modal = document.getElementById('stateModal')
    modal.click()
    fetch(url,{method,headers,body})
    .then( response => response.json())
    .then( data => {
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

// BEGIN

btnsNextState = document.querySelectorAll('[data-target="#stateModal"]')

btnsNextState.forEach( (btn) => {
    btn.addEventListener('click', (event) => {
        let orderId = event.target.getAttribute('id')
        let state = parseInt(parseInt(event.target.getAttribute('state')))
        const HTMLString = formNextState(state,orderId)
        if (HTMLString) {
            insertElement('#formContainer', HTMLString)
    
            btnRequest = document.getElementById('btnRequestNextState')
            btnRequest.addEventListener( 'click' , (event) => {
                state = parseInt(event.target.getAttribute('state'))
                orderId = event.target.getAttribute('orderId')
                sendData(state ,orderId)
            })
        }
    })
})


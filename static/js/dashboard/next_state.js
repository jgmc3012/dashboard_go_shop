const formsNextStates = (state, orderId ) => {
    switch (state+1) {
        case 1: return (`
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
        case 2: return (`
            <div class="modal-body" id='bodyModalState'>
                <form>
                    <div class="input-group mb-3">
                        <div class="input-group-prepend">
                        <span class="input-group-text">N° de Orden de Compra</span>
                        </div>
                        <input type="text" class="form-control" placeholder="1234">
                    </div>
                </form>
            </div>
            <div class="modal-footer">
            <div class="btn btn-primary" state='${state}' orderId='${orderId}'>Enviar</div>
            <button class="btn btn-secondary" type="button" data-dismiss="modal">Cancelar</button>
            </div>
        `)
        case 3: console.log('Recibido en Bodega')
            break
        case 4: return (`
            <div class="modal-body" id='bodyModalState'>
                <form>
                    <div class="input-group mb-3">
                        <div class="input-group-prepend">
                        <span class="input-group-text">Referencia de Pago</span>
                        </div>
                        <input type="text" class="form-control" placeholder="123456789">
                    </div>
                </form>
            </div>
            <div class="modal-footer">
            <a class="btn btn-primary" href="">Enviar</a>
            <button class="btn btn-secondary" type="button" data-dismiss="modal">Cancelar</button>
            </div>
        `)
        case 5: console.log('Recibido en Oficina')
            break
        case 6: console.log('Orden Completada')
            break
    }

}

function createTemplate(HTMLString) {
    const html = document.implementation.createHTMLDocument();
    html.body.innerHTML = HTMLString;
    return html.body.children[0];
    }

btnsNextState = document.querySelectorAll('[data-target="#stateModal"]')

function insertElement(Selectorcontaner, HTMLString) {
    let container = document.querySelector(Selectorcontaner)
    container.children[0].remove();
    element = createTemplate(HTMLString);
    container.append(element)
}

btnsNextState.forEach( (btn) => {
    btn.addEventListener('click', (event) => {
        let orderId = event.target.getAttribute('id')
        let state = parseInt(parseInt(event.target.getAttribute('state')))
        const HTMLString = formsNextStates(state,orderId)
        insertElement('#formContainer', HTMLString)

        btnRequest = document.getElementById('btnRequestNextState')
        btnRequest.addEventListener( 'click' , (event) => {
            nextstate = parseInt(event.target.getAttribute('state')) + 1
            orderId = event.target.getAttribute('orderId')
            sendData(orderId)
        })
    })
})

function sendData(orderId) {
    url = `${window.location.origin}/orders/api/new_pay/${orderId}`
    method = 'POST'
    headers = {
        "X-CSRFToken": getCookie('csrftoken'),
        'Content-Type': 'application/json',
        "X-Requested-With": "XMLHttpRequest",
    }
    body = JSON.stringify(getJsonFromForm("[api='nextState']"))
    fetch(url,{method,headers,body})
    .then( response => response.json())
    .then( data => {
        modal = document.getElementById('stateModal')
        modal.click()
        type = data.ok ? 'success':'danger'
        mtype = data.ok ? 'Buen Trabajo':'Error'
        HTMLString = alertInfoHTML(data.msg, type, mtype)
        insertElement('#InfoMsg', HTMLString)
    } )
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

alertInfoHTML = (message, type, mtype) => `
<div class="alert alert-${type} fade in alert-dismissible show">
    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true" style="font-size:20px">×</span>
    </button>
    <strong>${mtype}</strong>   ${message}
</div>
`
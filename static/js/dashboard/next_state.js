function selectUrl(state, orderId) {
    switch (state + 1) {
        case 1:
            return `${window.location.origin}/orders/api/new_pay/${orderId}`
            break
        case 2:
            return `${window.location.origin}/orders/api/buys/done/${orderId}`
            break
        case 3:
            return `${window.location.origin}/orders/api/provider_deliveries/${orderId}`
            break
        case 6:
            return `${window.location.origin}/orders/api/complete_order/${orderId}`
            break
    }
}

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
            sendData({}, selectUrl(state, orderId), '#stateModal', hideOrder, {orderId})
            break
        case 4:
            window.location = `${window.location.origin}/dashboard/shipping_packages`
            break
        case 5:
            window.location = `${window.location.origin}/dashboard/received_package`
            break
        case 6: 
            sendData({}, selectUrl(state, orderId), '#stateModal', hideOrder, {orderId})
            break
    }
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
                let url = selectUrl(state, orderId)
                let data = getJsonFromForm("[api='nextState']")
                sendData(data ,url, '#stateModal', hideOrder, {orderId})
            })
        }
    })
})
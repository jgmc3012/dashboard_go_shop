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
        case 5:
            return `${window.location.origin}/orders/api/received_package/${orderId}`
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
            sendData({}, selectUrl(state, orderId), '#stateModal', hideOrder, {orderId})
            break
        case 6: 
            sendData({}, selectUrl(state, orderId), '#stateModal', hideOrder, {orderId})
            break
    }
}
// BEGIN

btnsNextState = document.querySelectorAll("[api='modalNextState']")
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

// CANCEL ORDER

const cancel_template = orderId => (`
<div>
    <form id="formCancelOrder" method="post">
        <div class="modal-body" id='bodyModalState'>
            <div class="form-group">
            <label for="reasons">Motivo de la cancelacion:</label>
            <select class="form-control" id="reasons" name="reason" api='cancelOrder'>
                <option value="0">Nos quedamos sin stock</option>
                <option value="1">No pudimos contactar al comprador</option>
                <option value="2">El cliente no tenia el dinero suficiente para la compra</option>
                <option value="3">El cliente se arrepintio de la compra</option>
            </select>
            <div>
                <label class="radio-inline">
                    <input type="radio" name="rating" value="-1" api='cancelOrder'>Negativo
                </label>
                <label class="radio-inline">
                    <input type="radio" name="rating" value="0" api='cancelOrder' checked>Neutro
                </label>
                <label class="radio-inline">
                    <input type="radio" name="rating" value="1" api='cancelOrder'>Positivo
                </label>
            </div>

            <div class="form-group">
                <label for="mesage">Mensaje:</label>
                <textarea class="form-control" rows="5" name="message" required api='cancelOrder'></textarea>
            </div>

            </div>
            <input id="orderId" name="orderId" type="hidden" value="${orderId}" api='cancelOrder'>
        </div>
        <div class="modal-footer">
            <input class="btn btn-danger" type="submit" id='btnRequestCancelOrder' value='Cancelar Orden'></input>
            <div class="btn btn-secondary" data-dismiss="modal">Salir</div>
        </div>
    </form>
</div>
`)

btnsCancelOrder = document.querySelectorAll("[api='modalCancelOrder']")
btnsCancelOrder.forEach( (btn) => {
    btn.addEventListener('click', (event) => {
        let orderId = event.target.getAttribute('id')
        const HTMLString = cancel_template(orderId)
        insertElement('#formContainer', HTMLString)

        formRequest = document.getElementById('formCancelOrder')
        formRequest.addEventListener( 'submit' , (event) => {
            event.preventDefault()
            let url = `${window.location.origin}/orders/api/cancel`
            let data = getJsonFromForm("[api='cancelOrder']")
            sendData(data ,url, '#stateModal', hideOrder, {orderId})
        })
    })
})
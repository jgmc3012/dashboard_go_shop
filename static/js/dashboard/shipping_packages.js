let shippingOrders = {}
const products_items = document.querySelectorAll('[api="product-item"]')

products_items.forEach( element => element.addEventListener('click', ( event => {
    target = event.currentTarget
    target.classList.toggle('list-group-item-primary')
    orderId = target.getAttribute('order_id')
    orderTitle = target.getAttribute('title')
    if (shippingOrders[orderId]){
        delete((shippingOrders[orderId]))
    } else {
        shippingOrders[orderId] = {'id':orderId, 'title':orderTitle}
    }
})))

formTemplate = () => {
    tableStr = ''
    for (let key in shippingOrders) {
        tableStr += `
        <tr>
            <td>${key}</td>
            <td>${shippingOrders[key].title}</td>
        </tr>`
    }
    return (`
<div>
    <div class="modal-body" id='bodyModalState'>
        <form>
            <div class="input-group mb-3">
                <div class="input-group-prepend">
                    <span class="input-group-text">Costo de Envio: Bs</span>
                </div>
                <input type="number" class="form-control" api='shipping' name='amount'>
            </div>
            <div class="input-group mb-3">
                <div class="input-group-prepend">
                    <span class="input-group-text">Numero de Guia</span>
                </div>
                <input type="number" class="form-control" api='shipping' name='guide_shipping'>
            </div>
            <table class="table table-hover">
                <thead>
                <tr>
                    <th>N° Orden</th>
                    <th>Titulo</th>
                </tr>
                </thead>
                <tbody>
                ${tableStr}
                </tbody>
            </table>
        </form>
    </div>
    <div class="modal-footer">
        <div class="btn btn-primary" id='btnRequestNextState' >Enviar</div>
        <button class="btn btn-secondary" type="button" data-dismiss="modal">Cancelar</button>
    </div>
</div>
`)
}

btnShowModal = document.querySelector('[data-target="#shippingModal"]')

btnShowModal.addEventListener('click', (event) => {
    const HTMLString = formTemplate()
    if (HTMLString) {
        insertElement('#formContainer', HTMLString)

        btnRequest = document.getElementById('btnRequestNextState')
        btnRequest.addEventListener( 'click' , (event) => {
            data = getJsonFromForm("[api='shipping']")
            orders = Array()
            for (key in shippingOrders) {
                orders.push(key)
            }
            data['orders'] = orders
            url = `${window.location.origin}/orders/api/shipping_package`
            sendData(data, url, '#shippingModal', hideOrder, {orderId})
        })
    }
})
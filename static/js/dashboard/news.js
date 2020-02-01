const newTemplate = (userName, dateTime, message) => (`
    <div class="row p-2">
        <div class="col-1">
            <img class="img-profile rounded-circle" src="https://source.unsplash.com/QAB-WJcbgJk/60x60">
        </div>
        <div class="col-11">
            <div>
                <strong>${userName}</strong>
                <span>${dateTime}</span>
            </div>
            <div>
                <p>${message}</p>
            </div>
        </div>
    </div>
`)

const inputNewTemplate = (orderId) => (`
    <div>
        <form id="formNews-${orderId}">
            <input type="hidden" name="orderId" api='data-news' value="${orderId}">
            <div class="p-2 d-flex  align-content-center align-items-center">
                <div class="form-group col-11 mb-0">
                    <textarea class="form-control" rows="2" name="message" api='data-news'></textarea>
                </div> 
                <div class="col-1">
                    <button class="btn btn-primary" type="submit">
                        Enviar<i class="fas fa-paper-plane fa-sm"></i>
                    </button>            
                </div>
            </div>
        </form>
    </div>
`)

const displayNews = (news, orderId) => {
    insertElement(`#containerNews-${orderId}`, false)
    news.forEach((comment) => {
        appendElement(`#containerNews-${orderId}`, newTemplate(comment.user, comment.datetime, comment.message))
    })
    appendElement(`#containerNews-${orderId}`, inputNewTemplate(orderId))

    const formNews = document.querySelector(`#formNews-${orderId}`)
    formNews.addEventListener('submit', (event) => {
        event.preventDefault();
        data = getJsonFromForm(`#formNews-${orderId} [api='data-news']`)
    
        url = `${window.location.origin}/orders/api/news/create`
        sendData(data, url, false, console.log)
    })
}

// BEGIN
const $buttonsShowNews = document.querySelectorAll("[api='show_news']")

$buttonsShowNews.forEach( btn => {
    btn.addEventListener('click', (event) => {
        let orderId = event.target.getAttribute('order')
        showNews = event.target.getAttribute('show-news')
        if (!showNews) {
            url = `${window.location.origin}/orders/api/news/show`
            sendData(
                {orderId},
                url,
                false,
                (kwargs) => {
                    const {data, orderId} = kwargs
                    displayNews(data.data.news, orderId)
                    event.target.setAttribute('show-news', '1')
                },
                {orderId},
                false
            )
        } else {
            event.target.setAttribute('show-news', '0')
            insertElement(`#containerNews-${orderId}`, '<div></div>')
        }
    })
})


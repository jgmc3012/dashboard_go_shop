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
        <form api="formNew">
            <input type="hidden" name="orderId" api='data-news' value="${orderId}">
            <div class="p-2 d-flex  align-content-center align-items-center">
                <div class="form-group col-11 mb-0">
                    <textarea class="form-control" rows="4" name="message" api='data-news'></textarea>
                </div> 
                <div class="col-1">
                    <button class="btn btn-primary" type="button">
                        Enviar<i class="fas fa-paper-plane fa-sm"></i>
                    </button>            
                </div>
            </div>
        </form>
    </div>
`)

let news = [
    {
    'datetime' : '2020/01/25 12:00',
    'user': 'Jesus Millan',
    'message': 'Keep up the GREAT work! I am cheering for you!! Lorem ipsum dolor sit amet.'
    },
    {
        'datetime' : '2020/01/26 09:00',
        'user': 'Jesus Millan',
        'message': 'Keep up the GREAT work! I am cheering for you!! Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Keep up the GREAT work! I am cheering for you!! Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Keep up the GREAT work! I am cheering for you!! Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Keep up the GREAT work! I am cheering for you!! Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Keep up the GREAT work! I am cheering for you!! Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Keep up the GREAT work! I am cheering for you!! Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Keep up the GREAT work! I am cheering for you!! Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Keep up the GREAT work! I am cheering for you!! Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    },
    {
        'datetime' : '2020/01/26 15:00',
        'user': 'Jesus Millan',
        'message': 'Keep up the GREAT work! I am cheering for you!! Lorem ipsum dolor sit amet.Keep up the GREAT work! I am cheering for you!! Lorem ipsum dolor sit amet.Keep up the GREAT work! I am cheering for you!! Lorem ipsum dolor sit amet.Keep up the GREAT work! I am cheering for you!! Lorem ipsum dolor sit amet.Keep up the GREAT work! I am cheering for you!! Lorem ipsum dolor sit amet.Keep up the GREAT work! I am cheering for you!! Lorem ipsum dolor sit amet.'
    },
]

const submitNew = (event) => {
    event.preventDefault();
    data = getJsonFromForm("[api='formNew'] [api='data-news']")

    url = `${window.location.origin}/orders/api/news/create`
    sendData(data, url, false)
}

const displayNews = (news, orderId) => {
    insertElement(`#containerNews-${orderId}`, false)
    news.forEach((comment) => {
        appendElement(`#containerNews-${orderId}`, newTemplate(comment.user, comment.datetime, comment.message))
    })
    appendElement(``, inputNewTemplate(orderId))

    const formNews = document.querySelector(`#containerNews-${orderId} [api='formNew']`)

    formNews.addEventListener('submit', submitNew)
}

// BEGIN
const $buttonsShowNews = document.querySelectorAll("[api='show_news']")

$buttonsShowNews.forEach( btn => {
    btn.addEventListener('click', (event) => {
        showNews = event.target.getAttribute('show-news')
        if (!showNews) {
            let orderId = event.target.getAttribute('order')
            url = `${window.location.origin}/orders/api/news/show`
            
            response = sendData({orderId}, url, false)
            if (response.ok) {
                displayNews(response.data.news, orderId)
                event.target.setAttribute('show-news', '1')
            }
        } else {
            event.target.setAttribute('show-news', '0')
            insertElement(`#containerNews-${orderId}`, false)
        }
    })
})
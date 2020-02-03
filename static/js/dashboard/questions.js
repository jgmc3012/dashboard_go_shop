const $formsAnswers = document.querySelectorAll('[api="formAnswer"]')

$formsAnswers.forEach( form => form.addEventListener('submit', event => {
    event.preventDefault()
    questionId = event.target.getAttribute('question')
    data = getJsonFromForm(`#containerAnwers-${questionId} [api="data-answer-${questionId}"]`)
    const url = `${window.location.origin}/questions/api/answer`
    sendData(data, url, false, removeQuestion, {questionId})
}))

const removeQuestion = (kwargs) => {
    const {questionId} = kwargs

    const $question = document.getElementById(`question-${questionId}`)
    $question.remove()
}
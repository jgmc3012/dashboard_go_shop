from django.shortcuts import render
from django.utils.timezone import make_aware
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from store.views import get_or_create_buyer
from store.products.models import Product
from questions.models import Question, Answer
from django.http import JsonResponse
from store.store import Store
import json

#class QuestionsView():

def new_question(question_draw):
    question_id = int(question_draw['id'])
    question = Question.objects.filter(id=question_id)
    exist = True if question else False
    if exist:
        return question, exist

    date_created = make_aware(datetime.strptime(
        question_draw['date_created'].split('.')[0],
        '%Y-%m-%dT%H:%M:%S'
    ))

    buyer = get_or_create_buyer(int(question_draw['from']['id']))
    product = Product.objects.get(sku=question_draw['item_id'])

    question = Question.objects.create(
        id=question_id,
        buyer=buyer,
        text=question_draw['text'],
        date_created=date_created,
        product=product
    )

    return question, exist

@login_required
def send_answer(request):
    json_data=json.loads(request.body)
    question_id = json_data['questionId']
    text = json_data['answer']
    question = Question.objects.filter(id=question_id).first()

    if not question:
        return JsonResponse({
            'ok': False,
            'msg': 'Pregunta no encontrada. Concante con el desarrollador.'
        })

    response = new_answer(text, question, request.user)

    return response

def new_answer(text, question, user):
    store = Store()
    path = '/answers'

    body = {
        'question_id': question.id,
        'text': text,
    }

    res = store.post(path, body, auth=True)

    if res.get('error'):
        return JsonResponse({
            'ok': False,
            'msg': f'{res.get("error")}:{res.get("message")}'
        })

    Answer.objects.create(
        user=user,
        text=text,
        question= question,
        created_date=timezone.localtime()
    )

    return JsonResponse({
        'ok': True,
        'msg': 'Respuesta Creada correctamente',
    })

@login_required
def outwith_answer(request):
    questions = Question.objects.filter(answer=None).count()

    return JsonResponse({
        'ok': True,
        'msg': '',
        'data': {
            'total_questions': questions
        }
    })
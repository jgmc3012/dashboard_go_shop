from django.shortcuts import render
from django.utils.timezone import make_aware
from datetime import datetime

from store.views import get_or_create_buyer
from store.products.models import Product
from questions.models import Question

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
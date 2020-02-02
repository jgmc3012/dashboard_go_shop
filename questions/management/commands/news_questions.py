from django.core.management.base import BaseCommand, CommandError

from questions.views import new_question
from questions.models import Question
from store.store import Store
import logging
from decouple import config

class Command(BaseCommand):
    help = 'Deshabilitar produtos que continene malas Palabras'

    def handle(self, *args, **options):
        seller_id=config('MELI_ME_ID')
        store = Store(seller_id=seller_id)

        path = '/questions/search'
        params = {
            'seller_id':seller_id,
            'status':'UNANSWERED',
            'offset':0,
        }
        questions_api = store.get(path, params)

        total = questions_api['total']
        limit = questions_api['limit']

        questions_draw = questions_api['questions']

        params = [{
            'seller_id':seller_id,
            'status':'UNANSWERED',
            'offset':offset,
            'attributes':'questions'
        }for offset in range(limit,total,limit)]

        for questions_api in store.map_pool_get([path]*len(params), params):
            questions_draw += questions_api['questions']

        questions_draw = questions_draw[::-1]

        count=0
        for question_draw in questions_draw:
            question,exist =  new_question(question_draw)
            if exist:
                break
            else:
                logging.info(f'Nueva Pregunta de {question.buyer.id}:{question.buyer.nickname} en \
{question.product.title} a las {question.date_created.strftime("%H:%M:%S")}')        
                count +=1

        logging.info(f'Nuevas Preguntas: {count}. Sin responder: {total}')
from django.urls import path

from .views import send_answer, outwith_answer

urlpatterns = [
    # path('api/questions', show_questions, name='questions.questions'),
    path('api/answer', send_answer, name='questions.send_answer'),
    path('api/total', outwith_answer, name='questions.total'),
]
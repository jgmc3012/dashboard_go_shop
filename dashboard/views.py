from django.shortcuts import render

def index(request):
    return render(request,'dashboard/adviser.html', {
        'contex_title':'Centro de Ventas'
    })

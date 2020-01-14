from django.shortcuts import redirect

def redirect_view(request):
    response = redirect('/dashboard')
    return response
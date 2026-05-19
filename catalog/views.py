from django.shortcuts import render

# Create your views here.

# Логика для главной страницы
def home_view(request):
    return render(request, 'catalog/home.html')

# Логика для контактов
def contacts_view(request):
    return render(request, 'catalog/contacts.html')

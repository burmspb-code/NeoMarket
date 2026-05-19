from django.shortcuts import render
from django.contrib import messages


# Логика для главной страницы
def home_view(request):
    return render(request, 'catalog/home.html')

# Логика для контактов с формой обратной связи
def contacts_view(request):
    if request.method == 'POST':
        # Получаем данные из полей формы
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        
        # Создаем всплывающее уведомление об успехе
        messages.success(request, 'Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.')
        
    return render(request, 'catalog/contacts.html')

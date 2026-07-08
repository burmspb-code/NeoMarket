from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Главная страница
    # path("", TemplateView.as_view(template_name="catalog/empty.html"), name="home"), # Выводит пустой шаблон «из коробки
    path("", include("catalog.urls", namespace="catalog")),
    # Страница для администрирования
    path("admin/", admin.site.urls),
    # Страница интернет магазина
    path("blog/", include("blog.urls", namespace="blog")),
    # Страница библиотеки книг
    path("library/", include("library.urls", namespace="library")),
    # Страница регистрации пользователей
    path("users/", include("users.urls", namespace="users")),
]

# Настройка для раздачи медиафайлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

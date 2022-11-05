from django.utils import timezone


def year(request):
    """Добавляет в контекст переменную year"""
    return {
        'year': timezone.now().year,
    }

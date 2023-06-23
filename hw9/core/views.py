from django.shortcuts import render


def handler404(request, exception):
    context = {
        'title': 'Page not found',
        'error': f'Not found {request.path}'
    }
    return render(request, 'error.html', context=context, status=404)


def handler403(request, exception):
    context = {
        'title': 'Forbidden',
        'error': str(exception)
    }
    return render(request, 'error.html', context=context, status=403)


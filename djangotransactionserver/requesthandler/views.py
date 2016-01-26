from django.http import HttpResponse


def index(request):
    return render(request, 'requesthandler/templates/index.html', {})
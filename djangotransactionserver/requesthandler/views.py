from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from django.http import HttpResponse

@csrf_exempt
def index(request):
    print 'sup'
    if request.method == 'GET':
        return render(request, 'requesthandler/index.html', {})
    elif request.method == 'POST':
        response = HttpResponse()
        response.status_code = 200
        print request.body
        return response
    else:
        print "invalid request received"
        return render(request, 'requesthandler/index.html', {})


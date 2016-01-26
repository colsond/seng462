
from requesthandler import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
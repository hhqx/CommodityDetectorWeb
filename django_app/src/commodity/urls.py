from django.urls import path
from django.urls import path, re_path


app_name = 'commodity'

from . import main
urlpatterns = [
    # The home page
    path('index_old', main.inputForm, name='home'),
    path('index_old/<CMD>', main.inputForm, name='index_cmd'),
]

from . import views
urlpatterns += [
    path('index', views.index, name='index'),
    path('<int:page>', views.page, name='page'),
    path('<int:page>/calculate', views.calculate, name='calculate'),
    path('upload', views.upload, name='upload'),
    path('upload/calculate', views.upload_calculate, name='upload_calculate'),
]

# reverse('commodity:author-detail', kwargs={'pk': self.pk})
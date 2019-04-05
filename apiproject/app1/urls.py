from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from app1 import views

urlpatterns = patterns('app1.views',
    url(r'^api_root/$', 'api_root'),
    url(r'^user/register/$', views.RegisterUser.as_view(), name="register-user"),
    url(r'^user/login/$', views.UserLogin.as_view(), name="login"),

)

urlpatterns = format_suffix_patterns(urlpatterns)

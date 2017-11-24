from django.conf.urls import url
from .views import register_page, home_page, UserDetailsView

urlpatterns = [
    url(r'^register/$', register_page, name='user_registeration_page'),
    url(r'^home/$', home_page, name='home_page'),
    url(r'^(?P<user_id>[0-9]+)/$', UserDetailsView.as_view(), name='user_details_view'),
]

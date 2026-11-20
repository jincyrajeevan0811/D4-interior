from django.urls import path

from . import views

app_name = "inquiries"

urlpatterns = [
    path("get-a-quote/", views.quote, name="quote"),
    path("get-a-quote/sent/", views.thanks, name="thanks"),
    path("contact/", views.contact, name="contact"),
]

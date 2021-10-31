from django.urls import include
from django.conf.urls import url
from rest_framework import routers
from .views import RegisterViewset, UserView, forgot_password, reset_password


router = routers.SimpleRouter()
router.register(r"register", RegisterViewset, basename="register")

urlpatterns = [
    url(r"^", include(router.urls)),
    url(
        "helpers/forgot_password/",
        forgot_password,
        name="forgot-password",
    ),
    url("helpers/reset_password/", reset_password, name="reset-password"),
    url(r"^user/", UserView.as_view(), name="user"),
]

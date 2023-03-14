
from django.urls import path
from crudapp import views

urlpatterns = [
    path('registration/',views.Registration.as_view()),
    path('registration/<token>/',views.Registration.as_view()),
    path('user_login/',views.user_login.as_view()),
    path("reset_password/",views.Reset_pass.as_view()),
    path('CrudData/',views.CrudData.as_view()),
    

    # path('user_login/',views.user_login.as_view()),
    # path("Update_data/",views.Update_data.as_view()),
    # path("Update_data_patch/",views.Update_data_patch.as_view()),
    # path('Delete_data/',views.Delete_data.as_view()),
    # path("logout_user/",views.logout_user.as_view()),
    # path("forget_password/",views.forget_pass.as_view()),
]
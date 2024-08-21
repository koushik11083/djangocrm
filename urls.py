from django.urls import path
from . import views

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('post/', views.create_problem, name='post'),
    path('update/<int:pk>/', views.update_problem, name='update_problem'),
    path('all/', views.all_problems, name='all_problems'),
    path('user/<int:id>/', views.user_page, name='user_page'),
    path('notifications/', views.notifications, name='notifications'),
    path('problem/<int:pk>/', views.view_problem, name='view_problem'),
]


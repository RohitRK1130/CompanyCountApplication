from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('upload/', views.upload_file_page, name='upload_file_page'),
    path('user-management/', views.user_management, name='user_management'),
    path('query-builder/', views.query_builder_page, name='query_builder_page'),

    # Endpoint to fetch the list of users
    path('api/fetch_users/', views.fetch_users, name='fetch-users'),

    # Endpoint to create a new user
    path('api/create_user/', views.create_user, name='create-user'),

    # Endpoint to delete a user
    path('api/delete_user/<int:user_id>/', views.delete_user, name='delete-user'),

    # Endpoint to upload a file
    path('api/upload/', views.handle_file_upload, name='upload_file'),
    
    path('api/query/', views.query, name='query'),

    path('api/query-builder-data/', views.query_builder_data, name='query_builder_data'),

    path('api/get-states/', views.get_states, name='get_states'),
    path('api/get-cities/', views.get_cities, name='get_cities'),

]

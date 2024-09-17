# urls.py
from django.urls import path
from .views import (
    signup, 
    login, 
    search_users, 
    send_friend_request, 
    respond_friend_request
)

urlpatterns = [
    
    path('signup/', signup, name='signup'),        
    path('login/', login, name='login'),           

   
    path('send-friend-request/', send_friend_request, name='send_friend_request'),  
    path('respond-friend-request/<int:request_id>/', respond_friend_request, name='respond_friend_request'),  
    path('search/', search_users, name='search_users'), ]

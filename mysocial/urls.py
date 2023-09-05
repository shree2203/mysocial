from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from social import views
urlpatterns=[
                path("", views.index, name="index"),
                path('api/login/', views.login_view, name='login_view'),
                path('admin/', admin.site.urls),
                path('api/user-profile/<str:username>/', views.get_user_data, name='user-profile'),
                path('api/signup/', views.signup, name='signup'),
                path('api/get_all_user/', views.get_all_user, name='get_all_user'),
                path('signup/', views.signup, name='signup'),
                path('login/', views.login_view, name='login'),
                path('create_post/', views.create_post, name='create_post'),
                path('logout/', views.logout_user, name='logout'),
                path('uploadData/<str:username>/', views.upload_profile_image, name='upload_profile_image'),
                path('createProfile/<str:username>/', views.create_profile, name='create_profile'),
                path('api/createProfile/', views.create_profile, name='create_profile'),
                path('displayProfile/', views.display_profile, name='display_profile'),
                path('api/display-profile/', views.display_profile, name='display_profile'),
                path('startPost/', views.start_post, name='startPost'),
                path('userPost/<int:user_id>/', views.all_user_posts, name='userPost'),
                path('display_posts/<int:user_id>/', views.display_posts, name='display_posts'),
                path('display_posts/', views.display_posts, name='display_posts'),
                path('unfriend/<str:username>/', views.unfriend, name='unfriend'),
                path('userPost/', views.all_user_posts, name='userPost'),
                path('friends_list/', views.friends_list, name='friends_list'),
                path('sent_request/', views.count_friend_requests_sent, name='sent_request'),
                path('reject_friend_request/<int:request_id>/', views.reject_friend_request,
                     name='reject_friend_request'),
                path('accept_friend_request/<int:request_id>/', views.accept_friend_request,
                     name='accept_friend_request'),
                path('friend_requests/', views.received_friend_requests, name='friend_requests'),
                path('send_friend_request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
                path('any_profile_view/<int:user_id>/', views.any_profile_view, name='any_profile_view')
            ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


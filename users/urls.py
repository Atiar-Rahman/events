from django.urls import path
from users.views import sign_up,sign_in,user_logout,activate_user,admin_dashboard,assign_role,change_password,profile_edit,create_group,group_list,ProfileView,CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView
urlpatterns=[
   path('sign-up/',sign_up,name='sign-up'),
   path('sign-in/',sign_in,name='sign-in'),
   path('logout/',user_logout,name='logout'),
   path('activate/<int:user_id>/<str:token>/',activate_user),
   path('admin/dashboard/',admin_dashboard,name='admin-dashboard'),
   path('admin/<int:user_id>/assign-role/',assign_role,name='assign-role'),
   path('admin/create-group/',create_group,name='create-group'),
   path('admin/groups/', group_list, name='group-list'),
   path('profile/', ProfileView.as_view(), name='profile'),
   path('profile/edit/', profile_edit, name='edit_profile'),
   path('profile/change-password/', change_password, name='change_password'),
   path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
   path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
   path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
   path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

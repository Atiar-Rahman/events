from django.shortcuts import render,redirect,HttpResponse
from django.urls import reverse_lazy
from users.forms import RegisterForm,LoginForm,AssignRoleForm,CreateGroupForm,EditProfileForm
from django.contrib.auth import login,logout
from django.contrib import messages
from django.contrib.auth.models import User,Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.generic import TemplateView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


# Create your views here.

def is_admin(user):
    return user.groups.filter(name='admin').exists()

def sign_up(request):
   form = RegisterForm()
   if request.method=='POST':
       form=RegisterForm(request.POST)
       if form.is_valid():
           user = form.save(commit=False)
           user.set_password(form.cleaned_data.get('password1'))
           user.is_active = False
           user.save()
           messages.success(request,'A confirmation mail sent. check your email')
           return redirect('sign-in')
          
   return render(request,'users/register.html',{'form':form})


def sign_in(request):
   form = LoginForm()
   if request.method=='POST':
       form = LoginForm(data=request.POST)
       if form.is_valid():
            user = form.get_user()
            login(request,user)
            return redirect('dashboard_redirect')
   return render(request,'users/login.html',{'form':form})

@login_required
def user_logout(request):
   if request.method=='POST':
       logout(request)
       return redirect('sign-in')


def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('sign-in')
        else:
            return HttpResponse('Invalid id and token')
    except User.DoesNotExist:
        return HttpResponse('user does not exist')


@user_passes_test(is_admin,login_url='no-permession')
def admin_dashboard(request):
    users = User.objects.all()
    return render(request,'admin/dashboard.html',{'users':users})

@user_passes_test(is_admin,login_url='no-permession')
def assign_role(request, user_id):
    user = User.objects.get(id=user_id)
    form = AssignRoleForm()

    if request.method == 'POST':
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            user.groups.clear()
            user.groups.add(role)
            messages.success(request, f'{user.username} has been assigned to the {role.name}')
            return redirect('admin-dashboard')

    return render(request, 'admin/assign_role.html', {'form': form, 'user': user})


@user_passes_test(is_admin,login_url='no-permession')
def create_group(request):
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group '{group.name}' has been created successfully")
            return redirect('create-group')  # or to 'group-list', etc.
    return render(request, 'admin/creategroup.html', {'form': form})

@user_passes_test(is_admin,login_url='no-permession')
def group_list(request):
    groups = Group.objects.all()

    return render(request,'admin/group_list.html',{'groups':groups})




class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['username'] = user.username
        context['email'] = user.email
        context['name'] = user.get_full_name()

        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login
        return context
    


@login_required
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # make sure this is your profile view name
    else:
        form = EditProfileForm(instance=user)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})




@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # important to prevent logout
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'accounts/change_password.html', {'form': form})

from django.contrib.auth.views import PasswordResetCompleteView,PasswordResetConfirmView,PasswordResetDoneView,PasswordResetView
class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'
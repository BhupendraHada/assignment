from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.utils.translation import ugettext as _
from django.utils.http import is_safe_url
from django.shortcuts import resolve_url
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse_lazy
from .forms import RegistrationForm, User
from .tasks import send_verification_email
from assignment import settings
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.views import APIView
from braces.views import CsrfExemptMixin
from .user_serializer import UserSerializer


def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse_lazy('home_page'))

    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():
            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())
            redirect_to = reverse_lazy('home_page')

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
        'site_header':'User Profile',
        'site_title': 'User Profile',
        'title': 'Login'
    }
    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app

    return TemplateResponse(request, template_name, context)


def logout(request, next_page=None,
           template_name='main_page.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           current_app=None, extra_context=None):
    """
    Logs out the user and displays 'You are logged out' message.
    """
    auth_logout(request)


    if next_page is not None:
        next_page = resolve_url(next_page)

    if (redirect_field_name in request.POST or
            redirect_field_name in request.GET):
        next_page = request.POST.get(redirect_field_name,
                                     request.GET.get(redirect_field_name))
        # Security check -- don't allow redirection to a different host.
        if not is_safe_url(url=next_page, host=request.get_host()):
            next_page = request.path

    if next_page:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect(next_page)

    current_site = get_current_site(request)
    context = {
        'site': current_site,
        'site_name': current_site.name,
        'title': _('Logged out'),
        'site_header':'User Profile',
        'site_title': 'User Profile',
        'path': '/login', # not working
        'index_path': '/login', # not working
    }
    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app
    return TemplateResponse(request, template_name, context)


def home_page(request):
    return render(request, 'main_page.html', {"user": request.user})

@csrf_exempt
def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                form.check_username()
                form.password_validation()
            except Exception as e:
                print e.__str__()
                return render(request, 'registration/register.html', {'form': form})

            user = User.objects.create(username=form.cleaned_data['username'], password=make_password(form.cleaned_data['password'], None, 'md5'),
                                       email=form.cleaned_data['email'], first_name=form.cleaned_data['firstname'],
                                       last_name=form.cleaned_data['lastname'])
            send_verification_email(user.id, ["demouser@gmail.com"])
            return HttpResponseRedirect(reverse_lazy('login_page'))
    form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


class UserDetailsView(CsrfExemptMixin, APIView):
    """
        User Details View
    """

    def get(self, request, user_id):
        key = request.META.get('HTTP_X_API_KEY', '')
        if not key:
            content = {'message': "Unauthorized Access, Required key to access."}
            return Response(content, status=http_status.HTTP_412_PRECONDITION_FAILED)

        user_obj = User.objects.filter(id=user_id)
        if user_obj:
            user_details = user_obj.values("username", "first_name", "last_name", "email")
            return Response(user_details)
        else:
            content = {'search data': 'User object matching query does not exists.'}
            return Response(content, status=http_status.HTTP_404_NOT_FOUND)

    def put(self, request, user_id):
        try:
            key = request.META.get('HTTP_X_API_KEY', '')
            if not key:
                content = {'message': "Unauthorized Access, Required key to access."}
                return Response(content, status=http_status.HTTP_412_PRECONDITION_FAILED)

            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                input_data = serializer.data.get('inputData')
                user_obj = User.objects.filter(id=user_id)
                if user_obj:
                    data = {"username": input_data.get('username'), "first_name": input_data.get('first_name'),
                                    "last_name": input_data.get('last_name')}
                    user_obj.update(**data)

                    return Response("User Details update successfully.")
                else:
                    content = {'search data': 'User object matching query does not exists.'}
                    return Response(content, status=http_status.HTTP_404_NOT_FOUND)
            else:
                return Response(serializer.errors)
        except Exception as e:
            import sys
            print "UserDetailView Api put method exception: ", e.__str__(), sys.exc_traceback.tb_lineno
            return Response('Something went wrong.')


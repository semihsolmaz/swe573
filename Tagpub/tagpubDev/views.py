from django.shortcuts import render, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from tagpubDev.forms import ApplicationRegistrationForm
from tagpubDev.models import RegistrationApplication, UserProfileInfo, User, Article, Author
# Create your views here.


def index(request):
    if request.method == 'POST':
        results_list = Article.objects.filter(PMID__startswith='3394')
        results_dict = {"results_list": results_list}
        return render(request, 'tagpubDev/searchResults.html', context=results_dict)
    else:
        return render(request, 'tagpubDev/index.html')


def registration(request):
    if request.method == 'POST':
        registration_form = ApplicationRegistrationForm(data=request.POST)
        if registration_form.is_valid():
            if RegistrationApplication.objects.filter(email=request.POST['email']).filter(applicationStatus='1').exists():
                return HttpResponse('application under review')

            else:
                registration_application = registration_form.save()
                return HttpResponse('applications received')
        else:
            print(registration_form.errors)
    else:
        registration_form = ApplicationRegistrationForm()

    return render(request, 'tagpubDev/registration.html',
                  {'registration_form': registration_form})


# todo: create password and send email
def registrationRequests(request):
    if request.method == 'POST':
        approved_request = RegistrationApplication.objects.get(pk=request.POST['request_id'])
        approved_request.applicationStatus = '2'
        approved_request.save()
        user = User(username=approved_request.email,
                    first_name=approved_request.name,
                    last_name=approved_request.surname,
                    email=approved_request.email,
                    password='TestPwd123')
        user.set_password(user.password)
        user.save()
        user_profile = UserProfileInfo(registrationApplication_id=approved_request.id, user_id=user.id)
        user_profile.save()

    requests_list = RegistrationApplication.objects.filter(applicationStatus='1').order_by('applicationDate')
    requests_dict = {"registration_requests": requests_list}
    return render(request, 'tagpubDev/registrationRequests.html', context=requests_dict)


def userLogin(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('tagpubDev:index'))
            else:
                return HttpResponse("Your account is not active.")
        else:
            print("login failed username: {} and password: {}".format(username,password))
            return HttpResponse("Invalid login details")

    else:
        return render(request, 'tagpubDev/login.html', {})


@login_required
def userLogout(request):
    logout(request)
    return HttpResponseRedirect(reverse('tagpubDev:index'))


def articleDetail(request, pk):
    article = Article.objects.get(pk=pk)
    if request.method == 'POST':
        # todo: add tag
        pass
    else:
        authors = Author.objects.filter(article=article)
        article_dict = {"authors": authors,
                        "title": article.Title,
                        "abstract": article.Abstract,
                        "pmid": article.PMID
                        }
        return render(request, 'tagpubDev/articleDetail.html', context=article_dict)


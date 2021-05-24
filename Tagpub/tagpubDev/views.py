from functools import reduce
from dal import autocomplete
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from tagpubDev.forms import ApplicationRegistrationForm, TagForm
from tagpubDev.models import RegistrationApplication, UserProfileInfo, User, Article, Author, Tag, Keyword
from tagpubDev.wikiManager import getLabelSuggestion, WikiEntry
from django.db.models import F


# todo normalize ranking for tag and article search results before union and order results after union
def index(request):
    if request.method == 'POST':
        search_terms = [SearchQuery(term, ) for term in request.POST.get('searchTerms').split(",")]
        search_query = reduce(lambda x, y: x & y, search_terms)
        article_search_results = Article.objects.\
            filter(SearchIndex=search_query).\
            annotate(rank=SearchRank(F('SearchIndex'), search_query))
        tag_search_results = Article.objects.\
            filter(Tags__SearchIndex=search_query).\
            annotate(rank=SearchRank(F('SearchIndex'), search_query))
        results_list = (tag_search_results | article_search_results).distinct().order_by('-rank')
        # results_list = (article_search_results | tag_search_results).distinct().order_by('-rank')
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
        if 'add_tag' in request.POST:
            tag_form = TagForm(data=request.POST)
            if tag_form.data['wikiLabel']:
                tag_data = WikiEntry(tag_form.data['wikiLabel'])
                tag, created = Tag.objects.get_or_create(WikiID=tag_data.getID(), Label=tag_data.getLabel())
                if created:
                    tag.Description = tag_data.getDescription()
                    tag.Tokens = tag_data.getTokens()
                    tag.save()
                    tag.createTSvector()
                    article.Tags.add(tag)
                else:
                    article.Tags.add(tag)
        elif 'tag_id' in request.POST:
            tag = Tag.objects.get(pk=request.POST['tag_id'])
            print(request.POST['tag_id'])
            article.Tags.remove(tag)

    tag_form = TagForm()
    authors = Author.objects.filter(article=article)
    keywords = Keyword.objects.filter(article=article)
    keywords_list = ', '.join([item.KeywordText for item in keywords])
    tags = Tag.objects.filter(article=article)
    article_dict = {"authors": authors,
                    "title": article.Title,
                    "abstract": article.Abstract,
                    "pmid": article.PMID,
                    "tag_form": tag_form,
                    "keywords": keywords_list,
                    "tags": tags
                    }

    return render(request, 'tagpubDev/articleDetail.html', context=article_dict)


def tag_autocomplete(request):
    if request.is_ajax():
        # wiki_query = request.GET.get('tag_query', '')
        tags = ['kamil', 'kazım', 'manda']
        data = {
            'tags': tags,
        }
    return JsonResponse(data)


class TagAutocomplete(autocomplete.Select2ListView):

    def get_list(self):
        taglist = getLabelSuggestion(self.q)
        return taglist


def tagsList(request):
    if request.method == 'POST':
        tag_form = TagForm(data=request.POST)
        print(tag_form.data['wikiLabel'])
        if tag_form.data['wikiLabel']:
            return HttpResponse(tag_form.data['wikiLabel'])
    else:
        tag_list = Tag.objects.all()

    return render(request, 'tagpubDev/tagList.html',
                  {'tag_list': tag_list})

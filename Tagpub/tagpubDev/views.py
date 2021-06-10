from functools import reduce
from dal import autocomplete
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchQuery, SearchRank
from tagpubDev.forms import ApplicationRegistrationForm, TagForm
from tagpubDev.models import RegistrationApplication, UserProfileInfo, User, Article, Author, Tag, Keyword
from tagpubDev.wikiManager import getLabelSuggestion, WikiEntry
from django.db.models import F, CharField, Value, Sum, Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


# todo normalize ranking for tag and article search results before union and order results after union
def index(request):
    if request.method == 'POST':
        search_terms = [SearchQuery(term, search_type='phrase') for term in request.POST.get('searchTerms').split(",")]
        article_search_query = reduce(lambda x, y: x & y, search_terms)
        # todo: Change tag search logic to search for each term and get intersection results
        tag_search_query = reduce(lambda x, y: x | y, search_terms)
        # todo: Normalize tag and article result rank values
        # article_search_results = Article.objects.\
        #     filter(SearchIndex=article_search_query).\
        #     annotate(rank=SearchRank(F('SearchIndex'), article_search_query))
        #
        # # rel_tags = Tag.objects.filter(SearchIndex=tag_search_query).values_list('article', flat=True)
        #
        # print(list(article_search_results.values_list('rank', flat=True)))
        # tag_search_results = Article.objects.\
        #     filter(Tags__SearchIndex=tag_search_query).\
        #     annotate(rank=SearchRank(F('Tags__SearchIndex'), tag_search_query))
        # todo: Don't union, do group by instead and process annotations
        # results_list = (tag_search_results | article_search_results).order_by('-rank')
        # results_list = article_search_results.union(tag_search_results).values('id', 'Title', 'PublicationDate')\
        #     .annotate(rank_sum=Sum('rank')).order_by('-rank_sum')

        results = Article.objects.\
            filter(Q(SearchIndex=article_search_query) | Q(Tags__SearchIndex=tag_search_query))

        results_list = results.values('id', 'PMID', 'Title', 'PublicationDate').distinct().\
            annotate(a_rank=SearchRank(F('SearchIndex'), article_search_query)).\
            annotate(t_rank=SearchRank(F('Tags__SearchIndex'), tag_search_query)).\
            annotate(rank=(F('a_rank') + F('t_rank'))).values('id', 'Title', 'PublicationDate').\
            annotate(a_rank=Sum('a_rank'), t_rank=Sum('t_rank'), rank=Sum('rank')).\
            order_by(F('rank').desc(nulls_last=True), F('t_rank').desc(nulls_last=True), F('a_rank').desc(nulls_last=True))

        page = request.POST.get('page', 1)
        paginator = Paginator(results_list, 25)
        search_str = request.POST.get('searchTerms')
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
        # results_list = (article_search_results | tag_search_results).distinct().order_by('-rank')
        results_dict = {"results_list": results,
                        "search_term": search_str
                        }
        return render(request, 'tagpubDev/searchResults.html', context=results_dict)
    else:
        if request.GET.get('page', False):
            page = request.GET.get('page')
            search_terms = [SearchQuery(term, ) for term in request.GET.get('term').split(",")]
            article_search_query = reduce(lambda x, y: x & y, search_terms)
            tag_search_query = reduce(lambda x, y: x | y, search_terms)
            article_search_results = Article.objects. \
                filter(SearchIndex=article_search_query). \
                annotate(rank=SearchRank(F('SearchIndex'), article_search_query))
            tag_search_results = Article.objects. \
                filter(Tags__SearchIndex=tag_search_query). \
                annotate(rank=SearchRank(F('SearchIndex'), tag_search_query))
            results_list = (tag_search_results | article_search_results).distinct().order_by('-rank')
            paginator = Paginator(results_list, 25)
            search_str = request.GET.get('term')
            try:
                results = paginator.page(page)
            except PageNotAnInteger:
                results = paginator.page(1)
            except EmptyPage:
                results = paginator.page(paginator.num_pages)
            # results_list = (article_search_results | tag_search_results).distinct().order_by('-rank')
            results_dict = {"results_list": results,
                            "search_term": search_str
                            }
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
                registration_form.save()
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
            print("login failed username: {} and password: {}".format(username, password))
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


class TagAutocomplete(autocomplete.Select2ListView):

    def get_list(self):
        taglist = getLabelSuggestion(self.q)
        return taglist


def tagsList(request):

    tag_list = Tag.objects.all()

    return render(request, 'tagpubDev/tagList.html',
                  {'tag_list': tag_list})

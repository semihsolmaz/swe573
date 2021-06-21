from dal import autocomplete
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from tagpubDev.forms import ApplicationRegistrationForm, TagForm
from tagpubDev.models import RegistrationApplication, UserProfileInfo, User, Article, Author, Tag, Keyword
from tagpubDev.utils.wikiManager import getLabelSuggestion, WikiEntry
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from tagpubDev.utils.data import SearchResult


def index(request):
    if request.method == 'POST':
        search_terms = request.POST.get('searchTerms').split(",")

        search = SearchResult(search_terms)
        results_list = search.getSearchResults()

        page = request.POST.get('page', 1)
        paginator = Paginator(results_list, 25)
        search_str = request.POST.get('searchTerms')
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        date_data = search.getYearlyArticleCounts()

        results_dict = {"results_list": results,
                        "search_term": search_str,
                        "date_labels": date_data.keys(),
                        "data_values": date_data.values()
                        }
        return render(request, 'tagpubDev/searchResults.html', context=results_dict)
    else:
        if request.GET.get('page', False):
            page = request.GET.get('page')
            search_terms = request.GET.get('term').split(",")

            results_list = SearchResult(search_terms).getSearchResults()

            paginator = Paginator(results_list, 25)
            search_str = request.GET.get('term')
            try:
                results = paginator.page(page)
            except PageNotAnInteger:
                results = paginator.page(1)
            except EmptyPage:
                results = paginator.page(paginator.num_pages)
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


@login_required
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
def userList(request):
    if request.method == 'POST':
        if 'user_id' in request.POST:
            removed_user = User.objects.get(pk=request.POST['user_id'])
            removed_user.is_active = False
            removed_user.save()
        elif 'admin_status' in request.POST:
            admin_user = User.objects.get(pk=request.POST['admin_status'])
            admin_user.userprofileinfo.adminStatus = not admin_user.userprofileinfo.adminStatus
            admin_user.userprofileinfo.save()

    users = User.objects.filter(is_active=True)
    cur_username = request.user.username
    admin_status = User.objects.filter(username=cur_username).values_list('userprofileinfo__adminStatus')
    print(admin_status[0][0])
    return render(request, 'tagpubDev/userList.html', {'user_list': users, 'admin': admin_status[0][0]})


def userProfile(request):
    if request.method == 'POST':
        username = request.user.username
        password = request.POST.get('password')
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()

    return render(request, 'tagpubDev/userProfile.html', {})


@login_required
def userLogout(request):
    logout(request)
    return HttpResponseRedirect(reverse('tagpubDev:userLogin'))

@login_required
def articleDetail(request, pk):
    article = Article.objects.get(pk=pk)
    wiki_info = {}
    if request.method == 'POST':
        if 'get_tag' in request.POST:
            tag_form = TagForm(data=request.POST)
            tag_data = WikiEntry(tag_form.data['wikiLabel'])
            wiki_info['qid'] = tag_data.getID()
            wiki_info['label'] = tag_data.getLabel()
            wiki_info['description'] = tag_data.getDescription()
            wiki_info['existing_tags'] = Tag.objects.filter(WikiID=tag_data.getID())
        elif 'add_tag' in request.POST:
            tag_data = WikiEntry(request.POST['qid'])
            tag, created = Tag.objects.get_or_create(WikiID=tag_data.getID(), Label=tag_data.getLabel(), TagName=request.POST['tag_name'])
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

    article_dict.update(wiki_info)

    return render(request, 'tagpubDev/articleDetail.html', context=article_dict)


class TagAutocomplete(autocomplete.Select2ListView):

    def get_list(self):
        taglist = getLabelSuggestion(self.q)
        return taglist

@login_required
def tagsList(request):

    tag_list = Tag.objects.all()

    return render(request, 'tagpubDev/tagList.html',
                  {'tag_list': tag_list})

from django.shortcuts import render,redirect,Http404,get_object_or_404,reverse,get_list_or_404
from django.core.mail import mail_admins
from django.db.models import Q
from django.contrib import auth
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes,force_text
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from .decorators import private_snippet
from .forms import *
from .models import *
from .utils import paginate_result
import datetime
# Create your views here.
def userprofile(request,username):
    user=get_object_or_404(User,username=username)
    if user.profile.private and request.user.username!=user.username:
        raise Http404
    elif not user.profile.private and request.user.username!=user.username:
        snippet_list=user.snippet_set.filter(exposure='public')
        user.profile.views+=1
        user.profile.save()
    else:
        snippet_list=user.snippet_set.all()
    snippets=paginate_result(request,snippet_list,5)
    return render(request,'codeviewer/profile.html',{'user':user,'snippets':snippets})
def search(request):
    f = SearchForm(request.GET)
    snippets = []

    if f.is_valid():

        query = f.cleaned_data.get('query')
        mysnippets = f.cleaned_data.get('mysnippet')

        # if mysnippet field is selected, search only logged in user's snippets
        if mysnippets:
            snippet_list = Snippet.objects.filter(
                Q(user=request.user),
                Q(orig_code__icontains=query) | Q(title__icontains=query)
            )

        else:
            qs1 = Snippet.objects.filter(
                Q(exposure='public'),
                Q(orig_code__icontains = query) | Q(title__icontains = query)
                # Q(user=request.user)
            )

            # if the user is logged in then search his snippets
            if request.user.is_authenticated:
               qs2 = Snippet.objects.filter(Q(user=request.user),
                                            Q(orig_code__icontains=query) | Q(title__icontains=query))
               snippet_list = (qs1 | qs2).distinct()

            else:
                snippet_list = qs1

        snippets = paginate_result(request, snippet_list, 5)

    return render(request, 'codeviewer/search.html', {'form': f, 'snippets': snippets })
def tagsnippet(request,tagname):
    t=get_object_or_404(Tag,name=tagname)
    snippet_list=get_list_or_404(t.snippet_set)
    snippets=paginate_result(request,snippet_list,5)
    return render(request,'codeviewer/taglist.html',{'snippets':snippets,'tag':t})
def trendingsnippet(request,language_slug=''):
    lang=None
    snippets=Snippet.objects
    if language_slug:
        snippets=snippets.filter(language__slug=language_slug)
        lang=get_object_or_404(Language,slug=language_slug)
    snippet_list=get_list_or_404(snippets.filter(exposure='public').order_by('-hits'))
    snippets=paginate_result(request,snippet_list,5)
    return render(request,'codeviewer/trending.html',{'snippets':snippets,'lang':lang})
@private_snippet
def snippetdetail(request,snippet_slug):
    snippet=get_object_or_404(Snippet,slug=snippet_slug)
    snippet.hits+=1
    snippet.save()
    return render(request,'codeviewer/snippetdetail.html',{'snippet':snippet})
def index(request):
    if request.method ==  'POST':
        f = SnippetForm(request,request.POST)
        if f.is_valid():
            snippet = f.save(request)
            return redirect(reverse('codeviewer:snippetdetail', args=[snippet.slug]))

    else:
        f = SnippetForm(request)
    return render(request, 'codeviewer/index.html', {'form': f})
@private_snippet
def download_snippet(request,snippet_slug):
    snippet=get_object_or_404(Snippet,slug=snippet_slug)
    file_extension=snippet.language.file_extension
    filename=snippet.slug+file_extension
    res=HttpResponse(snippet.orig_code)
    res['content-disposition']='attachment;filename='+filename+';'
    return res
@private_snippet
def raw_snippet(request,snippet_slug):
    snippet=get_object_or_404(Snippet,slug=snippet_slug)
    return HttpResponse(snippet.orig_code,content_type=snippet.language.mime)
def contact(request):
    if request.method == 'POST':
        f = ContactForm(request,request.POST)
        if f.is_valid():

            if request.user.is_authenticated:
                name = request.user.username
                email = request.user.email
            else:
                name = f.cleaned_data['name']
                email = f.cleaned_data['email']
            subject = "You have a new Feedback from {}:<{}>".format(name,email)
            message="Purpose:{}\n\nDate:{}\n\nMessage:\n\n{}".format(dict(f.purpose_choices).get(f.cleaned_data['purpose']),datetime.datetime.now(),f.cleaned_data['message'])
            mail_admins(subject,message)
            messages.add_message(request,messages.INFO,'Thanks for submitting your feedback.')
            return redirect('codeviewer:contact')
    else:
        f=ContactForm(request)
    return render(request,'codeviewer/contact.html',{'form':f})
def login(request):
    if request.user.is_authenticated:
        return redirect('codeviewer:userprofile',username=request.user.username,email=request.user.email)
    if request.POST:
        f=LoginForm(request.POST)
        if f.is_valid():
            user=User.objects.filter(email=f.cleaned_data['email'])
            if user:
                username=user[0].username
                password=f.cleaned_data['password']
                user=auth.authenticate(username=username,password=password)
                if user:
                    auth.login(request,user)
                    return redirect(request.GET.get('next')or 'codeviewer:index')
            messages.add_message(request,messages.INFO,'Invalid email/password.')
            return redirect('codeviewer:login')
    else:
        f=LoginForm()
    return render(request,'codeviewer/login.html',{'form':f})
@login_required
def logout(request):
    auth.logout(request)
    return render(request,'codeviewer/logout.html')
@login_required
def user_detail(request):
    user=get_object_or_404(User,id=request.user.id)
    return render(request,'codeviewer/user_detail.html',{'user':user})
def signup(request):
    if request.user.is_authenticated:
        return redirect('codeviewer:userprofile',username=request.user.username,email=request.user.email)
    if request.POST:
        f=CreateUserForm(request.POST)
        if f.is_valid():
            f.save(request)
            messages.success(request,'Account created successfully.check your mail section to verify your account.')
            return redirect('codeviewer:signup')
    else:
        f=CreateUserForm()
    return render(request,'codeviewer/signup.html',{'form':f})
def activate_account(request,uidb64,token):
    try:
        uid=force_text(urlsafe_base64_decode(uidb64))
        user=User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.add_message(request,messages.INFO,'Account activated.Please login.')
    else:
        messages.add_message(request,messages.INFO,'Link expired.Contact admin to login.')
    return redirect('codeviewer:login')
@login_required
def settings(request):
    user=get_object_or_404(User,id=request.user.id)
    if request.POST:
        f=SettingForm(request.POST,instance=user.profile)
        if f.is_valid():
            f.save()
            messages.add_message(request,messages.INFO,'Settings updated.')
            return redirect('codeviewer:settings')
    else:
        f=SettingForm(instance=user.profile)
    return render(request,'codeviewer/settings.html',{'form':f})
@login_required
def delete_snippet(request,snippet_slug):
    snippet=get_object_or_404(Snippet,slug=snippet_slug)
    if request.user!=snippet.user:
        raise Http404
    snippet.delete()
    return redirect('codeviewer:userprofile',request.user)
#def add_lang(request):
#    if request.POST:
#        f=LanguageForm(request.POST)
#        if f.is_valid():
#            lang=f.save()
#            messages.add_message(request,messages.INFO,'New language saved.')
#            return redirect('codeviewer:add_lang')
#    else:
#        f=LanguageForm()
#    return render(request,'codeviewer/add_lang.html',{'form':f})
#def update_lang(request,lang_slug):
#    l=get_object_or_404(Language,slug__iexact=lang_slug)
#    if request.POST:
#        f=LanguageForm(request.POST,instance=l)
#        if f.is_valid():
#            lang=f.save()
#            messages.add_message(request,messages.INFO,'Language updated.')
#            return redirect('codeviewer:update_lang',lang.slug)
#    else:
#        f=LanguageForm(instance=l)
#    return render(request,'codeviewer/update_lang.html',{'form':f})

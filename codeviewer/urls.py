from django.contrib import admin
from django.urls import path,re_path,reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
app_name='codeviewer'
urlpatterns = [
    path('',views.index,name='index'),
    re_path('^user/(?P<username>[A-Za-z]+)/$',views.userprofile,name='userprofile'),
    re_path('^trending/$',views.trendingsnippet,name='trendingsnippet'),
    re_path('^trending/(?P<language_slug>[\w-]+)/$',views.trendingsnippet,name='trendingsnippet'),
    re_path('^(?P<snippet_slug>[0-9]+)/$',views.snippetdetail,name='snippetdetail'),
    re_path('^tag/(?P<tagname>[\w-]+)/$',views.tagsnippet,name='tagsnippet'),
    re_path('^download/(?P<snippet_slug>[\w-]+)/$',views.download_snippet,name='download_snippet'),
    re_path('^raw/(?P<snippet_slug>[\w-]+)/$',views.raw_snippet,name='raw_snippet'),
    re_path('^contact/$',views.contact,name='contact'),
    #re_path('^login/$',auth_views.LoginView.as_view(template_name='codeviewer/login.html'),name='login'),
    #re_path('^logout/$',auth_views.LogoutView.as_view(template_name='codeviewer/logout.html'),name='logout'),
    re_path('^login/$',views.login,name='login'),
    re_path('^logout/$',views.logout,name='logout'),
    re_path('^user_detail/$',views.user_detail,name='user_detail'),
    re_path('^signup/$',views.signup,name='signup'),
    re_path('^activate/(?P<uidb64>[\w.-]+)/(?P<token>[\w.-]+)/$',views.activate_account,name='activate'),
    re_path('^password-reset/$',auth_views.PasswordResetView.as_view(template_name='codeviewer/password_reset.html',email_template_name='codeviewer/email/password_reset_email.txt',subject_template_name='codeviewer/email/password_reset_subject.txt',success_url=reverse_lazy('codeviewer:password_reset_done')),name='password_reset'),
    re_path('^password-reset-done/$',auth_views.PasswordResetDoneView.as_view(template_name='codeviewer/password_reset_done.html'),name='password_reset_done'),
    re_path('^password-reset-confirm/(?P<uidb64>[\w.-]+)/(?P<token>[\w.-]+)/$',auth_views.PasswordResetConfirmView.as_view(template_name='codeviewer/password_reset_confirm.html',success_url=reverse_lazy('codeviewer:password_reset_complete')),name='password_reset_confirm'),
    re_path('^password-reset-complete/$',auth_views.PasswordResetCompleteView.as_view(template_name='codeviewer/password_reset_complete.html'),name='password_reset_complete'),
    re_path('^password-change/$',auth_views.PasswordChangeView.as_view(template_name='codeviewer/password_change.html',success_url=reverse_lazy('codeviewer:password_change_done')),name='password_change'),
    re_path('^password-change-done/$',auth_views.PasswordChangeDoneView.as_view(template_name='codeviewer/password_change_done.html'),name='password_change_done'),
    re_path('^settings/$',views.settings,name='settings'),
    re_path('^delete/(?P<snippet_slug>[\w-]+)/$',views.delete_snippet,name='delete_snippet'),
    re_path('^search/$',views.search,name='search'),
    #path('add_lang/',views.add_lang,name='add_lang'),
    #re_path('update_lang/(?P<lang_slug>[\w-]+)/',views.update_lang,name='update_lang')
    ]

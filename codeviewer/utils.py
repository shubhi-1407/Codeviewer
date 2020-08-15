from django.contrib.auth.models import User
from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger
class Preference:
    snippet_expire_never='never'
    snippet_expire_onemonth='1 month'
    snippet_expire_sixmonths='6 months'
    snippet_expire_oneyear='1 year'
    expiration_choices=((snippet_expire_never,'never'),
    (snippet_expire_onemonth,'1 month'),
    (snippet_expire_sixmonths,'6 months'),
    (snippet_expire_oneyear,'1 year'))
    snippet_private='private'
    snippet_public='public'
    snippet_unlisted='unlisted'
    exposure_choices=((snippet_private,'private'),
    (snippet_public,'public'),
    (snippet_unlisted,'unlisted'))
def get_current_user(request):
    if request.user.is_authenticated:
        return request.user
    return User.objects.filter(username='guest')[0]
def paginate_result(request,object_list,records_per_page):
    paginator=Paginator(object_list,records_per_page)
    page=request.GET.get('page')
    try:
        results=paginator.page(page)
    except PageNotAnInteger:
        results=paginator.page(1)
    except EmptyPage:
        results=paginator.page(paginator.num_pages)
    return results

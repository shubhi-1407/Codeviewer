from .models import Snippet

def recent_snippet(request):
    return dict(recent_snippet=Snippet.objects.filter(exposure='public').order_by('-id')[:8])

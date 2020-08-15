from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from . import models
class LanguageAdmin(admin.ModelAdmin):
    list_display=['name','lang_code','mime','slug','file_extension','created_on','updated_on']
    search_fields=['name','lang_code']
    ordering=['name']
    list_filter=['name','created_on']
    date_hierarchy='created_on'
class AuthorInline(admin.StackedInline):
    model=models.Author
class CustomUserAdmin(UserAdmin):
    inlines=(AuthorInline,)
class SnippetAdmin(admin.ModelAdmin):
    list_display=['title','slug','expiration','exposure','hits','created_on','user','language']
    search_fields=['title','user']
    ordering=['-created_on']
    list_filter=['created_on']
    date_hierarchy='created_on'
    raw_id_fields=['tag']
    readonly_fields=['high_code','slug','hits']
class TagAdmin(admin.ModelAdmin):
    list_display=['name','slug']
    search_fields=['name']
    readonly_fields=['slug']
admin.site.unregister(User)
admin.site.register(User,CustomUserAdmin)
admin.site.register(models.Language,LanguageAdmin)
admin.site.register(models.Snippet,SnippetAdmin)
admin.site.register(models.Tag,TagAdmin)

from django.shortcuts import reverse,render,HttpResponse,get_object_or_404
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .utils import Preference
from pygments import lexers,highlight
from pygments.formatters import HtmlFormatter
from django.utils.text import slugify
import time

class Language(models.Model):
    name=models.CharField(max_length=100)
    lang_code=models.CharField(max_length=100,unique=True)
    slug=models.SlugField(max_length=100,unique=True)
    mime=models.CharField(max_length=100)
    file_extension=models.CharField(max_length=10)
    created_on=models.DateTimeField(auto_now_add=True)
    updated_on=models.DateTimeField(auto_now=True)
    def get_lexer(self):
        return lexers.get_lexer_by_name(self.lang_code)
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('codeviewer:trendingsnippet',args=[self.slug])
    class Meta:
        ordering=['name']
def get_default_language():
    lang=Language.objects.get_or_create(name='Plain Text',lang_code='text',slug='text',mime='text/plain',file_extension='.txt')
    return lang[0].id
class Author(models.Model):
    user=models.OneToOneField(User,related_name='profile',on_delete=models.CASCADE)
    default_language=models.ForeignKey(Language,on_delete=models.CASCADE,default=get_default_language)
    default_exposure=models.CharField(max_length=10,choices=Preference.exposure_choices,default=Preference.snippet_public)
    default_expiration=models.CharField(max_length=10,choices=Preference.expiration_choices,default=Preference.snippet_expire_never)
    private=models.BooleanField(default=False)
    views=models.IntegerField(default=0)

    def __str__(self):
        return self.user.username
    def get_absolute_url(self):
        return reverse('codeviewer:userprofile',args=[self.user.username])
    def get_snippet_count(self):
        return self.user.snippet_set.count()
    def get_preferences(self):
        return {'language':self.default_language.id,'exposure':self.default_exposure,'expiration':self.default_expiration}
@receiver(post_save,sender=User)
def create_author(sender,**kwargs):
    if kwargs.get('created',False):
        Author.objects.get_or_create(user=kwargs.get('instance'))

class Snippet(models.Model):
    title=models.CharField(max_length=100,blank=True)
    orig_code=models.TextField()
    high_code=models.TextField(help_text='readonly field')
    slug=models.SlugField(max_length=100,unique=True,help_text='readonly field')
    expiration=models.CharField(max_length=10,choices=Preference.expiration_choices)
    exposure=models.CharField(max_length=10,choices=Preference.exposure_choices)
    hits=models.IntegerField(default=0,help_text='readonly field')
    created_on=models.DateTimeField(auto_now_add=True)

    user=models.ForeignKey(User,on_delete=models.CASCADE)
    language=models.ForeignKey(Language,on_delete=models.CASCADE)
    tag=models.ManyToManyField('Tag',blank=True)

    def highlight(self):
        formatter=HtmlFormatter(full=True,linenos=True)
        return highlight(self.orig_code,self.language.get_lexer(),formatter)
    def __str__(self):
        return (self.title if self.title else 'untitled')+'-'+self.language.name
    def get_absolute_url(self):
        return reverse('codeviewer:snippetdetail',args=[self.slug])
    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug=str(time.time()).replace('.','')
        self.high_code=self.highlight()
        if not self.title:
            self.title='Untitled'
        super(Snippet,self).save(*args,**kwargs)
    class Meta:
        ordering=['-created_on']
class Tag(models.Model):
    name=models.CharField(max_length=100,unique=True)
    slug=models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('codeviewer:tagsnippet',args=[self.slug])

    def save(self,*args,**kwargs):
        self.slug=slugify(self.name)
        super(Tag,self).save(*args,**kwargs)
    class Meta:
        ordering=['name']

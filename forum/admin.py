# -*- coding: utf-8 -*-

from django.contrib import admin
from models import *


class QuestionAdmin(admin.ModelAdmin):
    """Question admin class"""

class TagAdmin(admin.ModelAdmin):
    """Tag admin class"""
    
class Answerdmin(admin.ModelAdmin):
    """Answer admin class"""
    
    
admin.site.register(Question, QuestionAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Answer, Answerdmin)
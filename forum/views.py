# encoding:utf-8
import datetime
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template import RequestContext
from django.utils.html import *
from django.core import serializers 

from forum.forms import *
from forum.models import *
from utils.html import sanitize_html
import logging

# used in tags list
DEFAULT_PAGE_SIZE = 65

def index(request):
    view_id = request.GET.get('sort', None)
    view_dic = {"latest":"-added_at", "active":"-last_activity_at", "hottest":"-answer_count", "mostvoted":"-score" }
    try:
        orderby = view_dic[view_id]
    except KeyError:
        view_id = "latest"
        orderby = "-added_at"
    questions = Question.objects.all().order_by(orderby)[:30]
    tags = Tag.objects.all().order_by("-id")[:100]
    #print datetime.datetime.now()
    min = max = tags[0].used_count
    for tag in tags:
        if tag.used_count < min:
            min = tag.used_count
        if tag.used_count > max:
            max = tag.used_count

    #print datetime.datetime.now()
    
    return render_to_response('index.html', {
        "questions" : questions,
        "tab_id" : view_id,
        "tags" : tags,
        "max" : 100,
        "min" : 1,
        }, context_instance=RequestContext(request))
    
def questions(request):
    questions = Question.objects.all()
    return render_to_response('index.html', {
        "questions" : questions,
        }, context_instance=RequestContext(request))

#TODO: allow anynomus user to ask question by providing email and username.
@login_required 
def ask(request):
    if request.method == "POST":
        form = AskForm(request.POST)
        if form.is_valid():
            added_at = datetime.datetime.now()
            question = Question(
                title            = form.cleaned_data['title'],
                author           = request.user,
                added_at         = added_at,
                last_activity_at = added_at,
                last_activity_by = request.user,
                tagnames         = form.cleaned_data['tags'].strip(),
                html             = sanitize_html(form.cleaned_data['text']),
                summary          = strip_tags(form.cleaned_data['text'])[:180]
            )
            
            question.save()
            
            #TODO:add wiki support
            #TODO:add badge support
            
            return HttpResponseRedirect("/questions/%s" % question.id)
        
    else:
        form = AskForm()
        tags = serializers.serialize("json", Tag.objects.all())
    return render_to_response('ask.html', {
        'form' : form,
        'tags' : tags,
        }, context_instance=RequestContext(request))

def question(request, id):
    question = get_object_or_404(Question, id=id)
    logging.debug(question)
    answer_form = AnswerForm()
    answers = Answer.objects.get_answers_from_question(question, request.user)
    
    return render_to_response('question.html', {
        "question" : question,
        "answer" : answer_form,
        "answers" : answers,
        }, context_instance=RequestContext(request))
 
#TODO: allow anynomus
@login_required 
def answer(request, id):
    question = get_object_or_404(Question, id=id)
    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            try:
                answer = Answer(
                    question = question,
                    author = request.user,
                    added_at = datetime.datetime.now(),
                    html = sanitize_html(form.cleaned_data['text']),
                )
                answer.save()
                Question.objects.update_answer_count(question)
                
            except Exception,e:
                logging.error(e)
                
    return HttpResponseRedirect(question.get_absolute_url())

def tags(request):
    stag = ""
    is_paginated = True
    sortby = request.GET.get('sort', 'used')
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    
    if request.method == "GET":
        if sortby == "name":
            objects_list = Paginator(Tag.objects.all().order_by("name"), DEFAULT_PAGE_SIZE)
        else:
            objects_list = Paginator(Tag.objects.all().order_by("-used_count"), DEFAULT_PAGE_SIZE)

    elif request.method == "POST":
        stag = request.POST.get("ipSearchTag")
        #disable paginator for search results
        is_paginated = False
        if stag is not None:
            objects_list = Paginator(Tag.objects.extra(where=['name like %s'], params=['%' + stag + '%'])[:50] , DEFAULT_PAGE_SIZE) 

    try:
        tags = objects_list.page(page)
    except (EmptyPage, InvalidPage):
        tags = objects_list.page(tags.num_pages)

    return render_to_response('tags.html', {
        "tags" : tags,
        "stag" : stag,
        "tab_id" : sortby,
        "context" : {
            'is_paginated' : is_paginated,
            'pages': objects_list.num_pages,
            'page': page,
            'has_previous': tags.has_previous(),
            'has_next': tags.has_next(),
            'previous': tags.previous_page_number(),
            'next': tags.next_page_number(),
            'base_url' : '/tags?sort=%s&' % sortby
        }
        
        }, context_instance=RequestContext(request))

def tag(request, name):    
    return render_to_response('tag.html', context_instance=RequestContext(request))
    
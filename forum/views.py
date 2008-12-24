# encoding:utf-8
import datetime
import logging
from urllib import quote, unquote
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


# used in tags list
DEFAULT_PAGE_SIZE = 65
# used for questions
QUESTIONS_PAGE_SIZE = 10
# used for users
USERS_PAGE_SIZE = 35

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

def unanswered(request):
    return questions(request, unanswered=True)
    
def questions(request, tagname=None, unanswered=False):
    """
    List of Questions, Tagged questions, and Unanswered questions.
    """
    # template file 
    # "questions.html" or "unanswered.html"
    template_file = "questions.html"
    # Set flag to False by default. If it is equal to True, then need to be saved.
    pagesize_changed = False
    # get pagesize from session, if failed then get default value
    user_page_size = request.session.get("pagesize", QUESTIONS_PAGE_SIZE)
    # set pagesize equal to logon user specified value in database
    if request.user.is_authenticated() and request.user.questions_per_page > 0:
        user_page_size = request.user.questions_per_page

    try:
        page = int(request.GET.get('page', '1'))
        # get new pagesize from UI selection
        pagesize = int(request.GET.get('pagesize', user_page_size))
        if pagesize <> user_page_size:
            pagesize_changed = True
        
    except ValueError:
        page = 1
        pagesize  = user_page_size
    
    # save this pagesize to user database
    if pagesize_changed:
        request.session["pagesize"] = pagesize
        if request.user.is_authenticated():
            user = request.user
            user.questions_per_page = pagesize 
            user.save()

    view_id = request.GET.get('sort', None)
    view_dic = {"latest":"-added_at", "active":"-last_activity_at", "hottest":"-answer_count", "mostvoted":"-score" }
    try:
        orderby = view_dic[view_id]
    except KeyError:
        view_id = "latest"
        orderby = "-added_at"
    
    # check if request is from tagged questions
    if tagname is not None:
        #print datetime.datetime.now()
        objects_list = Paginator(Question.objects.filter(tags__name = unquote(tagname)).order_by(orderby), pagesize)
        #print datetime.datetime.now()
    elif unanswered:
        #check if request is from unanswered questions
        template_file = "unanswered.html"
        objects_list = Paginator(Question.objects.filter(answer_count=0).order_by(orderby), pagesize)
    else:
        objects_list = Paginator(Question.objects.all().order_by(orderby), pagesize)
    
    questions = objects_list.page(page)
    
    # Get related tags from this page objects
    related_tags = []
    for question in questions.object_list:
        tags = list(question.tags.all())
        for tag in tags:
            if tag not in related_tags:
                related_tags.append(tag)
            
    return render_to_response(template_file, {
        "questions" : questions,
        "tab_id" : view_id,
        "questions_count" : objects_list.count,
        "tags" : related_tags,
        "searchtag" : tagname, 
        "is_unanswered" : unanswered,
        "context" : {
            'is_paginated' : True,
            'pages': objects_list.num_pages,
            'page': page,
            'has_previous': questions.has_previous(),
            'has_next': questions.has_next(),
            'previous': questions.previous_page_number(),
            'next': questions.next_page_number(),
            'base_url' : request.path + '?sort=%s&' % view_id,
            'pagesize' : pagesize
        }}, context_instance=RequestContext(request))

#TODO: allow anynomus user to ask question by providing email and username.
@login_required 
def ask(request):
    if request.method == "POST":
        form = AskForm(request.POST)
        if form.is_valid():
            added_at = datetime.datetime.now()
            question = Question(
                title            = quote(sanitize_html(form.cleaned_data['title'])),
                author           = request.user,
                added_at         = added_at,
                last_activity_at = added_at,
                last_activity_by = request.user,
                tagnames         = form.cleaned_data['tags'].strip(),
                html             = sanitize_html(form.cleaned_data['text']),
                summary          = strip_tags(form.cleaned_data['text'])[:120]
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
    answer_form = AnswerForm()
    answers = Answer.objects.get_answers_from_question(question, request.user)
    # update view count
    Question.objects.update_view_count(question)
    return render_to_response('question.html', {
        "question" : question,
        "answer" : answer_form,
        "answers" : answers,
        "tags" : question.tags.all(),
        "similar_questions" : Question.objects.get_similar_questions(question)
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
        stag = request.POST.get("ipSearchTag").strip()
        #disable paginator for search results
        is_paginated = False
        if stag is not None:
            objects_list = Paginator(Tag.objects.extra(where=['name like %s'], params=['%' + stag + '%'])[:50] , DEFAULT_PAGE_SIZE) 

    try:
        tags = objects_list.page(page)
    except (EmptyPage, InvalidPage):
        tags = objects_list.page(objects_list.num_pages)

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
            'base_url' : '/tags/?sort=%s&' % sortby
        }
        
        }, context_instance=RequestContext(request))

def tag(request, tag):    
    return questions(request, tagname=tag)

def users(request):
    is_paginated = True
    sortby = request.GET.get('sort', 'reputation')
    suser = request.REQUEST.get('ipSearchUser',  "")
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
  
    if suser == "":
        if sortby == "date_joined_desc":
            objects_list = Paginator(User.objects.all().order_by('-date_joined'), USERS_PAGE_SIZE)
        elif sortby == "date_joined_asc":
            objects_list = Paginator(User.objects.all().order_by('date_joined'), USERS_PAGE_SIZE)
        elif sortby == "username":
            objects_list = Paginator(User.objects.all().order_by('username'), USERS_PAGE_SIZE)
        # default
        else:
            objects_list = Paginator(User.objects.all().order_by('-reputation'), USERS_PAGE_SIZE)
    else:
        sortby = "username"
        objects_list = Paginator(User.objects.extra(where=['username like %s'], params=['%' + suser + '%']).order_by(sortby), USERS_PAGE_SIZE)
    
    if suser == "":
        base_url = '/users/?sort=%s&' % sortby
    else:
        base_url = '/users/?ipSearchUser=%s&sort=%s&' % (suser, sortby)
    
    try:
        users = objects_list.page(page)
    except (EmptyPage, InvalidPage):
        users = objects_list.page(objects_list.num_pages)
  
    return render_to_response('users.html', {
        "users" : users,
        "suser" : suser,
        "tab_id" : sortby,
        "context" : {
            'is_paginated' : is_paginated,
            'pages': objects_list.num_pages,
            'page': page,
            'has_previous': users.has_previous(),
            'has_next': users.has_next(),
            'previous': users.previous_page_number(),
            'next': users.next_page_number(),
            'base_url' : base_url
        }
        
        }, context_instance=RequestContext(request))

def user_stats(request, user_id, username):
    user = get_object_or_404(User, id=user_id)
    # TODO:order by vote_count desc
    questions = user.questions.all().order_by('-added_at')
    answers = user.answers.all().order_by('-added_at')
    up_votes = Vote.objects.get_up_vote_count_from_user(user)
    down_votes = Vote.objects.get_down_vote_count_from_user(user)
    tags = user.created_tags.all().order_by('-used_count')
    # TODO: Badges
    
    return render_to_response('user_stats.html',{
        "tab_name" : "stats",
        "user" : user,
        "questions" : questions,
        "answers" : answers,
        "up_votes" : up_votes,
        "down_votes" : down_votes,
        "tags" : tags
    })
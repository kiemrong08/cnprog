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
from django.utils import simplejson
from django.core import serializers 
from django.db import transaction
from forum.forms import *
from forum.models import *
from forum.auth import *
from utils.html import sanitize_html

# used in index page
INDEX_PAGE_SIZE = 30
INDEX_TAGS_SIZE = 100
# used in tags list
DEFAULT_PAGE_SIZE = 65
# used in questions
QUESTIONS_PAGE_SIZE = 10
# used in users
USERS_PAGE_SIZE = 35
# used in answers
ANSWERS_PAGE_SIZE = 10 

def index(request):
    view_id = request.GET.get('sort', None)
    view_dic = {"latest":"-added_at", "active":"-last_activity_at", "hottest":"-answer_count", "mostvoted":"-score" }
    try:
        orderby = view_dic[view_id]
    except KeyError:
        view_id = "latest"
        orderby = "-added_at"
    questions = Question.objects.filter(deleted=False).order_by(orderby)[:INDEX_PAGE_SIZE]
    
    # RISK - inner join queries
    questions = questions.select_related();
    tags = Tag.objects.all().order_by("-id")[:INDEX_TAGS_SIZE]
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

def about(request):
    return render_to_response('about.html', context_instance=RequestContext(request))
        
def faq(request):
    return render_to_response('faq.html', context_instance=RequestContext(request))
            
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
        objects = Question.objects.filter(deleted=False, tags__name = unquote(tagname)).order_by(orderby)
        #print datetime.datetime.now()
    elif unanswered:
        #check if request is from unanswered questions
        template_file = "unanswered.html"
        objects = Question.objects.filter(deleted=False, answer_count=0).order_by(orderby)
    else:
        objects = Question.objects.filter(deleted=False).order_by(orderby)
        
    # RISK - inner join queries
    objects = objects.select_related();
    objects_list = Paginator(objects, pagesize)
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
                title            = strip_tags(form.cleaned_data['title']),
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

    tags = Tag.objects.select_related('created_by')
    tags = serializers.serialize("json", tags, fields=('name', 'used_count'))
    return render_to_response('ask.html', {
        'form' : form,
        'tags' : tags,
        }, context_instance=RequestContext(request))

def question(request, id):
    try:
        page = int(request.GET.get('page', '1'))        
    except ValueError:
        page = 1
    view_id = request.GET.get('sort', 'latest')
    view_dic = {"latest":"-added_at", "oldest":"added_at", "votes":"-score" }
    try:
        orderby = view_dic[view_id]
    except KeyError:
        view_id = "latest"
        orderby = "-added_at"
        
    question = get_object_or_404(Question, id=id)

    answer_form = AnswerForm()
    answers = Answer.objects.get_answers_from_question(question, request.user)
    answers = answers.select_related(depth=1)
    
    favorited = question.has_favorite_by_user(request.user)
    question_vote = question.votes.select_related().filter(user=request.user)
    if question_vote is not None and question_vote.count() > 0:
        question_vote = question_vote[0]
        
    user_answer_votes = {}
    for answer in answers:
        vote = answer.get_user_vote(request.user)
        if vote is not None and not user_answer_votes.has_key(answer.id):
            vote_value = -1
            if vote.is_upvote():
                vote_value = 1
            user_answer_votes[answer.id] = vote_value
            
            
    if answers is not None:
        answers = answers.order_by("-accepted", orderby)
    objects_list = Paginator(answers, ANSWERS_PAGE_SIZE)
    page_objects = objects_list.page(page)
    # update view count
    Question.objects.update_view_count(question)
    return render_to_response('question.html', {
        "question" : question,
        "question_vote" : question_vote,
        "question_comment_count":question.comments.count(),
        "answer" : answer_form,
        "answers" : page_objects.object_list,
        "user_answer_votes": user_answer_votes,
        "tags" : question.tags.all(),
        "tab_id" : view_id,
        "favorited" : favorited,
        "similar_questions" : Question.objects.get_similar_questions(question), 
        "context" : {
            'is_paginated' : True,
            'pages': objects_list.num_pages,
            'page': page,
            'has_previous': page_objects.has_previous(),
            'has_next': page_objects.has_next(),
            'previous': page_objects.previous_page_number(),
            'next': page_objects.next_page_number(),
            'base_url' : request.path + '?sort=%s&' % view_id,
            'extend_url' : "#sort-top"
        }
        }, context_instance=RequestContext(request))
 
@login_required 
def close(request, id):
    question = get_object_or_404(Question, id=id)
    # open question
    if not can_close_question(request.user, question):
        return HttpResponse('Permission denied.')
    if request.method == 'POST':
        form = CloseForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            question.closed = True
            question.closed_by = request.user
            question.closed_at = datetime.datetime.now()
            question.close_reason = reason
            question.save()
        return HttpResponseRedirect(question.get_absolute_url())
    else:
        form = CloseForm()
        return render_to_response('close.html', {
            'form' : form,
            'question' : question,
            }, context_instance=RequestContext(request))
        
#TODO: allow anynomus
@login_required 
def answer(request, id):
    question = get_object_or_404(Question, id=id)
    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            try:
                update_time = datetime.datetime.now()
                answer = Answer(
                    question = question,
                    author = request.user,
                    added_at = update_time,
                    html = sanitize_html(form.cleaned_data['text']),
                )
                answer.save()
                Question.objects.update_answer_count(question)
                
                question = get_object_or_404(Question, id=id)
                question.last_activity_at = update_time 
                question.last_activity_by = request.user
                question.save()
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

def vote(request, id):
    """
    accept answer code:
        response_data['allowed'] = -1, Accept his own answer   0, no allowed - Anonymous    1, Allowed - by default
        response_data['success'] =  0, failed                                               1, Success - by default
        response_data['status']  =  0, By default                                           1, Answer has been accepted already(Cancel)

    vote code:
        allowed = -3, Don't have enough votes left
                  -2, Don't have enough reputation score     
                  -1, Vote his own post   
                   0, no allowed - Anonymous    
                   1, Allowed - by default
        status  =  0, By default
                   1, Cancel
                   2, Vote is too old to be canceled
    
    offensive code:
        allowed = -3, Don't have enough flags left
                  -2, Don't have enough reputation score to do this
                   0, not allowed
                   1, allowed
        status  =  0, by default
                   1, can't do it again
    """
    response_data = {
        "allowed": 1,
        "success": 1,
        "status" : 0,
        "count"  : 0, 
        "message" : ''
    }
    
    def can_vote(vote_score, user):
        if vote_score == 1:
            return can_vote_up(request.user)
        else:
            return can_vote_down(request.user)
        
    try:
        if not request.user.is_authenticated():
            response_data['allowed'] = 0
            response_data['success'] = 0
            
        elif request.is_ajax():
            question = get_object_or_404(Question, id=id)
            vote_type = request.POST.get('type')
            
            #accept answer
            if vote_type == '0':
                answer_id = request.POST.get('postId')
                answer = get_object_or_404(Answer, id=answer_id)
                # make sure question author is current user
                if question.author == request.user:
                    # answer user who is also question author is not allow to accept answer
                    if answer.author == question.author:
                        response_data['success'] = 0
                        response_data['allowed'] = -1
                    # check if answer has been accepted already
                    elif answer.accepted:
                        onAnswerAcceptCanceled(answer, request.user)
                        response_data['status'] = 1
                    else:
                        # set other answers in this question not accepted first
                        for answer_of_question in Answer.objects.get_answers_from_question(question, request.user):
                            if answer_of_question != answer and answer_of_question.accepted:
                                onAnswerAcceptCanceled(answer_of_question, request.user)
                        
                        #make sure retrieve data again after above author changes, they may have related data
                        answer = get_object_or_404(Answer, id=answer_id)
                        onAnswerAccept(answer, request.user)
                      
                else:
                    response_data['allowed'] = 0
                    response_data['success'] = 0
            # favorite
            elif vote_type == '4':
                has_favorited = False
                fav_questions = FavoriteQuestion.objects.filter(question=question)
                # if the same question has been favorited before, then delete it
                if fav_questions is not None:
                    for item in fav_questions:
                        if item.user == request.user:
                            item.delete()
                            response_data['status'] = 1
                            response_data['count']  = len(fav_questions) - 1
                            if response_data['count'] < 0:
                                response_data['count'] = 0
                            has_favorited = True
                # if above deletion has not been executed, just insert a new favorite question            
                if not has_favorited:
                    new_item = FavoriteQuestion(question=question, user=request.user)
                    new_item.save()
                    response_data['count']  = FavoriteQuestion.objects.filter(question=question).count()
                Question.objects.update_favorite_count(question) 
                
            elif vote_type in ['1', '2', '5', '6']:
                post_id = id
                post = question
                vote_score = 1
                if vote_type in ['5', '6']:
                    answer_id = request.POST.get('postId')
                    answer = get_object_or_404(Answer, id=answer_id)
                    post_id = answer_id
                    post = answer
                if vote_type in ['2', '6']:
                    vote_score = -1
                
                if post.author == request.user:
                    response_data['allowed'] = -1
                elif not can_vote(vote_score, request.user):
                    response_data['allowed'] = -2
                elif post.votes.filter(user=request.user).count() > 0:
                    vote = post.votes.filter(user=request.user)[0]
                    # unvote should be less than certain time
                    if (datetime.datetime.now().day - vote.voted_at.day) >= VOTE_RULES['scope_deny_unvote_days']:
                        response_data['status'] = 2
                    else:
                        voted = vote.vote
                        if voted > 0:
                            # cancel upvote
                            onUpVotedCanceled(vote, post, request.user)
                            
                        else:
                            # cancel downvote
                            onDownVotedCanceled(vote, post, request.user)
                            
                        response_data['status'] = 1
                        response_data['count'] = post.score
                elif Vote.objects.get_votes_count_today_from_user(request.user) >= VOTE_RULES['scope_votes_per_user_per_day']:
                    response_data['allowed'] = -3
                else:
                    vote = Vote(user=request.user, content_object=post, vote=vote_score, voted_at=datetime.datetime.now())
                    if vote_score > 0:
                        # upvote
                        onUpVoted(vote, post, request.user)
                    else:
                        # downvote
                        onDownVoted(vote, post, request.user)
                        
                    votes_left = VOTE_RULES['scope_votes_per_user_per_day'] - Vote.objects.get_votes_count_today_from_user(request.user)    
                    if votes_left <= VOTE_RULES['scope_warn_votes_left']:
                        response_data['message'] = u'%s votes left' % votes_left
                    response_data['count'] = post.score
            elif vote_type in ['7', '8']:
                post = question
                post_id = id
                if vote_type == '8':
                    post_id = request.POST.get('postId')
                    post = get_object_or_404(Answer, id=post_id)
                
                if FlaggedItem.objects.get_flagged_items_count_today(request.user) >= VOTE_RULES['scope_flags_per_user_per_day']:
                    response_data['allowed'] = -3
                elif not can_flag_offensive(request.user):
                    response_data['allowed'] = -2
                elif post.flagged_items.filter(user=request.user).count() > 0:
                    response_data['status'] = 1
                else:
                    item = FlaggedItem(user=request.user, content_object=post, flagged_at=datetime.datetime.now())
                    onFlaggedItem(item, post, request.user)
                    response_data['count'] = post.offensive_flag_count
                    
                print 2    
        else:
            response_data['success'] = 0
            response_data['message'] = u'Request mode is not supported. Please try again.'

        data = simplejson.dumps(response_data)
    
    except Excecption, e:
        response_data['message'] = e    
    return HttpResponse(data, mimetype="application/json")
    
def users(request):
    is_paginated = True
    sortby = request.GET.get('sort', 'reputation')
    suser = request.REQUEST.get('name',  "")
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
  
    if suser == "":
        if sortby == "newest":
            objects_list = Paginator(User.objects.all().order_by('-date_joined'), USERS_PAGE_SIZE)
        elif sortby == "last":
            objects_list = Paginator(User.objects.all().order_by('date_joined'), USERS_PAGE_SIZE)
        elif sortby == "user":
            objects_list = Paginator(User.objects.all().order_by('username'), USERS_PAGE_SIZE)
        # default
        else:
            objects_list = Paginator(User.objects.all().order_by('-reputation'), USERS_PAGE_SIZE)
        base_url = '/users/?sort=%s&' % sortby
    else:
        sortby = "reputation"
        objects_list = Paginator(User.objects.extra(where=['username like %s'], params=['%' + suser + '%']).order_by('-reputation'), USERS_PAGE_SIZE)
        base_url = '/users/?name=%s&sort=%s&' % (suser, sortby)

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

def user_stats(request, user_id):
    user = get_object_or_404(User, id=user_id)
    questions = Question.objects.extra(
        select={
            'vote_count' : 'question.vote_up_count + question.vote_down_count',
            'favorited_myself' : 'SELECT count(*) FROM favorite_question f WHERE f.user_id = %s AND f.question_id = question.id',
            'la_user_id' : 'auth_user.id',
            'la_username' : 'auth_user.username',
            'la_user_gold' : 'auth_user.gold',
            'la_user_silver' : 'auth_user.silver',
            'la_user_bronze' : 'auth_user.bronze',
            'la_user_reputation' : 'auth_user.reputation'
            },
        select_params=[user_id],
        tables=['question', 'auth_user'],
        where=['question.deleted = 0 AND question.author_id=%s AND question.last_activity_by_id = auth_user.id'],
        params=[user_id],
        order_by=['-vote_count', '-question.id']
    ).values('vote_count',
             'favorited_myself',
             'id',
             'title',
             'author_id',
             'added_at',
             'answer_accepted',
             'answer_count',
             'comment_count',
             'view_count',
             'favourite_count',
             'summary',
             'tagnames',
             'vote_up_count',
             'vote_down_count',
             'last_activity_at',
             'la_user_id',
             'la_username',
             'la_user_gold',
             'la_user_silver',
             'la_user_bronze',
             'la_user_reputation')
    
    answered_questions = Question.objects.extra(
        select={
            'vote_count' : 'question.vote_up_count + question.vote_down_count',
            'user_answered_count' : 'SELECT count(*) FROM answer a2 WHERE a2.author_id = %s AND a2.question_id=question.id' 
            },
        tables=['question', 'answer'],
        where=['answer.deleted=0 AND answer.author_id=%s AND answer.question_id=question.id'],
        params=[user_id],
        order_by=['-vote_count', '-answer.id'],
        select_params=[user_id]
    ).distinct().values('user_answered_count', 
                        'id', 
                        'title', 
                        'author_id', 
                        'answer_accepted',
                        'answer_count',
                        'vote_up_count',
                        'vote_down_count')
    up_votes = Vote.objects.get_up_vote_count_from_user(user)
    down_votes = Vote.objects.get_down_vote_count_from_user(user)
    tags = user.created_tags.all().order_by('-used_count')[:50]
    # TODO: Badges
    
    return render_to_response('user_stats.html',{
        "tab_name" : "stats",
        "view_user" : user,
        "questions" : questions,
        "answered_questions" : answered_questions,
        "up_votes" : up_votes,
        "down_votes" : down_votes,
        "total_votes": up_votes + down_votes,
        "tags" : tags
    }, context_instance=RequestContext(request))

def user_recent(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render_to_response('user_recent.html',{
        "tab_name" : "recent",
        "view_user" : user
    }, context_instance=RequestContext(request))
    
def user_responses(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render_to_response('user_responses.html',{
        "tab_name" : "responses",
        "view_user" : user
    }, context_instance=RequestContext(request))

def user_reputation_history(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render_to_response('user_reputation_history.html',{
        "tab_name" : "reputation_history",
        "view_user" : user
    }, context_instance=RequestContext(request))

def users_favorites(request, user_id):
    user = get_object_or_404(User, id=user_id)
    questions = Question.objects.extra(
        select={
            'vote_count' : 'question.vote_up_count + question.vote_down_count',
            'favorited_myself' : 'SELECT count(*) FROM favorite_question f WHERE f.user_id = %s AND f.question_id = question.id',
            'la_user_id' : 'auth_user.id',
            'la_username' : 'auth_user.username',
            'la_user_gold' : 'auth_user.gold',
            'la_user_silver' : 'auth_user.silver',
            'la_user_bronze' : 'auth_user.bronze',
            'la_user_reputation' : 'auth_user.reputation'
            },
        select_params=[user_id],
        tables=['question', 'auth_user', 'favorite_question'],
        where=['question.deleted = 0 AND question.last_activity_by_id = auth_user.id AND favorite_question.question_id = question.id AND favorite_question.user_id = %s'],
        params=[user_id],
        order_by=['-vote_count', '-question.id']
    ).values('vote_count',
             'favorited_myself',
             'id',
             'title',
             'author_id',
             'added_at',
             'answer_accepted',
             'answer_count',
             'comment_count',
             'view_count',
             'favourite_count',
             'summary',
             'tagnames',
             'vote_up_count',
             'vote_down_count',
             'last_activity_at',
             'la_user_id',
             'la_username',
             'la_user_gold',
             'la_user_silver',
             'la_user_bronze',
             'la_user_reputation')
    return render_to_response('users_favorites.html',{
        "tab_name" : "favorites",
        "questions" : questions,
        "view_user" : user
    }, context_instance=RequestContext(request))

def question_comments(request, id):
    question = get_object_or_404(Question, id=id)
    user = request.user
    return __comments(request, question, user)

def answer_comments(request, id):
    answer = get_object_or_404(Answer, id=id)
    user = request.user
    return __comments(request, answer, user)

def __comments(request, obj, user):
    def generate_comments_json():
        comments = obj.comments.all().order_by('-id')
        # {"Id":6,"PostId":38589,"CreationDate":"an hour ago","Text":"hello there!","UserDisplayName":"Jarrod Dixon","UserUrl":"/users/3/jarrod-dixon","DeleteUrl":null}
        json_comments = []
        for comment in comments:
            comment_user = comment.user
            delete_url = ""
            if user != None and user.id == comment_user.id:
                delete_url = "/posts/392845/comments/219852/delete"
            json_comments.append({"id" : comment.id,
                "object_id" : obj.id,
                "add_date" : comment.added_at.strftime('%Y-%m-%d'),
                "text" : comment.comment,
                "user_display_name" : comment_user.username,
                "user_url" : "/users/%s/%s" % (comment_user.id, comment_user.username),
                "delete_url" : delete_url
            })
    
        data = simplejson.dumps(json_comments)
        return HttpResponse(data, mimetype="application/json")
        
    # only support get comments by ajax now
    if request.is_ajax():
        if request.method == "GET":
            return generate_comments_json()
        elif request.method == "POST":
            comment_data = request.POST.get('comment')
            comment = Comment(content_object=obj, comment=comment_data, user=request.user)
            comment.save()
            obj.comment_count = obj.comment_count + 1
            obj.save()
            return generate_comments_json()
# encoding:utf-8
import datetime
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.utils.html import *
from django.core import serializers 

from forum.forms import *
from forum.models import *
from utils.html import sanitize_html
import logging

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
    tags = Tag.objects.all()
    return render_to_response('tags.html', {
        "tags" : tags,
        }, context_instance=RequestContext(request))

def tag_search(request):
    q = request.GET.get("q", None)
    tags = serializers.serialize("json", Tag.objects.extra(where=["name LIKE %s"], params=['%'+ q +'%']))
    return HttpResponse(tags, mimetype="application/json")

def tag(request, name):
    tags = serializers.serialize("json", Tag.objects.all())
    
    return render_to_response('tag.html', {"tags": tags}, context_instance=RequestContext(request))
    
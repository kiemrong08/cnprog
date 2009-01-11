# encoding:utf-8
import datetime
import hashlib
from urllib import quote_plus, urlencode
from django.db import models
from django.utils.html import strip_tags
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify
from django.db.models.signals import post_delete, post_save, pre_save
from forum.managers import *
from const import *

class Tag(models.Model):
    name       = models.CharField(max_length=255, unique=True)
    created_by = models.ForeignKey(User, related_name='created_tags')
    # Denormalised data
    used_count = models.PositiveIntegerField(default=0)

    objects = TagManager()
    
    class Meta:
        db_table = u'tag'
        ordering = ('-used_count', 'name')

    def __unicode__(self):
        return self.name

class Comment(models.Model):
    content_type   = models.ForeignKey(ContentType)
    object_id      = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    user           = models.ForeignKey(User, related_name='comments')
    comment        = models.CharField(max_length=300)
    added_at       = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        ordering = ('-added_at',)
        db_table = u'comment'
    def __unicode__(self):
        return self.comment

class Vote(models.Model):
    VOTE_UP = +1
    VOTE_DOWN = -1
    VOTE_CHOICES = (
        (VOTE_UP,   u'Up'),
        (VOTE_DOWN, u'Down'),
    )

    content_type   = models.ForeignKey(ContentType)
    object_id      = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    user           = models.ForeignKey(User, related_name='votes')
    vote           = models.SmallIntegerField(choices=VOTE_CHOICES)
    voted_at       = models.DateTimeField(default=datetime.datetime.now)
    
    objects = VoteManager()
    
    class Meta:
        unique_together = ('content_type', 'object_id', 'user')
        db_table = u'vote'
    def __unicode__(self):
        return '[%s] voted at %s: %s' %(self.user, self.voted_at, self.vote)
        
    def is_upvote(self):
        return self.vote == self.VOTE_UP

    def is_downvote(self):
        return self.vote == self.VOTE_DOWN

class FlaggedItem(models.Model):
    """A flag on a Question or Answer indicating offensive content."""
    content_type   = models.ForeignKey(ContentType)
    object_id      = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    user           = models.ForeignKey(User, related_name='flagged_items')
    flagged_at     = models.DateTimeField(default=datetime.datetime.now)

    objects = FlaggedItemManager()
    
    class Meta:
        unique_together = ('content_type', 'object_id', 'user')
        db_table = u'flagged_item'
    def __unicode__(self):
        return '[%s] flagged at %s' %(self.user, self.flagged_at)
        
class Question(models.Model):
    title    = models.CharField(max_length=300)
    author   = models.ForeignKey(User, related_name='questions')
    added_at = models.DateTimeField(default=datetime.datetime.now)
    tags     = models.ManyToManyField(Tag, related_name='questions')
    # Status
    wiki            = models.BooleanField(default=False)
    wikified_at     = models.DateTimeField(null=True, blank=True)
    answer_accepted = models.BooleanField(default=False)
    closed          = models.BooleanField(default=False)
    closed_by       = models.ForeignKey(User, null=True, blank=True, related_name='closed_questions')
    closed_at       = models.DateTimeField(null=True, blank=True)
    close_reason    = models.SmallIntegerField(choices=CLOSE_REASONS, null=True, blank=True)
    deleted         = models.BooleanField(default=False)
    deleted_at      = models.DateTimeField(null=True, blank=True)
    deleted_by      = models.ForeignKey(User, null=True, blank=True, related_name='deleted_questions')
    locked          = models.BooleanField(default=False)
    locked_by       = models.ForeignKey(User, null=True, blank=True, related_name='locked_questions')
    locked_at       = models.DateTimeField(null=True, blank=True)
    # Denormalised data
    score                = models.IntegerField(default=0)
    vote_up_count        = models.IntegerField(default=0)
    vote_down_count      = models.IntegerField(default=0)
    answer_count         = models.PositiveIntegerField(default=0)
    comment_count        = models.PositiveIntegerField(default=0)
    view_count           = models.PositiveIntegerField(default=0)
    offensive_flag_count = models.SmallIntegerField(default=0)
    favourite_count      = models.PositiveIntegerField(default=0)
    last_edited_at       = models.DateTimeField(null=True, blank=True)
    last_edited_by       = models.ForeignKey(User, null=True, blank=True, related_name='last_edited_questions')
    last_activity_at     = models.DateTimeField(default=datetime.datetime.now)
    last_activity_by     = models.ForeignKey(User, related_name='last_active_in_questions')
    tagnames             = models.CharField(max_length=125)
    summary              = models.CharField(max_length=180)
    html                 = models.TextField()
    comments             = generic.GenericRelation(Comment)
    votes                = generic.GenericRelation(Vote)
    flagged_items        = generic.GenericRelation(FlaggedItem)
    
    objects = QuestionManager()

    def save(self, **kwargs):
        """
        Overridden to manually manage addition of tags when the object
        is first saved.

        This is required as we're using ``tagnames`` as the sole means of
        adding and editing tags.
        """
        initial_addition = (self.id is None)
        super(Question, self).save(**kwargs)
        if initial_addition:
            tags = Tag.objects.get_or_create_multiple(self.tagname_list(),
                                                      self.author)
            self.tags.add(*tags)
            Tag.objects.update_use_counts(tags)
    
    def tagname_list(self):
        """Creates a list of Tag names from the ``tagnames`` attribute."""
        return [name for name in self.tagnames.split(u' ')]
       
    def get_absolute_url(self):
        return '%s%s' % (reverse('question', args=[self.id]), self.title)
    
    def has_favorite_by_user(self, user):
        if not user.is_authenticated():
            return False
        return FavoriteQuestion.objects.filter(question=self, user=user).count() > 0
        
    def get_answer_count_by_user(self, user_id):
        query_set = Answer.objects.filter(author__id=user_id)
        return query_set.filter(question=self).count()       
    
    def get_question_title(self):
        return u'%s %s' % (self.title, CONST['closed']) if self.closed else self.title
        
    def get_revision_url(self):
        return reverse('question_revisions', args=[self.id])

    def get_latest_revision(self):
        return self.revisions.all()[0]    
        
    def __unicode__(self):
        return self.title
        
    class Meta:
        db_table = u'question'

class QuestionRevision(models.Model):
    """A revision of a Question."""
    question   = models.ForeignKey(Question, related_name='revisions')
    revision   = models.PositiveIntegerField(blank=True)
    title      = models.CharField(max_length=300)
    author     = models.ForeignKey(User, related_name='question_revisions')
    revised_at = models.DateTimeField()
    tagnames   = models.CharField(max_length=125)
    summary    = models.CharField(max_length=300, blank=True)
    text       = models.TextField()

    class Meta:
        db_table = u'question_revision'
        ordering = ('-revision',)

    def get_question_title(self):
        return self.question.title
        
    def get_absolute_url(self):
        return '/questions/%s/revisions' % (self.question.id)
        
    def save(self, **kwargs):
        """Looks up the next available revision number."""
        if not self.revision:
            self.revision = QuestionRevision.objects.filter(
                question=self.question).values_list('revision',
                                                    flat=True)[0] + 1
        super(QuestionRevision, self).save(**kwargs)

    def __unicode__(self):
        return u'revision %s of %s' % (self.revision, self.title)
        
class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers')
    author   = models.ForeignKey(User, related_name='answers')
    added_at = models.DateTimeField(default=datetime.datetime.now)
    # Status
    wiki        = models.BooleanField(default=False)
    wikified_at = models.DateTimeField(null=True, blank=True)
    accepted    = models.BooleanField(default=False)
    deleted     = models.BooleanField(default=False)
    deleted_by  = models.ForeignKey(User, null=True, blank=True, related_name='deleted_answers')
    locked      = models.BooleanField(default=False)
    locked_by   = models.ForeignKey(User, null=True, blank=True, related_name='locked_answers')
    locked_at   = models.DateTimeField(null=True, blank=True)
    # Denormalised data
    score                = models.IntegerField(default=0)
    vote_up_count        = models.IntegerField(default=0)
    vote_down_count      = models.IntegerField(default=0)
    comment_count        = models.PositiveIntegerField(default=0)
    offensive_flag_count = models.SmallIntegerField(default=0)
    last_edited_at       = models.DateTimeField(null=True, blank=True)
    last_edited_by       = models.ForeignKey(User, null=True, blank=True, related_name='last_edited_answers')
    html                 = models.TextField()
    comments             = generic.GenericRelation(Comment)
    votes                = generic.GenericRelation(Vote)
    flagged_items        = generic.GenericRelation(FlaggedItem)
    
    objects = AnswerManager()
    
    def get_user_vote(self, user):
        votes = self.votes.filter(user=user)
        if votes.count() > 0:
            return votes[0]
        else:
            return None
            
    def get_latest_revision(self):
        return self.revisions.all()[0]  
        
    def get_question_title(self):
        return self.question.title
        
    def get_absolute_url(self):
        return '%s%s#%s' % (reverse('question', args=[self.question.id]), self.question.title, self.id)
        
    class Meta:
        db_table = u'answer'
        
    def __unicode__(self):
        return self.html    

class AnswerRevision(models.Model):
    """A revision of an Answer."""
    answer     = models.ForeignKey(Answer, related_name='revisions')
    revision   = models.PositiveIntegerField()
    author     = models.ForeignKey(User, related_name='answer_revisions')
    revised_at = models.DateTimeField()
    summary    = models.CharField(max_length=300, blank=True)
    text       = models.TextField()

    def get_absolute_url(self):
        return '/answers/%s/revisions' % (self.answer.id)
        
    def get_question_title(self):
        return self.answer.question.title
        
    class Meta:
        db_table = u'answer_revision'
        ordering = ('-revision',)

    def save(self, **kwargs):
        """Looks up the next available revision number if not set."""
        if not self.revision:
            self.revision = AnswerRevision.objects.filter(
                answer=self.answer).values_list('revision',
                                                flat=True)[0] + 1
        super(AnswerRevision, self).save(**kwargs)
        
class FavoriteQuestion(models.Model):
    """A favorite Question of a User."""
    question      = models.ForeignKey(Question)
    user          = models.ForeignKey(User, related_name='user_favorite_questions')
    added_at = models.DateTimeField(default=datetime.datetime.now)
    class Meta:
        db_table = u'favorite_question'
    def __unicode__(self):
        return '[%s] favorited at %s' %(self.user, self.added_at)
    
class Badge(models.Model):
    """Awarded for notable actions performed on the site by Users."""
    GOLD = 1
    SILVER = 2
    BRONZE = 3
    TYPE_CHOICES = (
        (GOLD,   u'Gold'),
        (SILVER, u'Silver'),
        (BRONZE, u'Broze'),
    )

    name        = models.CharField(max_length=50)
    type        = models.SmallIntegerField(choices=TYPE_CHOICES)
    slug        = models.SlugField(max_length=50, blank=True)
    description = models.CharField(max_length=300)
    multiple    = models.BooleanField(default=False)
    # Denormalised data
    awarded_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = u'badge'
        ordering = ('name',)
        unique_together = ('name', 'type')

    def __unicode__(self):
        return u'%s: %s' % (self.get_type_display(), self.name)

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Badge, self).save(**kwargs)

    def get_absolute_url(self):
        return '%s%s/' % (reverse('badge', args=[self.id]), self.slug)

class Award(models.Model):
    """The awarding of a Badge to a User."""
    user       = models.ForeignKey(User)
    badge      = models.ForeignKey(Badge)
    awarded_at = models.DateTimeField(default=datetime.datetime.now)
    notified   = models.BooleanField(default=False)
    
    class Meta:
        db_table = u'award'

class Repute(models.Model):
    """The reputation histories for user"""
    user     = models.ForeignKey(User)
    positive = models.SmallIntegerField(default=0)
    negative = models.SmallIntegerField(default=0)
    question = models.ForeignKey(Question)
    reputed_at = models.DateTimeField(default=datetime.datetime.now)
    reputation_type = models.SmallIntegerField(choices=TYPE_REPUTATION)
    reputation = models.IntegerField(default=1)
    objects = ReputeManager()
    
    class Meta:
        db_table = u'repute'

class Activity(models.Model):
    """
    We keep some history data for user activities
    """
    user = models.ForeignKey(User)
    activity_type = models.SmallIntegerField(choices=TYPE_ACTIVITY)
    active_at = models.DateTimeField(default=datetime.datetime.now)
    content_type   = models.ForeignKey(ContentType)
    object_id      = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        db_table = u'activity'
    
# User extend properties
QUESTIONS_PER_PAGE_CHOICES = (
   (10, u'10'),
   (30, u'30'),
   (50, u'50'),
)

User.add_to_class('reputation', models.PositiveIntegerField(default=1))
User.add_to_class('gravatar', models.CharField(max_length=32))
User.add_to_class('favorite_questions',
                  models.ManyToManyField(Question, through=FavoriteQuestion,
                                         related_name='favorited_by'))
User.add_to_class('badges', models.ManyToManyField(Badge, through=Award,
                                                   related_name='awarded_to'))
User.add_to_class('gold', models.SmallIntegerField(default=0))
User.add_to_class('silver', models.SmallIntegerField(default=0))
User.add_to_class('bronze', models.SmallIntegerField(default=0))
User.add_to_class('questions_per_page',
                  models.SmallIntegerField(choices=QUESTIONS_PER_PAGE_CHOICES, default=10))
User.add_to_class('last_seen',
                  models.DateTimeField(default=datetime.datetime.now))
User.add_to_class('real_name', models.CharField(max_length=100, blank=True))
User.add_to_class('website', models.URLField(max_length=200, blank=True))
User.add_to_class('location', models.CharField(max_length=100, blank=True))
User.add_to_class('date_of_birth', models.DateField(null=True, blank=True))
User.add_to_class('about', models.TextField(blank=True))   

def get_profile_url(self):
    """Returns the URL for this User's profile."""
    return '%s%s/' % (reverse('user', args=[self.id]), self.username)
User.add_to_class('get_profile_url', get_profile_url)
    
def calculate_gravatar_hash(instance, **kwargs):
    """Calculates a User's gravatar hash from their email address."""
    if kwargs.get('raw', False):
        return
    instance.gravatar = hashlib.md5(instance.email).hexdigest()

def record_ask_event(instance, created, **kwargs):
    if created:
        activity = Activity(user=instance.author, active_at=instance.added_at, content_object=instance, activity_type=1)
        activity.save()
def record_answer_event(instance, created, **kwargs):
    if created:
        activity = Activity(user=instance.author, active_at=instance.added_at, content_object=instance, activity_type=2)
        activity.save()    
def record_comment_event(instance, created, **kwargs):
    if created:
        from django.contrib.contenttypes.models import ContentType
        question_type = ContentType.objects.get_for_model(Question)
        question_type_id = question_type.id
        type = 3 if instance.content_type_id == question_type_id else 4
        activity = Activity(user=instance.user, active_at=instance.added_at, content_object=instance, activity_type=type)
        activity.save() 
def record_revision_question_event(instance, created, **kwargs):
    if created and instance.revision <> 1:
        activity = Activity(user=instance.author, active_at=instance.revised_at, content_object=instance, activity_type=5)
        activity.save()   
def record_revision_answer_event(instance, created, **kwargs):
    if created and instance.revision <> 1:
        activity = Activity(user=instance.author, active_at=instance.revised_at, content_object=instance, activity_type=6)
        activity.save()         
def record_award_event(instance, created, **kwargs):
    if created:
        activity = Activity(user=instance.user, active_at=instance.awarded_at, content_object=instance, activity_type=7)
        activity.save()  
def record_answer_accepted(instance, created, **kwargs):
    """
    when answer is accepted, we record it from data of reputation
    """
    if instance.reputation_type == 2:
        activity = Activity(user=instance.user, active_at=instance.reputed_at, content_object=instance, activity_type=8)
        activity.save() 
        
#signal for User modle save changes
pre_save.connect(calculate_gravatar_hash, sender=User)        
post_save.connect(record_ask_event, sender=Question)
post_save.connect(record_answer_event, sender=Answer)
post_save.connect(record_comment_event, sender=Comment)
post_save.connect(record_revision_question_event, sender=QuestionRevision)
post_save.connect(record_revision_answer_event, sender=AnswerRevision)
post_save.connect(record_award_event, sender=Award)
post_save.connect(record_answer_accepted, sender=Repute)
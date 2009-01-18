#-------------------------------------------------------------------------------
# Name:        Award badges command
# Purpose:     This is a command file croning in background process regularly to
#              query database and award badges for user's special acitivities.
#
# Author:      Mike
#
# Created:     18/01/2009
# Copyright:   (c) Mike 2009
# Licence:     GPL V2
#-------------------------------------------------------------------------------
#!/usr/bin/env python
#encoding:utf-8
from datetime import datetime, date
from django.core.management.base import NoArgsCommand
from django.db import connection
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from forum.models import *
from forum.const import *
"""
(7, '巡逻兵', 3, '巡逻兵', '第一次标记垃圾帖子', 0, 0),
(8, '清洁工', 3, '清洁工', '第一次撤销投票', 0, 0),
(9, '批评家', 3, '批评家', '第一次反对票', 0, 0),
(10, '小编', 3, '小编', '第一次编辑更新', 0, 0),
(11, '村长', 3, '村长', '第一次重新标签', 0, 0),
(12, '学者', 3, '学者', '第一次标记答案', 0, 0),
(13, '学生', 3, '学生', '第一次提问并且有一次以上赞成票', 0, 0),
(14, '支持者', 3, '支持者', '第一次赞成票', 0, 0),
(15, '教师', 3, '教师', '第一次回答问题并且得到一个以上赞成票', 0, 0),
(16, '自传作者', 3, '自传作者', '完整填写用户资料所有选项', 0, 0),


TYPE_ACTIVITY_ASK_QUESTION=1
TYPE_ACTIVITY_ANSWER=2
TYPE_ACTIVITY_COMMENT_QUESTION=3
TYPE_ACTIVITY_COMMENT_ANSWER=4
TYPE_ACTIVITY_UPDATE_QUESTION=5
TYPE_ACTIVITY_UPDATE_ANSWER=6
TYPE_ACTIVITY_PRIZE=7
TYPE_ACTIVITY_MARK_ANSWER=8
TYPE_ACTIVITY_VOTE_UP=9
TYPE_ACTIVITY_VOTE_DOWN=10
TYPE_ACTIVITY_CANCEL_VOTE=11
TYPE_ACTIVITY_DELETE_QUESTION=12
TYPE_ACTIVITY_DELETE_ANSWER=13
TYPE_ACTIVITY_MARK_OFFENSIVE=14
TYPE_ACTIVITY_UPDATE_TAGS=15
TYPE_ACTIVITY_FAVORITE=16
TYPE_ACTIVITY_EDIT_QUESTION=17
TYPE_ACTIVITY_EDIT_ANSWER=18
"""
class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        try:
            clean_awards()
            alpha_user()
            first_mark_offensive()
        except Exception, e:
            print e

def alpha_user():
    """
    Before Jan 25, 2009(Chinese New Year Eve and enter into Beta for CNProg), every registered user
    will be awarded the "Alpha" badge if he has any activities.
    """
    alpha_end_date = date(2009, 1, 25)
    if date.today() < alpha_end_date:
        badge = get_object_or_404(Badge, id=22)
        for user in User.objects.all():
            award = Award.objects.filter(user=user, badge=badge)
            if award and not badge.multiple:
                continue
            activities = Activity.objects.filter(user=user)
            if len(activities) > 0:
                new_award = Award(user=user, badge=badge)
                new_award.save()

def first_mark_offensive():
    activities = Activity.objects.filter(activity_type=TYPE_ACTIVITY_MARK_OFFENSIVE, is_auditted=False)
    activities.query.group_by = ['user_id']
    badge = get_object_or_404(Badge, id=7)
    for act in activities:
        award = Award.objects.filter(user=act.user, badge=badge)
        if award and not badge.multiple:
            continue
        new_award = Award(user=act.user, badge=badge)
        new_award.save()


def clean_awards():
    Award.objects.all().delete()

    award_type =ContentType.objects.get_for_model(Award)
    Activity.objects.filter(content_type=award_type).delete()

    for user in User.objects.all():
        user.gold = 0
        user.silver = 0
        user.bronze = 0
        user.save()

    for badge in Badge.objects.all():
        badge.awarded_count = 0
        badge.save()

def main():
    pass

if __name__ == '__main__':
    main()
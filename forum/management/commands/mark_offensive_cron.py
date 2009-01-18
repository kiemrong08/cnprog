from django.core.management.base import NoArgsCommand
from django.db import connection
from django.shortcuts import get_object_or_404

from forum.models import *
from forum.const import *

class Command(NoArgsCommand):
    def handle_noargs(self, **options): 
        cursor = connection.cursor()
        cursor.execute("SELECT count(*) offensive_count, user_id \
            FROM activity WHERE is_auditted=0 AND activity_type=%s GROUP BY user_id", [TYPE_ACTIVITY_MARK_OFFENSIVE])
        rows = cursor.fetchall()
        for row in rows:
            user_id = row[1]
            user = get_object_or_404(User, id=user_id)
            # id 7
            badge = get_object_or_404(Badge, id=7)
            multiple = badge.multiple
            # check the user whether has the badge before
            if not multiple:
                count = Award.objects.filter(user=user, badge=badge).count()
                if count:
                    return
            
            # new award
            award = Award(user=user, badge=badge)
            # update badge
            badge.awarded_count += 1
            # update user info
            if badge.type == Badge.GOLD:
                user.gold += 1
            elif badge.type == Badge.SILVER:
                user.sliver += 1
            else:
                user.bronze += 1
            
            award.save()
            badge.save()
            user.save()
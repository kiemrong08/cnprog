from django.contrib.auth.models import User, UserManager
from django.db import connection, models, transaction
from django.db.models import Q
from forum.models import *

import logging

class QuestionManager(models.Manager):
    def update_tags(self, question, tagnames, user):
        """
        Updates Tag associations for a question to match the given
        tagname string.

        Returns ``True`` if tag usage counts were updated as a result,
        ``False`` otherwise.
        """
        current_tags = list(question.tags.all())
        current_tagnames = set(t.name for t in current_tags)
        updated_tagnames = set(t for t in tagnames.split(' ') if t)
        modified_tags = []

        removed_tags = [t for t in current_tags
                        if t.name not in updated_tagnames]
        if removed_tags:
            modified_tags.extend(removed_tags)
            question.tags.remove(*removed_tags)

        added_tagnames = updated_tagnames - current_tagnames
        if added_tagnames:
            added_tags = Tag.objects.get_or_create_multiple(added_tagnames,
                                                            user)
            modified_tags.extend(added_tags)
            question.tags.add(*added_tags)

        if modified_tags:
            Tag.objects.update_use_counts(modified_tags)
            return True

        return False

    def update_answer_count(self, question):
        """
        Executes an UPDATE query to update denormalised data with the
        number of answers the given question has.
        """
        logging.debug('execute update_answer_count')
        # for some reasons, this Answer class failed to be imported,
        # although we have imported all classes from models on top.
        from forum.models import Answer
        self.filter(id=question.id).update(
            answer_count=Answer.objects.get_answers_from_question(question).count())
        

class TagManager(models.Manager):
    UPDATE_USED_COUNTS_QUERY = (
        'UPDATE tag '
        'SET used_count = ('
            'SELECT COUNT(*) FROM question_tags '
            'WHERE tag_id = tag.id'
        ') '
        'WHERE id IN (%s)')

    def get_or_create_multiple(self, names, user):
        """
        Fetches a list of Tags with the given names, creating any Tags
        which don't exist when necesssary.
        """
        tags = list(self.filter(name__in=names))
        if len(tags) < len(names):
            existing_names = set(tag.name for tag in tags)
            new_names = [name for name in names if name not in existing_names]
            tags.extend([self.create(name=name, created_by=user)
                         for name in new_names])
        return tags

    def update_use_counts(self, tags):
        """Updates the given Tags with their current use counts."""
        if not tags:
            return
        cursor = connection.cursor()
        query = self.UPDATE_USED_COUNTS_QUERY % ','.join(['%s'] * len(tags))
        cursor.execute(query, [tag.id for tag in tags])
        transaction.commit_unless_managed()

class AnswerManager(models.Manager):
    def get_answers_from_question(self, question, user=None):
        """
        Retrieves visibile answers for the given question. Delete answers
        are only visibile to the person who deleted them.
        """
        logging.debug('execute AnswerManager')
        if user is None or not user.is_authenticated():
            return self.filter(question=question, deleted=False)
        else:
            return self.filter(Q(question=question),
                               Q(deleted=False) | Q(deleted_by=user))

class VoteManager(models.Manager):
    # TODO: Check vote value: 0 down, 1 up
    COUNT_UP_VOTE_BY_USER = "SELECT count(*) FROM vote WHERE user_id = %s AND vote = 1"
    COUNT_DOWN_VOTE_BY_USER = "SELECT count(*) FROM vote WHERE user_id = %s AND vote = 0"
    
    def get_up_vote_count_from_user(self, user):
        if user is not None:
            cursor = connection.cursor()
            cursor.execute(self.COUNT_UP_VOTE_BY_USER, [user.id])
            row = cursor.fetchone()
            return row
        else:
            return 0
    
    def get_down_vote_count_from_user(self, user):
        if user is not None:
            cursor = connection.cursor()
            cursor.execute(self.COUNT_DOWN_VOTE_BY_USER, [user.id])
            row = cursor.fetchone()
            return row
        else:
            return 0
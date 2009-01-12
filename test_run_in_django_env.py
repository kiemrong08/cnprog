from forum.models import Comment
class CronProcess(object):        
    def run(self):
        objs = Comment.objects.all()
        print objs
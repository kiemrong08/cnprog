#!/usr/bin/env python
import sys
from django.core.management import setup_environ

def load_class(clazz):
    return getattr(__import__(clazz,
                   {}, {}, ['CronProcess']), 'CronProcess')()

try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)
            
setup_environ(settings)
# python run_in_dango_env.py test_run_in_django_env
if len(sys.argv) == 1:
    print 'usage: python run_in_dango_env.py file_name, sample:python run_in_dango_env.py test_run_in_django_env'
else:
    instance = load_class(sys.argv[1])
    instance.run()
    

        
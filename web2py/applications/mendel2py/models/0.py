'''
Created on May 1, 2013

@author: tgambin
'''

from gluon.storage import Storage
settings = Storage()

settings.migrate = True
settings.title = 'Variant Analyzer'
#settings.subtitle = 'powered by web2py'
settings.author = 'Tomasz Gambin'
settings.author_email = 'gambin@bcm.edu'
settings.keywords = ''
settings.description = ''
settings.layout_theme = 'Default'
settings.database_uri = 'sqlite://storage.sqlite'
settings.security_key = '9cb97b0c-159a-42d8-9776-4f2daab71d2c'
settings.email_server = 'localhost'
settings.email_sender = 'you@example.com'
settings.email_login = ''
settings.login_method = 'local'
settings.login_config = ''
settings.plugins = []

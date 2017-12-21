'''
Created on May 1, 2013

@author: tgambin
'''

exec("from applications.%s.modules.utils import *" % request.application)

def index():
    
    if isAdmin(db, auth):
        res = SQLFORM.grid(db.project_data)
    else: 
        res = None
    return dict(res = res,)
    
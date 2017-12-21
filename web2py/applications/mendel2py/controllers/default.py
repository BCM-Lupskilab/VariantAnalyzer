# -*- coding: utf-8 -*-
'''
Created on May 1, 2013

@author: tgambin
'''

### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires
def index():
    return dict(ttt="testMessage")




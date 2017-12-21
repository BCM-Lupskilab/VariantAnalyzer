'''
Created on May 1, 2013

@author: tgambin
'''

import applications.mendel2py.modules.commonForms as commonForms


@auth.requires_login()
@auth.requires_membership('lupskilab')
def index():
    query=db.bab_data    
    sample_create = SQLFORM.grid(query, deletable = False)#, left=left)
    return dict(sample_create=sample_create)
    
'''
Created on May 1, 2013

@author: tgambin
'''

exec("from applications.%s.modules.utils import *" % request.application)
import applications.mendel2py.modules.commonForms as commonForms
from applications.mendel2py.modules.utils import *

appDir = request.folder
rDir =   "~/workspace/variant_analyzer/r_scripts/"
rpkmDir = "/home/va/data/RPKM/"
snpDir= "/home/va/data/cSNP/"
aohPlotsDir = "/home/va/data/aoh_cnv_plots/"
cnvPlotsDir = "/home/va/data/conifer_output/call_images/"

ll_XlsDir = "/home/va/data/ll_xls/"
uploadDir = appDir + "uploads/"
outputDir = appDir + "output/"
r = robjects.r
r.source(rDir + "getTrackingDump.R")
r.source(rDir + "aoh_cnv.R")

import csv
import rpy2.robjects as robjects
import os
import gc


@auth.requires_login()
@auth.requires_membership('mendel')
def index():
    
    
    query = (db.request_data.user_id == auth.user )
    if isAdmin(db, auth): 
        query = (db.request_data.id > 0)
    
    requestForm = SQLFORM.grid(query, 
                                deletable =True,
                                editable = True,
                                #maxtextlength=maxtextlength,
                                paginate=1000000000000,
                                search_widget=None,
                                create=True,
                                overflowauto="",
                                sortable=False
                                #links = [lambda row: 'eblebl']# INPUT('First pass',_type="checkbox", id ="first_pass_" )],
                                )
    return(dict(requestForm=requestForm))



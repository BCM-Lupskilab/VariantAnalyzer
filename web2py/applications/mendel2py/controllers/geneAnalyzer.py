'''
Created on May 1, 2013

@author: tgambin
'''

import rpy2.robjects as robjects
import os

appDir = request.folder
rDir =   "/home/va/workspace/variant_analyzer/r_scripts/"
uploadDir = appDir + "uploads/"
outputDir = appDir + "output/"
r = robjects.r
r.source(rDir + "analyzeGene.R")

@auth.requires_login()
@auth.requires_membership('lupskilab')
def downloadFile():
    from gluon.contenttype import contenttype
    response.headers['Content-Type'] = contenttype('application/octet-stream')
    print request.vars.path
    response.headers['Content-Disposition'] =  'attachment; filename="'+(request.vars.path.split("/")[-1])+'"'
    return response.stream(open(request.vars.path,'rb'),chunk_size=4096)


@auth.requires_login()
@auth.requires_membership('lupskilab')
def onFilter(form):
    gene =  request.vars.gene_name
    ff = uploadDir +  gene.split(",")[0] + "_and_others.csv"    
    r.analyzeGene(gene, ff) 
    redirect(URL('downloadFile',vars=dict(path=ff)))
    pass

@auth.requires_login()
@auth.requires_membership('lupskilab')
def index():
    #pass
    import gc;
    gc.collect()
    input_form = crud.create(db.gene_analyzer_data, onaccept = onFilter)
    return dict(input_form = input_form)


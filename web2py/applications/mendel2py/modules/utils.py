'''
Created on May 29, 2009

@author: tgambin, macieksk
'''


import re
import string
import gzip
import rpy2.robjects as robjects

from gluon.tools import redirect
from gluon.html import URL
from gluon.sqlhtml import *

from applications.mendel2py.modules.Config import Config
import applications.mendel2py.modules.imidlog as imidlog

g_default_threshold = 0.14

g_interval_data_types = {'int_refseq_gene':0 , 'int_refseq_exon':1, 
                       'int_toronto_cnv':2, 'probe':3 , 'acgh_segment':4}
g_global_step = 40 # Global number of records shown on one page

def isAdmin(db, auth):
    res = db((db.auth_membership.user_id == auth.user)&
       (db.auth_group.id  == db.auth_membership.group_id)&
       (db.auth_group.role == "admin" )).select(db.auth_group.ALL)
    print (res)
    return (len(res )> 0)


def isLL(db, auth):
    res = db((db.auth_membership.user_id == auth.user)&
       (db.auth_group.id  == db.auth_membership.group_id)&
       (db.auth_group.role == "lupskilab" )).select(db.auth_group.ALL)
    print (res)
    return (len(res )> 0)

def isLLXLS(db, auth):
    res = db((db.auth_membership.user_id == auth.user)&
       (db.auth_group.id  == db.auth_membership.group_id)&
       (db.auth_group.role == "llxls" )).select(db.auth_group.ALL)
    print (res)
    return (len(res )> 0)


def strip_path_and_sanitize(path):
    pre=re.compile(r'[/\\:]')
    return pre.split(path)[-1]


def validateVariableName(var):
    from pylint.checkers import tokenize
    pattern = re.compile(tokenize.Name)
    return True if re.match(pattern, var) else False


def leaveAlphaNumAnd(strToParse,otherLetters='-_.()'):
    #Removes all non alphanumeric characters, leaving possibly letters give as arguments
    valid_chars = "%s%s%s" % (otherLetters,string.ascii_letters, string.digits)
    return ''.join(c for c in strToParse if c in valid_chars)


#################################3
############## SQLTABLE MODIFICATIONS AND USAGE

def addColumnToSQLTABLE_old(stab,data,title,**thargs):
    stab[0][0].append(TH(title,**thargs))
    #Modify each row
    for tr,fs in zip(stab[1],data): 
        tr.append(TD(fs))
    return stab


def addColumnToSQLTABLE(stab,data,title,**thargs):
    stab[1][0][0][0][0].append(TH(title,**thargs)); 
    for tr,fs in zip(stab[1][0][0][1],data):            tr.append(TD(fs));    
    return stab

def removeColumnFromSQLTABLE(stab,colNo):
  #  import pdb;pdb.set_trace()
    stab[0][0].components = stab[0][0].components[0:colNo]+stab[0][0].components[colNo+1:]
    remCol=[tr.components[colNo] for tr in stab[1]]
    for tr in stab[1]: 
        tr.components = tr.components[0:colNo]+tr.components[colNo+1:]
    return remCol

def getColumnNumberFromSQLTABLE(stab,title=None, cmpFun=None):
    return [i for i,th in enumerate(stab[0][0]) if cmpFun(th[0],title)][0]


def transformColumnFromSQLTABLE(stab,colNo,transFun):
  #  import pdb;pdb.set_trace()
    for tr in stab[1]: 
        tr.components[colNo][0] = transFun(tr.components[colNo][0])
    return stab

def columnIteratorFromSQLTABLE(stab,colNo):
  #  import pdb;pdb.set_trace()
    for tr in stab[1]: 
        yield tr.components[colNo]
    pass


def handleQueryForTableView(session,request,db,def_orderby,query,selectArgs,step=5,doCount=True,**args):
    if request.vars.start:
        start = int(request.vars.start)
    else:
        start = 0
    stop = start + step
    nrows = None
    rows = []
    orderby = request.vars.orderby
    if orderby:
        if orderby[0] == '~': orderby = '~db.'+orderby[1:]
        else: orderby='db.'+orderby
        #if orderby == session.last_orderby:
        #    if orderby[0] == '~': orderby = orderby[1:]
        #    else:  orderby = '~' + orderby
    else: orderby=def_orderby                         
    session.last_orderby = orderby
    if doCount: nrows = db(*query).count()
    if orderby:
        args.update(dict(orderby=eval(orderby),limitby=(start, stop)))   
    else: 
        args.update( dict(limitby=(start, stop)))
    rows = db(*query).select(*selectArgs,**args)       
    orderby=re.sub("db\.","",orderby)
    prevLink = A('prev %d rows' % step, #% ((start-step if start-step>0 else 0),(start-step if start-step>0 else 0)+step),
                 _href=URL(r=request,vars=dict(orderby=orderby,start=max(start-step,0)))) if start>0 else None 
    nextLink = A('next %d rows' % step, #((start+step),(start+step+step)),
                 _href=URL(r=request,vars=dict(orderby=orderby,start=start+step))) if (stop<nrows) | (nrows==None) else None  
    return dict(records=rows,prevLink=prevLink,
                 nextLink=nextLink,nrows=nrows,start=start,stop=stop)


#########################################3

def i2chr(i):
    if (int(i) == 23):
        ret = 'X'
    elif (int(i) == 24):
        ret = 'Y'
    elif ( int(i) == 25):
        ret = 'M'
    else:
        ret = str(i)
    return 'chr' + ret


def chr2i(chr):
    chr = chr[3:].upper()
    if (chr == "X"):
        return 23
    if (chr == "Y"):
        return 24
    if (chr == "M"):
        return 25    
    try:
        return int(chr)
    except ValueError:
        return None
    return None


def systematicName2Interval(name):
    tab = name.split(':')
    if (len(tab) != 2):
        return None
    chr = chr2i(tab[0])
    tab2 = tab[1].split('-')
    if (len(tab2) != 2):
        return None
    start = int(tab2[0])
    stop = int(tab2[1])
    if (start > stop):
        start = int(tab2[1])
        stop = int(tab2[0])
    return (chr, start , stop)



def readAgilent(fileName, utilsRPath):
    #r = robjects.r
    #read_table = r("read.table");
    #m = read_table(fileName , sep = "\t" , skip = 9, header=True)
    
    r = robjects.r
    r.source( utilsRPath)
    d2 = r.readAllSamples(fileName)
    
    dataf = robjects.r['data.frame'](d2)
        
    return dataf


def calcDlrsd(dataf , qualityMeasuresRPath):
    r = robjects.r
    r.source( qualityMeasuresRPath)
    return (r.dlrsd(dataf)[0])
    
    

def getFormField(form,rowName,fieldClass):
    trow = filter(lambda f: f.attributes['_id']=='%s_%s__row' % (form.table._tablename,rowName),form[0])[0]
    finp = filter(lambda td:isinstance(td[0],fieldClass) if len(td)>0 else False,trow)[0][0]
    return finp

def getFormRow(form,rowName,fieldClass):
    trow = filter(lambda f: f.attributes['_id']=='%s_%s__row' % (form.table._tablename,rowName),form[0])[0]
    finp = filter(lambda td:isinstance(td[0],fieldClass) if len(td)>0 else False,trow)
    return finp


def getFormSubmitButtonTD(form):
    return filter(lambda f: f.attributes['_id']=='submit_record__row',form[0])[0]

            
#class IS_IN_DB_ORNULL(IS_IN_DB):
#    def build_set(self):
#        IS_IN_DB.build_set(self)
#        self.theset.insert(0,None) 
#        self.labels.insert(0,'None')
#        pass
#    def __call__(self, value): 
#        #print(type(value))
#        if value=='None':
#            return (value, None)
#        return IS_IN_DB.__call__(self, value)
#    
#    pass
#
#        

def addOverlaps(db,interval_id): #,exp_id=None):
    return 0

#    #Old Code
#    counter = 0
#    intervals = db(db.interval_data.id == interval_id).select(db.interval_data.ALL)
#    if (len(intervals) > 0):
#        id =  intervals[0].id
#        chr = intervals[0].chr
#        start = intervals[0].start
#        stop = intervals[0].stop
#        type =  intervals[0].type
#            
#        #g_interval_data_types = {'int_refseq_gene':0 , 'int_refseq_exon':1, 
#        #               'int_toronto_cnv':2, 'probe':3 , 'acgh_segment':4}
#        segmentType = g_interval_data_types['acgh_segment']
#        
#        overlappedWithSegmentTypes = [g_interval_data_types['int_refseq_gene'],
#                           g_interval_data_types['int_toronto_cnv']]
#        
#        
#        
#        if (type == segmentType):
#            overlappingIntervals = db((db.interval_data.type.belongs(overlappedWithSegmentTypes))&
#                                      (db.interval_data.chr == chr) &
#                                      (db.interval_data.start <= stop) &
#                                      (db.interval_data.stop >= start) ).select(db.interval_data.id)
#
#               
#        elif type in overlappedWithSegmentTypes:
#            overlappingIntervals = db((db.interval_data.type == segmentType)&
#                                      (db.interval_data.chr == chr) &
#                                      (db.interval_data.start <= stop) &
#                                      (db.interval_data.stop >= start) ).select(
#                                                        db.interval_data.id) 
#        else:
#            overlappingIntervals = []
#        
#        for oInterval in overlappingIntervals:       
#            # add into interval overlap symmetrical records
#            db.interval_overlap.insert(interval_id_1 = id , interval_id_2 =oInterval.id)
#            db.interval_overlap.insert(interval_id_1 = oInterval.id , interval_id_2 = id )
#            counter = counter + 1 
#         
#    return counter
       
    
    
def insertFileIntoTable(dbtable,fileFieldName,source_file,
                        original_filename,
                        **otherFields): # in particular add (original) filename in otherFields
                
    fileField = dbtable[fileFieldName]    
    newfilename = fileField.store(source_file, original_filename)
    insertFields = {}            
    insertFields[fileFieldName]=newfilename        
    if fileField.uploadfield and not fileField.uploadfield==True:
        insertFields[fileField.uploadfield] = source_file.read()
        
    insertFields.update(otherFields)    
               
    newid = dbtable.insert(**insertFields)
    return newid
        
    
def updateFileIntoTable(recordId,dbtable,fileFieldName,source_file,
                        original_filename,
                        **otherFields): # in particular add (original) filename in otherFields            
    fileField = dbtable[fileFieldName]    
    newfilename = fileField.store(source_file, original_filename)
    insertFields = {}            
    insertFields[fileFieldName]=newfilename        
    if fileField.uploadfield and not fileField.uploadfield==True:
        insertFields[fileField.uploadfield] = source_file.read()
        
    insertFields.update(otherFields)    
    
    db=dbtable._db           
    db(dbtable.id==recordId).update(**insertFields)
    return recordId
        
def redirect404(request,**errorDict):
    return redirect(URL(r=request,c='error404',f='index',vars=errorDict))

def recalcAberrationClassForExp(db, expId=None,segmId=None):
    if not segmId:
        segmId = db.acgh_experiment[expId].main_segm_id
    if not expId:
        expId = db.acgh_segmentation[segmId].acgh_exp_id
                
    mainmsg = "fixAberrationClassForSegmentation(expId=%d, segmId=%d)"%(expId,segmId)                 
    imidlog.log(mainmsg)    
    rconf = db(db.result_config.acgh_exp_id == expId).select(db.result_config.ALL)
    if len(rconf)==0: 
        imidlog.log(mainmsg+" ?? no rconf for this exp!!!")
        return mainmsg+" ?? no rconf for this exp!!!"
    rconf = rconf[0]
    
    mainmsg = mainmsg+" rconf thresholds are: (%f,%f) "%(rconf.minus_min_l2r_mean,rconf.plus_min_l2r_mean)
    imidlog.log(mainmsg)
    
    for i,segment in enumerate(db(db.acgh_segment.segmentation_id==segmId).select(db.acgh_segment.id,db.acgh_segment.l2r_mean)):
        if segment.l2r_mean < rconf.minus_min_l2r_mean:     aclass = 'deletion'
        elif segment.l2r_mean > rconf.plus_min_l2r_mean:    aclass = 'duplication'
        else: aclass = 'normal'
        db(db.acgh_segment.id == segment.id).update (aberration_class = aclass)  
    db.commit()
    
    msg = mainmsg+" fixed %d segments"%i
    imidlog.log(msg)
    
    return msg


def orderAccordingToDict(toOrder,orderDict):
    '''
        Sorts data according to keys provided by a dictionary 
        (dict values are used as keys for sorting)
    '''
    goodOrdering, sortedData = zip(*sorted(enumerate(toOrder),
                    key=lambda (cnt,data):orderDict[data]))
    return goodOrdering, sortedData


    
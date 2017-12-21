'''
Created on May 1, 2013

@author: tgambin
'''

exec("from applications.%s.modules.utils import *" % request.application)
import applications.mendel2py.modules.commonForms as commonForms
from applications.mendel2py.modules.utils import *

appDir = request.folder
rDir =   "/home/va/workspace/variant_analyzer/r_scripts/"
rpkmDir = "/home/va/data/RPKM/"
snpDir= "/home/va/data/cSNP/"
aohPlotsDir = "/home/va/data/aoh_cnv_plots/"
cnvPlotsDir = "/home/va/data/conifer_output/call_images/"
cnvCallsDir = "/home/va/data/cSNP_calls/"

ll_XlsDir = "/home/va/data/ll_xls/"
ll_Xls_v2_Dir = "/home/va/data/ll_xls_v2/"
uploadDir = appDir + "uploads/"
outputDir = appDir + "output/"
r = robjects.r
r.source(rDir + "getTrackingDump.R")
r.source(rDir + "aoh_cnv.R")
r.source(rDir + "doProcessMercury.R")
r.source(rDir + "updateRObject.R")

import csv
import rpy2.robjects as robjects
import os
import gc


@auth.requires_login()
@auth.requires_membership('mendel')
def backup():
    import time
    import os
    from datetime import datetime
    dd =  datetime.now().isoformat()
    os.system("scp /home/va/workspace/variant_analyzer/web2py/applications/mendel2py/databases/storage.sqlite user@server:BACKUP_PATH" + dd)

@auth.requires_login()
@auth.requires_membership('mendel')
def updateAll():
    #make backup
    backup()
    updateSamples()
    processSamples()
    checkAlive()
    downloadVCFs()
    doProcessMercury()
    updateSamples()
    processSamples()
    updateRObject()

@auth.requires_login()
@auth.requires_membership('mendel')
def doProcessMercury():
    if not isAdmin(db, auth):
        return
    r.doProcessMercury()
    

@auth.requires_login()
@auth.requires_membership('mendel')
def updateRObject():
    if not isAdmin(db, auth):
        return
    r.updateRObject()
    
@auth.requires_login()
@auth.requires_membership('mendel')
def checkAliveAndDownload():
    checkAlive()
    downloadVCFs()
    
@auth.requires_login()
@auth.requires_membership('mendel')
def updateSamples():
    if not isAdmin(db, auth):
        return
    else:
        #import system.os
        r.downloadReport(uploadDir + "tmp.csv")
    pass 

@auth.requires_login()
@auth.requires_membership('mendel')
def file_len(full_path):
  """ Count number of lines in a file."""
  f = open(full_path)
  nr_of_lines = sum(1 for line in f)
  f.close()
  return nr_of_lines

@auth.requires_login()
@auth.requires_membership('mendel')
def checkAlive():
    if not isAdmin(db, auth):
        return
    else:
        import os
        samples =  db(db.sample_data.id > 0).select(db.sample_data.ALL)
        for s in samples:
            path  = s.path_server
            if path != "":
                os.system ("ssh  user@server stat " +  path  + " > stat.tmp")
                res =  file_len("stat.tmp") > 1 
                os.system("rm stat.tmp")
                
                print path + ": "  + str(res)
                db(db.sample_data.id == s.id).update(alive=str(res))
                db.commit()
    pass 

@auth.requires_login()
@auth.requires_membership('mendel')
def processSamples():
    csvReader = csv.reader(open(uploadDir + "tmp.csv"), delimiter=',')
    cnt = 0
    for line in csvReader:
     
        print (len(line))
        if len(line) == 28:        
            bab = line[0]
            project = line[2]
            pi = project.split("-")[-1]
            path = line[20]
            ll = line[22]
            #if (ll != "TRUE"): continue 
            projectName = line[23]
            pathServer = path
            raw_snp = line[24]
            raw_indels = line [25]
            xls = line[26]
            xls31 = line[27]
            pathBackup=""
            #if projectName != "Familial Dysautonomia": continue
            
            #import  pdb;pdb.set_trace();
            if (xls != "" and xls != None): cnt = cnt + 1
            print bab + "; " + path + ";" + ll + ";" + projectName
            if len( db(db.project_data.name == projectName).select(db.project_data.ALL)) ==0:
                db.project_data.insert(name = projectName)
            else:
                 db(db.project_data.name == projectName).update(pi = pi)
            db.commit()
       
            project_id = (db(db.project_data.name == projectName).select(db.project_data.id)[0]).id
            current_data = db(db.sample_data.bab_number == bab).select(db.sample_data.ALL)
            
            if len( current_data) ==0:
                db.sample_data.insert(bab_number = bab , 
                                      project_id = project_id,
                                      path_server = pathServer,
                                      raw_snp = raw_snp,
                                      raw_indels = raw_indels,
                                      xls = xls,
                                      xls31 = xls31,
                                      path_backup = pathBackup,
                                      analyst_id = None)
            else:
                if(current_data[0].path_server !=""):
                    print "updating path for " + bab
                    pathServer = current_data[0].path_server                
                if(raw_snp ==""):raw_snp = current_data[0].raw_snp
                if(raw_indels ==""):raw_indels = current_data[0].raw_indels
                if(xls ==""):xls = current_data[0].xls
                if(xls31 ==""):xls31 = current_data[0].xls31
                                
                db(db.sample_data.bab_number == bab).update(   project_id = project_id,
                                                      path_server = pathServer,
                                                      raw_snp = raw_snp,
                                                      raw_indels = raw_indels,
                                                      xls = xls,
                                                      xls31 = xls31)
                                                      #path_backup = pathBackup)
                
            current_data= db(db.sample_data.bab_number == bab).select(db.sample_data.ALL)
            if xls != "" and xls != None and xls != "NA" and ( len(db(db.event_data.sample_data_id == current_data[0],id).select(db.event_data.ALL))==0):
                db.event_data.insert(sample_data_id = current_data[0].id, event_type= 'data_released')
            
            db.commit()
#r.source(rDir + "common.R")

@auth.requires_login()
@auth.requires_membership('mendel')
def downloadVCFs():
    if not isAdmin(db, auth):
        return
    else:
        import os
        samples =  db((db.sample_data.id > 0) & 
                      (db.project_data.id == db.sample_data.project_id)).select(db.sample_data.ALL, db.project_data.ALL)
        for s in samples:
            path  = s.sample_data.path_server
            if (s.sample_data.alive == "True") :
            #if (path != "") :
                try:
                    os.system("mkdir /home/va/data/raw_data/" + s.sample_data.bab_number + "/")
                except:
                    pass
                
                if (s.sample_data.raw_snp == "NA" or s.sample_data.raw_snp == "" or s.sample_data.raw_snp ==None): 
                    os.system ("scp  user@server:" +  s.sample_data.path_server + "/SNP/*_Annotated.vcf  /home/va/data/raw_data/" +s.sample_data.bab_number +  "/")
                    os.system ("bzip2  /home/va/data/raw_data/" +s.sample_data.bab_number +  "/*SNPs_Annotated.vcf")
                if (s.sample_data.raw_indels == "NA" or s.sample_data.raw_indels == "" or s.sample_data.raw_indels==None ): 
                    os.system ("scp  user@server:" +  s.sample_data.path_server + "/INDEL/*_Annotated.vcf  /home/va/data/raw_data/" +s.sample_data.bab_number +  "/")
                    os.system ("bzip2  /home/va/data/raw_data/" +s.sample_data.bab_number +  "/*INDELs_Annotated.vcf")

@auth.requires_login()
@auth.requires_membership('mendel')                        
def test():
    scheduler.queue_task(task_add,pvars=dict(a=1,b=2))

@auth.requires_login()
@auth.requires_membership('mendel')
def download():
        file = request.vars['path']
        print file
        return __download(file, recordEvent=False)

    
    
def __download(file, recordEvent=True):
    import os
    import gluon.contenttype
    filename=(file.split("/"))[-1]
    sampleName = (filename.split("."))[0].replace("_v31", "").replace("_ll", "")
    sampleNames = [id.bab_number for id in db((db.analyst_data.user_id  == auth.user) & (db.sample_data.analyst_id == db.analyst_data.id)).select(db.sample_data.bab_number)]
    print "here:" +  file;
    #import pdb; pdb.set_trace();
    if (sampleName in sampleNames) or isAdmin(db, auth):
        if (recordEvent):
            sample_data_id = (db(db.sample_data.bab_number == sampleName).select(db.sample_data.id))[0].id
            db.event_data.insert(sample_data_id = sample_data_id, event_type='downloaded_by_analyst')
        response.headers['Content-Type']=gluon.contenttype.contenttype(filename)
        response.headers['Content-Disposition'] =  'attachment; filename="'+filename+'"'
        print file;
        #pathfilename=os.path.join("/home/tgambin/Desktop/test")
        return response.stream(open(file,'rb'), chunk_size=10**5)
    return None
        

def __assignSampleAnalyst(form):
     input_file = form.vars.input_file
     ff  =uploadDir + input_file
     analysts =dict()    
     for a in db(db.analyst_data.id > 0).select(db.analyst_data.ALL):
         analysts[str(a.id)] = a.id
     
     csvReader = csv.reader(open(ff), delimiter=',')
     #import pdb; pdb.set_trace()
     for line in csvReader:
         bab = "BAB" + line[0]
         print line
         print (line[1])
         analyst_id = analysts[line[1]]
         #if (len(db(db.sample_data.bab_number == bab).select(db.sample_data.ALL))>0):
         db(db.sample_data.bab_number == bab).update(analyst_id = analyst_id)
    
     db.commit()
         
@auth.requires_login()
@auth.requires_membership('mendel')
def saveFirstPass():
    #import pdb; pdb.set_trace();
    myVars = request.vars;
    id =myVars.pop('sample_id')
    value =myVars.pop('value')
    db(db.sample_data.id == id).update (first_pass=(True if value == 'checked' else False))
    
    if value == 'checked':
        db.event_data.insert(event_type="first_pass_finished",sample_data_id = id)
    db.commit()
    pass
     
@auth.requires_login()
@auth.requires_membership('mendel')
def getAOH_CNV():
    sample_id = request.vars.pop("sample_id")
    analysis_type = request.vars.pop("type")
    bab  = (db(db.sample_data.id == sample_id).select(db.sample_data.bab_number))[0].bab_number
    import os.path
    file = aohPlotsDir + str(bab) +"."+analysis_type+ ".png" 
    if not os.path.isfile(file):
        r.plotAOH(bab, analysis_type, file)
    return __download(file, recordEvent=False)


@auth.requires_login()
@auth.requires_membership('mendel')
def getAOH_snp():
    return getAOH_CNV_snp("aoh")
    
@auth.requires_login()
@auth.requires_membership('mendel')
def getCNV_snp():
    return getAOH_CNV_snp("cnv")
    
@auth.requires_login()
@auth.requires_membership('mendel')
def getAOH_CNV_snp(analysisType):
    sample_id = request.vars.pop("sample_id")
    bab  = (db(db.sample_data.id == sample_id).select(db.sample_data.bab_number))[0].bab_number
    import os.path
    file = aohPlotsDir + str(bab)  + "."+ analysisType+"_cSNP"+".png" 
    if not os.path.isfile(file):
        r.plotAOH_CNV_snp(bab, analysisType, file)
    return __download(file, recordEvent=False)


@auth.requires_login()
#@auth.requires_membership('lupskilab')
@auth.requires(auth.has_membership('lupskilab') or auth.has_membership('llxls')) 
def getXls_ll():
    sample_id = request.vars.pop("sample_id")
    bab  = (db(db.sample_data.id == sample_id).select(db.sample_data.bab_number))[0].bab_number
    import os.path
    file = ll_XlsDir + str(bab)  +"_ll"+".csv" 
    if not os.path.isfile(file):
        r.getXls_ll(bab, file)
    r.gc()
    gc.collect()
    return __download(file, recordEvent=False)


@auth.requires_login()
#@auth.requires_membership('lupskilab')
@auth.requires(auth.has_membership('lupskilab') or auth.has_membership('llxls')) 
def getXls_ll_v2():
    sample_id = request.vars.pop("sample_id")
    bab  = (db(db.sample_data.id == sample_id).select(db.sample_data.bab_number))[0].bab_number
    import os.path
    file = ll_Xls_v2_Dir + str(bab)  +"_filtered_reannotated"+".csv" 
    gc.collect()
    return __download(file, recordEvent=False)


@auth.requires_login()
@auth.requires_membership('mendel')
def getCNV():
    sample_id = request.vars.pop("sample_id")
    bab  = (db(db.sample_data.id == sample_id).select(db.sample_data.bab_number))[0].bab_number
    import os.path
    
    sample2path = dict()
    for x in os.listdir(cnvPlotsDir):
        cbab = "_".join(x.split(".")[0].split("_")[3:])
        if not sample2path.has_key(cbab):
            sample2path[cbab]= []
        sample2path[cbab].append(x)
    
    #import pdb; pdb.set_trace()
    ofile =  cnvPlotsDir  + bab + ".cnv.pdf"
    allchroms = cnvPlotsDir + bab + ".all_chr.png"
    
    allchroms = allchroms if os.path.isfile(allchroms) else ""
    os.system("convert " + allchroms+ " " +  (" ".join([cnvPlotsDir + y for y in sample2path[bab]]) if sample2path.has_key(bab) else "")  + " "+ ofile)
    
    #file = cnvPlotsDir + str(bab) +".png" 
    #if not os.path.isfile(file):
    #    r.plotAOH(bab)
    return __download(ofile, recordEvent=False)

@auth.requires_login()
@auth.requires_membership('mendel')    
def getCNV_calls_snp():
    sample_id = request.vars.pop("sample_id")
    bab  = (db(db.sample_data.id == sample_id).select(db.sample_data.bab_number))[0].bab_number
    import os.path
   
    #import pdb; pdb.set_trace()
    ofile =  cnvCallsDir  + bab + "_cSNP_calls.csv"
    return __download(ofile, recordEvent=False)

@auth.requires_login()
@auth.requires_membership('mendel')
def index():
    
    analyst_assignment = crud.create(db.analyst_assignment, onaccept = __assignSampleAnalyst)
    #hideColumns = ['id', 'user_id', 'dob','doa', 'dos', 'dop', 'decision', 'referral_physician', 'patient_name']
    hideColumns = ['id', 'creation_time', 'path_backup', 'raw_snp', 'raw_indels','alive', 'project_id', 'xls', 'xls31']
    
    showAllColumnsCheckbox=commonForms.giveCheckboxWithState(session,request,'showAllColumns',default="off")
    showAllPatients=commonForms.giveCheckboxWithState(session,request,'showAllPatients',default="off")
    showOnlyWithPaths=commonForms.giveCheckboxWithState(session,request,'showOnlyWithPaths',default="on")
    doNotShowFirstPass=commonForms.giveCheckboxWithState(session,request,'doNotShowFirstPass',default="off")
    
    #selectProject =  commonForms.giveSelectionWithState(session,request,'selectProject','string',
    #                               tableTmpName='sel_projects',requires=db.project_data.name.requires,
    #                              default='', stripLabel=True)
    
    
    db.sample_data.first_pass.readable=False
    showAll = False
    if session.showAllColumns != "on":
        db.project_data.id.readable=False
        for col in hideColumns:
            db.sample_data[col].readable = False
            
   
   
    
    pids = [id.id for id in db((db.analyst_data.user_id  == auth.user) & (db.sample_data.analyst_id == db.analyst_data.id)).select(db.sample_data.id)]
    if auth.user == None: pids = [] 
    pquery = (db.project_data.id == db.sample_data.project_id )
    query= pquery & (db.sample_data.id.belongs(pids) )
    #import pdb; pdb.set_trace()
    #if isAdmin(db, auth):
        #query=db.sample_data
   
    if session.showAllPatients == "on" and isAdmin(db, auth):query= pquery &(db.sample_data.id >0) 
    
    if session.showOnlyWithPaths == "on":
        query = query & (db.sample_data.path_server != "")
    
    if session.doNotShowFirstPass == "on":
        query = query & ((db.sample_data.first_pass == None  ) | (db.sample_data.first_pass == False  )) 
    
    maxtextlength = 30

    deletable = False
    editable = False
    #if isAdmin(db, auth) and isSuperAdmin(db, auth): 
    #    deletable = True
    #    editable = True
         
    
    sample_create = SQLFORM.grid(query, 
                                deletable =deletable,
                                editable = editable,
                                maxtextlength=maxtextlength,
                                paginate=1000000000000,
                                search_widget=None,
                                create=False,
                                overflowauto="",
                                sortable=False
                                #links = [lambda row: 'eblebl']# INPUT('First pass',_type="checkbox", id ="first_pass_" )],
                                )
    
    if len(sample_create) > 1 and len(sample_create[1])>0 and len(sample_create[1][0]) > 0 and sample_create[1][0][0] != "No records found":
        #import pdb; pdb.set_trace()
        sample_create[1][0][0].attributes.update(_id = "patient_form")
    
    #import pdb; pdb.set_trace()
    #import pdb;pdb.set_trace();
    samples = [s for s in db(query).select(db.sample_data.ALL)]
    updateUrl =  URL(r=request , c='sampleManager',f='saveFirstPass' )
    
    view = False
    
    
    def __getModal(sample_name, results):
        #params = {'_href':"#myModal",'_class':"btn", '_data-toggle':"modal",  '_data-id':str(sample_id)}
        #launch_modal= A("add/edit",**params)
        res = DIV()
        for r in results: 
            if (r.sample_name == sample_name):
               res = res + DIV(str(r.chr) + ":"+ str(r.start_pos) + "_" + str(r.ref) + ">"+str(r.alt) + "("+str(r.gene_name) + ")")
         
                
        return (res)
    
    
    import os;
    cnvSamples = [x[0:-13] for x in os.listdir(rpkmDir)]
    snpSamples = [x[0:-4] for x in os.listdir(snpDir)]
    cnvSnpSamples = [x[0:-15] for x in os.listdir(cnvCallsDir)]
    if len(request.args)>0 and request.args[0]=='view': view=True
    if len(samples) > 0 and not view:
        results = [r for r in db(db.result_variant_data.id > 0).select(db.result_variant_data.ALL)]
        
        if isLL(db, auth) or isLLXLS(db,auth):
            addColumnToSQLTABLE(sample_create, [A(str(s.bab_number) + "_ll.csv", _href=URL(r=request , c='sampleManager',f='getXls_ll' , vars=dict(sample_id=s.id))) if (s.xls31 != None and s.xls31 != "NA" and s.xls31 !="") else "" for s in samples], "ll_xls")
            addColumnToSQLTABLE(sample_create, [A(str(s.bab_number) + "_filtered_reannotated.csv", _href=URL(r=request , c='sampleManager',f='getXls_ll_v2' , vars=dict(sample_id=s.id))) if (s.xls31 != None and s.xls31 != "NA" and s.xls31 !="") else "" for s in samples], "ll_xls_v2")
            
        addColumnToSQLTABLE(sample_create,[  DIV(  A(("AOH/CNV(exome)" if (s.bab_number in cnvSamples) else "AOH(exome)"), 
                                                   _href=URL(r=request , c='sampleManager',f='getAOH_CNV' , 
                                                             vars=dict(sample_id=s.id, 
                                                             type=("aoh_cnv" if (s.bab_number in cnvSamples) else "aoh")))) 
                                                                if (s.raw_snp != None and s.raw_snp!= "NA" and s.raw_snp!="") else "", 
                                                 " , " if (s.bab_number in cnvSamples) else "",
                                            (A("CNV calls(exome)", _href=URL(r=request , c='sampleManager',f='getCNV' , vars=dict(sample_id=s.id))) if (s.bab_number in cnvSamples)  else ""),
                                                 " , " if (s.bab_number in snpSamples) else "",
                                            (A("Bi-allele(cSNP)", _href=URL(r=request , c='sampleManager',f='getAOH_snp' , vars=dict(sample_id=s.id))) if (s.bab_number in snpSamples)  else ""),
                                                      " , " if (s.bab_number in snpSamples) else "",                                            
                                            (A("LogRatio(cSNP)", _href=URL(r=request , c='sampleManager',f='getCNV_snp' , vars=dict(sample_id=s.id))) if (s.bab_number in snpSamples)  else ""),
                                                      " , " if (s.bab_number in cnvSnpSamples) else "",                                            
                                            (A("CNV calls(cSNP)", _href=URL(r=request , c='sampleManager',f='getCNV_calls_snp' , vars=dict(sample_id=s.id))) if (s.bab_number in cnvSnpSamples)  else ""),
                                            
                                            )
                                            #A("CNV calls", _href=URL(r=request , c='sampleManager',f='getCNV' , vars=dict(sample_id=s.id))) if (s.bab_number in cnvSamples)  else "")                                         
                                            for s in samples],"AOH/CNV")
        
        addColumnToSQLTABLE(sample_create,[ INPUT(_type='checkbox', _name =  'first_pass_sid_' + str(s.id) ,  _value = s.first_pass , value = s.first_pass,
            _onchange= "  firstPassAjax('"+updateUrl+"',"+  str(s.id)+"," + "'first_pass_sid_"+str(s.id)+"');"  ) for s in samples],"First pass finished")
        
        addColumnToSQLTABLE(sample_create,[__getModal(s.bab_number, results) for s in samples],"Results")
        

        
        
        
    option_header= DIV(  TABLE(TR(TD("Show only samples with available data: "),TD(showOnlyWithPaths )),
                      TR( TD("Show other users' samples: "),TD(showAllPatients )),
                                    TR(TD("Show all columns: "),TD(showAllColumnsCheckbox )),
                                    TR(TD("Hide samples for which the first pass has been done: "),TD(doNotShowFirstPass )),
                                        TR(TD("Analyst assignment: "),TD(analyst_assignment ))
                                        ),
                  )
    if not isAdmin(db,auth):
        option_header = DIV(TABLE(TR(TD("Show only samples with available data: "),TD(showOnlyWithPaths )), 
                         TR(TD("Show all columns: "),TD(showAllColumnsCheckbox )),
                         TR(TD("Hide samples for which the first pass has been done: "),TD(doNotShowFirstPass )) ))

    params2 = {'_type':"button", '_class':"close", '_data-dismiss':"modal"}
    modal_window = DIV( DIV( BUTTON("x", **params2), _class="modal-header"),
                   DIV( TABLE(TR(TD("Reported variants"),TD (DIV(_class="variant_list",_id="variant_list"))), 
                       TR(TD("Add new"),TD(DIV(LOAD('sampleManager', 'report_variant.load',ajax=True, ajax_trap=True))))), 
                             _class="modal-body"),
                   DIV ("",_class="modal-footer") ,_id="myModal", _class="modal hide fade",_width='80%',_left='10%', _height='90%')

    

    return dict(option_header=option_header, 
                sample_create=sample_create,
                #modal_window=modal_window
               )
    
    
@auth.requires_login()
@auth.requires_membership('mendel')
def report_variant():
    #sample_id = request.vars['sample_id']
    #db.result_variant_data.sample_data_id.writable=False
    form = SQLFORM(db.result_variant_data, formstyle='bootstrap')
    #import pdb;pdb.set_trace();
    if form.process().accepted:
        session.flash = 'form accepted'
        redirect(URL('report_variant', vars={'success':'ok'}))
    elif form.errors:
        response.flash = 'form has errors'
        #redirect(URL('report_variant', vars={'success':'false'}))
    else:
        pass
    return dict(form=DIV( form))


def __results_added():
    import pdb; pdb.set_trace()
    session.flash = 'form accepted'
    redirect(URL('index'))
    return

@auth.requires_login()
@auth.requires_membership('mendel')
def get_variant_list():
    sample_id = request.vars['sample_id']
    #variant_list=DIV("AAAAAAAAAAAAAAA" + str(sample_id))
    #rows = db(db.result_variant_data.id>0).select(db.result_variant_data.ALL)
    #table = SQLTABLE(rows)
    query = db.result_variant_data.sample_data_id == sample_id
    rows= db(query).select(db.result_variant_data.ALL)
    select = SQLTABLE(rows)
    #db.result_variant_data.variant.represent = lambda k: TEXTAREA(value=k, _rows=2)
    #db.result_variant_data.molecular_diagnosis.represent = lambda k: TEXTAREA(value=k, _rows=2)
    #db.result_variant_data.notes.represent = lambda k: TEXTAREA(value=k, _rows=2)
    #db.result_variant_data.sample_data_id.default= sample_id
    #db.result_variant_data.sample_data_id.writable=False
    #create =crud.create(db.result_variant_data, onaccept = __results_added)
    #create = SQLFORM(db.result_variant_data, formstyle='bootstrap')
    
    if len(rows) > 0: 
        addColumnToSQLTABLE_old(select,["DEL_" + str(r.id) for r in rows],"Delete")
    
    
    return select
@auth.requires_login()
@auth.requires_membership('mendel')
def error():
    return dict()
    
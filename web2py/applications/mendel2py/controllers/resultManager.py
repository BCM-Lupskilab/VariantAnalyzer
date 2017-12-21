'''
Created on May 1, 2013

@author: tgambin
'''

exec("from applications.%s.modules.utils import *" % request.application)
import applications.mendel2py.modules.commonForms as commonForms
from applications.mendel2py.modules.utils import *

appDir = request.folder
rDir =    "/home/va/workspace/variant_analyzer/r_scripts/"
rpkmDir = "/home/va/data/RPKM/"
aohPlotsDir = "/home/va/data/aoh_cnv_plots/"
cnvPlotsDir = "/home/va/data/conifer_output/call_images/"

raw_data = "/home/va/data/raw_data/"
uploadDir = appDir + "uploads/"
outputDir = appDir + "output/"
r = robjects.r
r.source(rDir + "all_utils.R")
r.source(rDir + "getVariantsFromGene.R")


import csv
import rpy2.robjects as robjects
import os

@auth.requires_login()
@auth.requires_membership('mendel')
@auth.requires_membership('lupskilab')
def onCreateRes(form):
    #form.vars.sample_data_id = session.select_sample
    import pdb;pdb.set_trace(); 
    pass

@auth.requires_login()
@auth.requires_membership('mendel')
@auth.requires_membership('lupskilab')
def my_ondelete_function(table, record_id):                             
    print "Deleting %s from %s" % (record_id, table)                            
    db(table[table._id.name]==record_id).delete()                               
    db.commit()

def _myOnUpdate(form):
    print request.vars; 
    
    
#def updateNames():
#    for rec in db(db.result_variant_data.id>0).select(db.result_variant_data.ALL):
#        sample_name = (db(db.sample_data.id == rec.sample_data_id).select(db.sample_data.bab_number)[0]).bab_number
#        db(db.result_variant_data.id == rec.id).update(sample_name = sample_name)
#        db.commit()

def _getMutType(x):
    dd = {"frameshift_deletion":"frameshift_deletion",
         "frameshift_deletion/exonic_splicing":"frameshift_deletion",
         "frameshift_insertion":"frameshift_insertion",
         "frameshift_insertion/exonic_splicing":"frameshift_insertion",
         "nonframeshift_deletion":"nonframeshift_deletion",
         "nonframeshift_deletion/exonic_splicing":"nonframeshift_deletion",
         "nonframeshift_insertion":"nonframeshift_insertion",
         "nonframeshift_insertion/exonic_splicing":"nonframeshift_insertion",
         "nonsynonymous_snv":"missense",
         "nonsynonymous_snv/exonic_splicing":"missense",
         "splicing":"splicing",
         "stopgain_snv":"sptopgain",
         "stopgain_snv/exonic_splicing":"sptopgain",
         "stoploss_snv":"stoploss",
         "stoploss_snv/exonic_splicing":"stoploss",
         "missense":"missense",
         "deletion":"frameshift_deletion",
         "insertion":"frameshift_insertion",         
         "splicing_snv":"splicing",
         "substitution":"missense",
         "missense_snv":"missense",
          "missensesnv":"missense",
         }
    x = x.lower()
    if dd.has_key(x):return dd[x]
    return("other")         

def __matchMutType(x):
    return _getMutType(x.lower().replace(" ", "_"))
    

def __result_import(form):
     input_file = form.vars.input_file
     ff  =uploadDir + input_file
     analysts =dict()    
     
     csvReader = csv.reader(open(ff), delimiter=',')
     #import pdb; pdb.set_trace()
     cnt = 0 
     for line in csvReader:
         if (cnt !=0 ):
             #print str(line)
             dd = {}
             dd["sample_name"] = line[1]
             dd["gene_name"] = line[2]
             dd["gene_category"] = line[3].lower().replace(" ", "_")
             dd["status"] = line[5].lower()
             dd["phenodb_id"] = line[6]
             dd["chr"] = line[7]
             dd["start_pos"] = line[8]
             dd["ref"] = line[9]
             dd["alt"]=line[10]
             dd["zygosity"]=line[11].title()
             dd["mutation_type"]= __matchMutType(line[4])
             dd["nm_accession_id"] = line[12]
             dd["aminoacid_change"] = line[13]
             dd["cdna_change"] = line[14]
             dd["rsid"] = line[15]
             dd["inheritance_model"] = line[16].lower()
             dd["inheritance_mode"] = line[17].lower()
             dd["sanger_validation"] = line[18].lower()
             dd["additional_cases"] = line[20].lower()
             dd["ancestry"] = line[21]
             dd["omim"] = line[22]
             dd["heart_lung_or_blood_disorder"] = line[23].lower()
             dd["strategy"] = line[24].lower()
             dd["unsolved"] = line[25]
             dd["dbgap_cosent"] = line[26]#todos
             dd["publication_status"] = line[27].lower().replace(" ", "_")
             dd["publication_url"] = line[28]
             dd["evidence"] = line[29]
             dd["notes"] = line[30]
             print(dd)
             
             db.result_variant_data.insert(**dd)
             db.commit()
             
         cnt = cnt + 1
         
    
     db.commit()

@auth.requires_login()
@auth.requires_membership('mendel')
@auth.requires_membership('lupskilab')
def index():

    #showAll=commonForms.giveCheckboxWithState(session,request,'showAlls',default="off")
    #if (session.selectSample != ""):        session.showAlls = "off" 
    #if (session.showAlls == "on"): session.selectSample = ""
    #select_sample = None        
    #try:    select_sample = int(request.args[1])        
    #except: segmId = session.show_segmentation_id
    #import pdb;pdb.set_trace();s
    
    #sampleIds =[s.id for s in db(db.sample_data.id>0).select(db.sample_data.ALL)]
    #sampleBabs =[s.bab_number for s in db(db.sample_data.id>0).select(db.sample_data.ALL)]
    
    #req=IS_IN_SET([0] + sampleIds,["SELECT ALL"] + sampleBabs)
    #selectSample =  commonForms.giveSelectionWithState(session,request,'select_sample','integer',db,
    #                               tableTmpName='sel_samples',requires=req,
                                  # requires=db.result_variant_data.sample_data_id.requires,
                                  #default='',
    #                               stripLabel=True)
    
    #print(session.select_sample)
    analyst_id = None
    if auth.user:
        analyst_id = db(db.analyst_data.user_id == auth.user.id).select(db.analyst_data.id)[0].id
        
    #query =(db.result_variant_data.analyst_id == analyst_id)
    
    query =(db.result_variant_data.id>0)
    
    cdata = db(query).select(db.result_variant_data.ALL)
    cids = [d.id for d in cdata]
    
    
    
    print "****************"
    print (request.args)
    addResForm=None
    if request.vars.has_key("result_id") and int(request.vars.has_key("result_id")) > 0 :
        print("here")
        #import pdb; pdb.set_trace()
        #crud.settings.keepvalues = False
        crud.messages.submit_button = 'Update'
        crud.settings.update_next = URL(r=request, c="resultManager", f="index")
         
        addResForm=DIV(H3("Update variant"), crud.update(db.result_variant_data,int(request.vars["result_id"]), onupdate=_myOnUpdate, deletable=False, onaccept=auth.archive))
       #response.vars["result_id"] = 0
        #import pdb; pdb.set_trace();
        #request.vars.remove_key("result_id")
        #pass
    else:
        if request.vars.option_submit:
            sn = request.vars.sample_name
            gene = request.vars.gene_name
            db.result_variant_data.sample_name.default = sn       
            db.result_variant_data.gene_name.default = gene 
            bab = sn
            #db.result_variant_data.chr.default = request.vars.chrom
            #db.result_variant_data.start_pos.default = request.vars.
            data  = r.getVariantsFromGene(raw_data + bab + "/" + bab + "_v31.xls", gene)
            chroms = []
            pos = []
            keys=[]
            refs=[]
            alts=[]
            zygosity=[]
            mutType=[]
            cnt =0
            for colname in data.colnames:
                #if colname == "key": keys = [x for x in data[cnt]]
                if colname == "CHROM": chroms = [x for x in data[cnt]]
                if colname == "POS": pos = [x for x in data[cnt]]
                if colname == "REF": refs = [x for x in data[cnt]]
                if colname == "ALT": alts = [x for x in data[cnt]]
                if colname == "Zygosity": zygosity = [x for x in data[cnt]]
                if colname == "Zygosity": zygosity = [x for x in data[cnt]]
                if colname == "Mutation_type_.Refseq.": mutType = [_getMutType(x) for x in data[cnt]]
                cnt = cnt + 1 
                
            db.result_variant_data.chr.default = chroms[int(request.vars.options)]        
            db.result_variant_data.start_pos.default = pos[int(request.vars.options)]        
            db.result_variant_data.ref.default = refs[int(request.vars.options)]        
            db.result_variant_data.alt.default = alts[int(request.vars.options)]        
            db.result_variant_data.zygosity.default = zygosity[int(request.vars.options)]
            db.result_variant_data.mutation_type.default = mutType[int(request.vars.options)]
            
        
        crud.messages.submit_button = 'Submit'
        ff = SQLFORM(db.result_variant_data)
        ff.insert(0,INPUT(_type='submit', _value="Search for variants", _name='lucky'))
        addResForm=DIV(H3("Submit new variant"), ff)
        #if request.vars.keywords:
            
        if request.vars.lucky:
            sn = request.vars.sample_name
            gene= request.vars.gene_name
            bab = sn
        
            import os;
            
            if (os.path.exists(raw_data + "/" + bab + "/" + bab + "_v31.xls")):
                print "here"
                data  = r.getVariantsFromGene(raw_data + "/" + bab + "/" + bab + "_v31.xls", gene)
                chroms = []
                pos = []
                keys=[]
                cnt =0
                for colname in data.colnames:
                    if colname == "key": keys = [x for x in data[cnt]]
                    #if colname == "CHROM": chroms = [x for x in data[cnt]]
                    #if colname == "POS": pos = [x for x in data[cnt]]
                    cnt = cnt + 1 
                    

                addResForm = DIV(FORM( DIV("Select variant you want to submit [sample=" + bab +" gene="+ gene+"]"),
                                      SELECT(_name="options",*[OPTION(keys[k], _value=k) for k in range(0,len(keys))]),
                                      INPUT(_type="hidden", _name="gene_name", _value=gene),
                                      INPUT(_type="hidden", _name="sample_name", _value=sn),
                                      
                                       INPUT(_type='submit', _name='option_submit')), addResForm )
            else:
                addResForm = DIV(DIV("There is no data for this sample name: '" + bab + "'"), addResForm)
                #[code to return "I'm feeling lucky" results]
        else:
            if ff.accepts(request.vars, session):
                response.flash = 'record submitted'
            elif ff.errors:
                response.flash = 'form has errors'
        #import pdb; pdb.set_trace()  
        
    # addResForm=crud.create(db.result_variant_data)

    #addResForm=crud.update(db.result_variant_data, 5)
    
    #if addResForm.accepts(request.vars, formname="addResForm"):
    #    response.flash = T('Submitted')
    #else:
    #    response.flash = T('Not Submitted')
        
    #if (session.select_sample != None and int(session.select_sample) >0):
    #    query = (db.result_variant_data.sample_data_id == session.select_sample)
    #query = db.result_variant_data
    #result_form = SQLFORM.grid(query, 
                               
                               #create=True,
     #                           deletable =True,
     #                           editable = True,
     #                           maxtextlength=30,
     #                           paginate=1000000000000,
     #                           search_widget=None,
     #                           create=True,
     #                           oncreate=onCreateRes,
     #                           ondelete=my_ondelete_function,
                               
                                #overflowauto="",
                                #sortable=True
                                #links = [lambda row: 'eblebl']# INPUT('First pass',_type="checkbox", id ="first_pass_" )],
      #                          )
    
    #import pdb;pdb.set_trace();
    result_form=SQLFORM.grid( query,
                            
                               #_id="result_f",
                               create=False,
                                deletable =False,
                                editable = False,
        #                        maxtextlength=30,
                                paginate=1000000000000,
                                search_widget=None,
                                #create=False,
            #                    oncreate=onCreateRes,
                               ondelete=my_ondelete_function,
                               #viewable=False,
                               #   view=False,
                                overflowauto="",
                                sortable=False,
                                #links = [lambda row: 'eblebl']# INPUT('First pass',_type="checkbox", id ="first_pass_" )],
                                )
    #import  pdb; pdb.set_trace()
    addColumnToSQLTABLE(result_form, [ (A("Edit",_href=URL(r=request, c="resultManager", f="index",vars=dict(result_id=c.id)))) for c in cdata], "Edit")
     
     
    if len(result_form) > 1 and len(result_form[1])>0 and len(result_form[1][0]) > 0 and result_form[1][0][0] != "No records found":
        #import pdb; pdb.set_trace()
           result_form[1][0][0].attributes.update(_id = "result_f")
           
    result_import = crud.create(db.result_import, onaccept = __result_import)
    
    return dict(result_form=result_form,addResForm=addResForm, result_import=result_import)
    
from gluon.tools import redirect
from gluon.html import URL
from gluon.sqlhtml import *
from gluon.sql import *
from gluon.validators import *

from applications.mendel2py.modules.utils import getFormRow,getFormSubmitButtonTD



#Returns checkbox which state is remembered in session and updated on change (by reload!)
def giveCheckboxWithState(session,request,variableName,default="off"):
    if not request.vars.has_key(variableName):
        if session.has_key(variableName): request.vars[variableName]=session[variableName]
        else: request.vars[variableName]=default
    session[variableName]=request.vars[variableName]

    checkBoxUrl=URL(r=request,args=request.args,vars={variableName:"off" if request.vars[variableName]=="on" else "on"})
    checkbox=FORM(INPUT(_type='checkbox',_name=variableName,_value="on",
                                 _onchange="window.location = '%s';"%checkBoxUrl))
    #At this point FORM will setup the request.vars[variableName] appropriately and we can use it
    if request.vars[variableName]=="on": checkbox[0].attributes['_checked']=''
    checkbox.isSet = lambda: session[variableName] == "on"
    return checkbox



#Returns selection field which state is remembered in session and updated on submit
#As requires a validator like IS_IN_DB shall be used
def giveSelectionWithState(session,request,variableName,varType,tableTmpName='fakeTmp1',
                           default=None,requires=None,onaccept=lambda form:None,
                           submitOnChange=True,stripLabel=False):

    if not session.has_key(variableName): session[variableName]=default

    selform= SQLFORM(SQLDB(None).define_table(tableTmpName,
              Field(variableName,varType,requires=requires,
                    default=session[variableName])
            ))
    selectTag=getFormRow(selform,variableName,type(INPUT()))[0][0]
    if submitOnChange: #Hide submit and submit on change
        selectTag['_onchange']="this.form.submit();"
        selform[0][1][1][0]['_type']="hidden"
        #selform[0][1]=DIV(selform[0][1],_class="hidden")
    #import pdb;pdb.set_trace()
    if stripLabel:
        getFormRow(selform,variableName,type(LABEL()))[0].components=[]

    if selform.accepts(request.vars,session):
        session[variableName]= selform.vars[variableName]
        onaccept(selform)

    #Select actual correct option
    if isinstance(selectTag,type(SELECT())):
        for opt in selectTag:
            opt['_selected']="selected" if opt['_value']==str(session[variableName]) else None
    else: #input field
        selectTag['_value']=str(session[variableName])



    return selform


#Returns an update element for a given table,field and record
#submitted on change
def oneFieldCrudUpdate(crud,table,field,recordId,**crudParams):
    for fld in table.fields: table[fld].writable=table[fld].readable=False
    table[field].writable=table[field].readable=True
    crd = crud.update(table,recordId,deletable=False,**crudParams)
    getFormRow(crd,field,type(LABEL()))[0].components=[] #Strip label
    getFormSubmitButtonTD(crd).components=[]  #Remove submit button
    getFormRow(crd,field,type(SELECT()))[0][0]['_onchange']="this.form.submit();" #Submit on change
    return crd



def experimentUpdateForms(db,session,request,response,crud,expId):

    db.acgh_experiment.file_id.readable=True
    db.acgh_experiment.file_id.writable=True #It's turned off later below - otherwise problems with web2py
    db.acgh_experiment.file_id.requires=[]
    db.acgh_experiment.patient_id.writable=True
    db.acgh_experiment.chip_version_id.readable=True
    db.acgh_experiment.chip_version_id.writable=True #It's turned off later below - otherwise problems with web2py
    db.acgh_experiment.chip_version_id.requires=[]
    db.acgh_experiment.date.writable=False
    db.acgh_experiment.acgh_rdata_id.writable=db.acgh_experiment.acgh_rdata_id.readable=False
    db.acgh_experiment.main_segm_id.writable=True
    db.acgh_experiment.main_segm_id.readable=True
    db.acgh_experiment.main_segm_id.requires=IS_NULL_OR(IS_IN_DB(db(db.acgh_segmentation.acgh_exp_id==expId),
                                                         db.acgh_segmentation.id,orderby='~id'))
    db.acgh_experiment.probe_count.writable=False
    db.acgh_experiment.dlrsd.writable=False

    db.acgh_experiment.reverse_dyeing.writable=False

    crud.messages.submit_button= 'Update experiment'
    expInfo=crud.update(db.acgh_experiment,expId, message="Experiment updated!",
                        deletable=False,next=URL(r=request,args=request.args))
    #Changing ids to names - it doesn't work automatically when readonly field
    trs=getFormRow(expInfo,"file_id",object)
    trs[0][0][0] = 'File name:'
    trs[1][0].attributes['_type']="hidden"
    fqry=db((db.acgh_experiment.id==expId)&(db.file.id==db.acgh_experiment.file_id)).select(db.file.id,db.file.filename)
    trs[1].append(A(fqry[0].filename,_href=URL(r=request,c='default',f='showfile',args=['file',fqry[0].id])))

    trs=getFormRow(expInfo,"chip_version_id",object)
    trs[0][0][0] = 'Chip version:'
    trs[1][0].attributes['_type']="hidden"
    cqry=db((db.acgh_experiment.id==expId)&(db.chip_version.id==db.acgh_experiment.chip_version_id)
            ).select(db.chip_version.version,db.chip_version.id,db.chip_version.probe_count)
    trs[1].append(A(cqry[0].version,_href=URL(r=request,c='addChipVersion',f='update_chip',args=cqry[0].id)))

    trs=getFormRow(expInfo,"probe_count",object)
    trs[1][0] = "%s (on chip: %s)"%(trs[1][0],cqry[0].probe_count)
    #import pdb;pdb.set_trace()

    sel=getFormRow(expInfo,"patient_id",type(SELECT()))[0]
    patientId=int([opt.attributes['_value'] for opt in sel[0] if opt.attributes['_selected']!=None][0])

    crud.messages.submit_button= 'Update patient'
    db.patient.patient_identifier.writable=False
    updatePatient=crud.update(db.patient,patientId,next=URL(r=request,args=request.args),deletable=False,
                              message="Patient data updated!")
    trs=getFormRow(updatePatient,"category_id",object)
    trs[0][0][0] = 'Group:'


    crud.messages.submit_button= 'Add new patient'
    db.patient.patient_identifier.writable=True
    addPatient=crud.create(db.patient,next=URL(r=request,args=request.args),message="Patient created!")

    trs=getFormRow(addPatient,"category_id",object)
    trs[0][0][0] = 'Group:'


    #Add borders
    expInfo[0]['_class']="thin"
    updatePatient[0]['_class']="thin"
    addPatient[0]['_class']="thin"
    return {'Experiment details':expInfo,"Update patient": updatePatient,"Add new patient": addPatient}


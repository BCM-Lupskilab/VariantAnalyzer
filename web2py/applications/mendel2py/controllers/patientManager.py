'''
Created on May 1, 2013

@author: tgambin
'''

import applications.mendel2py.modules.commonForms as commonForms

def isAdmin():
    res = db((db.auth_membership.user_id == auth.user)&
       (db.auth_group.id  == db.auth_membership.group_id)&
       (db.auth_group.role == "admin" )).select(db.auth_group.ALL)
    print (res)
    return (len(res )> 0)

def index():
    
    hideColumns = ['id', 'user_id', 'dob','doa', 'dos', 'dop', 'decision', 'referral_physician', 'patient_name']
    showAllColumnsCheckbox=commonForms.giveCheckboxWithState(session,request,'showAllColumns',default="off")
    showAllPatients=commonForms.giveCheckboxWithState(session,request,'showAllPatients',default="off")
    showAll = False
    if session.showAllColumns != "on":
        for col in hideColumns:
            db.patient_data[col].readable = False
        
        
    if session.showAllPatients == "on" and isAdmin(db, auth.user):query=db.patient_data
    
    else:   query=(db.patient_data.user_id == auth.user)
    
    
    #left =(db.patient_relation.on(db.patient_relation.patient_1 == db.patient_data.id))
    sample_create = SQLFORM.grid(query, deletable = False)#, left=left)
    if 
    #if len(sample_create) > 1 and len(sample_create[1])>0 and len(sample_create[1][0]) > 0 and sample_create[1][0][0] != "No records found":
        #import pdb; pdb.set_trace()
        #sample_create[1][0][0].attributes.update(_id = "patient_form")

    #import pdb;pdb.set_trace();
    return dict(sample_create=DIV(TABLE(TR(TD("Show other users' patients: "),TD(showAllPatients )),
                                        TR(TD("Show all columns: "),TD(showAllColumnsCheckbox ))),
                sample_create))
    
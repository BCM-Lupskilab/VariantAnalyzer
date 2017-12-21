'''
Created on May 1, 2013

@author: tgambin
'''

def index():
  
    def onAccept(form):
        if (form.vars.relation_type == 'sibling of'): 
            db.patient_relation.insert(patient_1 = form.vars.patient_2, relation_type = 'sibling of' , patient_2 = form.vars.patient_1)
        pass

    def onValidation(form):
        if len(db((db.patient_relation.patient_1 == form.vars.patient_1) & (db.patient_relation.relation_type== form.vars.relation_type)&(db.patient_relation.patient_2 == form.vars.patient_2)).select(db.patient_relation.ALL)) > 0:
            error = SPAN(T('This relation already exists in DB'),_style='color:red')
            #form.errors.sapmple_1 = error
            form.errors = error
            response.flash = error
        if form.vars.patient_1 == form.vars.patient_2: 
            error = SPAN(T('Cannot define relation between single patient'),_style='color:red')
            form.errors = error
            session.flash = error
        pass
    
    ids  = [id.id for id in (db(db.patient_data.user_id == auth.user).select(db.patient_data.id))]
    query=( db.patient_relation.patient_1.belongs  (ids) )
    #query = db.patient_relation
    relation_create = SQLFORM.grid(query,oncreate=onAccept, onvalidation =  onValidation)
    if relation_create.create_form and relation_create.create_form.errors:
        response.flash = relation_create.create_form.errors
    
    return dict( relation_create = relation_create)
    
# -*- coding: utf-8 -*-
'''
Created on May 1, 2013

@author: tgambin
'''

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1)
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.# Analysis timestamps
 # - sample ID
 # - date
 # - status

# Samples
 #- BAB number
 # - last status
 # - project ID
 # - server path
 # - backup path
 # - local VCF path

# Projects
 # - name 
 # - analyst ID

# Analysts
 # - name
 # - emailmemcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

#mail.settings.server = settings.email_server
#mail.settings.sender = settings.email_sender
#mail.settings.login = settings.email_login

## for scheduler



######### GENES #
from applications.mendel2py.modules.utils import g_interval_data_types
from applications.mendel2py.modules.utils import g_default_threshold
#g_interval_data_types = {'int_refseq_gene':0 , 'int_refseq_exon':1,
#                       'int_toronto_cnv':2, 'probe':3 , 'acgh_segment':4}

db.define_table('interval_data',
                Field('chr' , 'integer' , requires=IS_NOT_EMPTY()  ),
                Field('startPos' , 'integer', requires=IS_NOT_EMPTY()  ),
                Field('stopPos' , 'integer', requires=IS_NOT_EMPTY()  ),
                Field('int_type'  ,'integer', requires=IS_NULL_OR(IS_IN_SET(g_interval_data_types.values())),default = None ),
                )

db.define_table('int_refseq_gene',
                Field('interval_id',db.interval_data,ondelete='CASCADE'),
                Field('name',requires=IS_NOT_EMPTY()),
                Field('http_link'),
                )
#db.int_refseq_gene.interval_id.requires=IS_IN_DB(db, 'interval')



db.define_table('int_refseq_exon',
                Field('interval_id',db.interval_data,ondelete='CASCADE'),
                Field('int_refseq_gene_id',db.int_refseq_gene),
                )



db.define_table('gene_list',
                Field('input_file','upload',required=True,requires=IS_NOT_EMPTY(), label = "gene list file"),
               Field('gene_list_name','string',unique = True, required=True, label = "group name"),
                Field('owner_id',db.auth_user, default = auth.user.id if auth.user else 0),
                )

db.define_table('gene_group',
                Field('gene_list_id',db.gene_list,required=True,requires=IS_IN_DB(db(db.gene_list.owner_id == auth.user), db.gene_list.id,'%(gene_list_name)s')),
                Field('int_refseq_gene_id',db.int_refseq_gene,required=True),
                )

db.gene_group.gene_list_id.represent = lambda id, var: db.gene_list(id).gene_list_name
db.gene_group.int_refseq_gene_id.represent = lambda id, var: db.int_refseq_gene(id).name


#############


db.define_table('analyst_data',
                Field('name','string', required=True, unique=True, label="Analyst name"),
                Field('email','string', required=True, unique=True, label="e-mail"),
                Field('user_id',db.auth_user, unique=True, label="user_id", 
                      requires=IS_NULL_OR(IS_IN_DB(db,db.auth_user, '%(email)s'))),
                )



db.define_table('project_data',
                Field('name','string', required=True, unique=True, label="Project name"),
                Field('pi','string', label="PI"),
                #Field("analyst_id", db.analyst_data,required=True,requires=IS_IN_DB(db, db.analyst_data.id,'%(email)s')),
                #fake_migrate=True,
                )


db.define_table('sample_data',
                Field('bab_number','string', required=True, unique=True, label="BAB number"),
                Field('path_server','string', label="Path - server"),
                Field('path_backup','string',  label="Path - backup"),
                Field('raw_snp','string',   label="raw SNP"),
                Field('raw_indels','string',   label="raw INDELs"),
                Field('xls','string',   label="filtered XLS"),
                 Field('xls31','string',   label="[new] filtered XLS V3.1", readable=True),
                Field("project_id", db.project_data,required=True,requires=IS_IN_DB( db, db.project_data.id,'%(name)s')),
                #Field('user_id',db.auth_user, default = auth.user.id if auth.user else 0),
                Field('creation_time','datetime',required=True,default=request.now,requires=IS_NOT_EMPTY()),
                Field("analyst_id", db.analyst_data,required=True,requires=IS_IN_DB(db, db.analyst_data.id,'%(email)s')),
                #fake_migrate=True
                Field("alive", 'string', label = "Is file alive on server"),
                Field('first_pass', 'boolean', default=False, label="First pass finished")
                )

db.sample_data.project_id.represent = lambda id, var: db.project_data(id).name
db.sample_data.analyst_id.represent = lambda id, var:  db.analyst_data(id).email if (db.analyst_data(id) != None) else None
db.sample_data.raw_snp.represent = lambda id, var:  A(id.split("/")[-1], _href=URL(f='download',vars={"path":id} )) if id != "NA" else None
db.sample_data.raw_indels.represent = lambda id, var:  A(id.split("/")[-1], _href=URL(f='download',vars={"path":id} )) if id != "NA" else None
db.sample_data.xls.represent = lambda id, var:  A(id.split("/")[-1], _href=URL(f='download',vars={"path":id} )) if id != "NA" else None 
db.sample_data.xls31.represent = lambda id, var:  A(id.split("/")[-1], _href=URL(f='download',vars={"path":id} )) if ((id != None) and (id != "NA")) else None 


db.define_table('event_data',
                 Field('event_type', 'string', requires=IS_IN_SET(['data_released', 'data_downloaded_by_analyst' , 'first_pass_finished' ,])),
                 Field('sample_data_id', db.sample_data,required=True,requires=IS_IN_DB( db, db.sample_data.id,'%(bab_number)s')),
                 Field('creation_time','datetime',required=True,default=request.now,requires=IS_NOT_EMPTY()),
                 Field('user_id',db.auth_user, default = auth.user.id if auth.user else 0),
                 )
db.define_table('analyst_assignment',
                Field('input_file', 'upload', required=True, requires=IS_NOT_EMPTY()))

db.define_table('result_import',
                Field('input_file', 'upload', required=True, requires=IS_NOT_EMPTY()))

#db.sample_data.patient_data_id.represent = lambda id, var: db.patient_data(id).bab_number
#db.sample_data.id.represent = lambda id, var: db.patient_data(db.sample_data(id).patient_data_id).bab_number

import re;
db.define_table('result_variant_data',
                Field('sample_name', 'string', label="Sample Name *"),
                Field('gene_name', 'string', label="Gene Symbol *"),                                  
                Field('gene_category', 'string', label="Gene Category *", requires=IS_NULL_OR(IS_IN_SET(["novel", "phenotypic_expansion","known"]))),                                                
                Field('status', 'string', label="Variant Status *", requires=IS_NULL_OR(IS_IN_SET(["candidate", "causal"]))),                                
                Field('phenodb_id', 'string', label="PhenonDB Id *"),
                
                Field('chr', 'string', label="CHROM *",requires=IS_IN_SET([str( s) for s in range(1,23)] + ["X", "Y"])),
                Field('start_pos', 'integer', label="POS *"),
                #Field('stop_pos', 'integer', label="stop"),
                Field('ref', 'string', label="REF *"),
                Field('alt', 'string', label="ALT *"),
                Field('zygosity', 'string', label="Zygosity", requires = IS_NULL_OR(IS_IN_SET(["Hom","Het"]))),
                Field('mutation_type', 'string', label="Mutation Type *", requires=IS_NULL_OR(IS_IN_SET(["missense",
                                                                                            "splicing",
                                                                                            "stopgain",
                                                                                            "stoploss",
                                                                                            "frameshift_deletion",
                                                                                            "frameshift_insertion",
                                                                                            "nonframeshift_deletion",
                                                                                            "nonframeshift_insertion",
                                                                                            "other" ]))),
                
                Field('nm_accession_id', 'string', label="NM Accession Id"),
                Field('exon_location', 'integer', label="exon number"),
                Field('aminoacid_change', 'string', label="Amino Acid Change"),
                Field('cdna_change', 'string', label="cDNA Change"),
                Field('rsid', 'string', label="Reference SNP ID"),
                Field('inheritance_model', 'string', label="Inheritance Model",requires=IS_NULL_OR(IS_IN_SET(["recessive", "dominant", "x-linked" ,"unknown"]))),
                Field('inheritance_mode', 'string', label="Mode of Inheritance",requires=IS_NULL_OR(IS_IN_SET(["maternal", "paternal", "de-novo" ,"unknown"]))),
                Field('sanger_validation', 'string', label="Variant Validation *",requires=IS_NULL_OR(IS_IN_SET(["yes", "no"]))),
                Field('total_for_validation', 'integer', label="Total # of samp. for val. *"),
                Field('additional_cases', 'string', label="Additional Cases Needed *",requires=IS_NULL_OR(IS_IN_SET(["yes", "no"]))),
                Field('ancestry', 'string', label="Ancestry",requires=IS_NULL_OR(IS_IN_SET(["African", "European", "Asian" ,"African-American", "Hispanic"]))),
                Field('omim', 'string', label="OMIM # *"),
                Field('heart_lung_or_blood_disorder', 'string',label ="Heart Lung or Blood Disorder *", requires=IS_NULL_OR(IS_IN_SET(["yes", "no"]))),
                Field('strategy', 'string', label="Strategy *",requires=IS_NULL_OR(IS_IN_SET(["trio/denovo", "familial/inherited", "cohort/unrelateds","mixed", "other"]))),
                Field('unsolved', 'integer', label="# of Unsolved Families with this Phenotype *",),
                Field('dbgap_cosent', 'string', label="dbGaP consent *", requires=IS_NULL_OR(IS_IN_SET(["yes-GRU", "yes-DUL" ,"no","yes"]))),
                Field('publication_status', 'string', label="Publication Status *", requires=IS_NULL_OR(IS_IN_SET(["in_progress", "submitted" ,"in-press", "published"]))),
                Field('publication_url', 'string', label="Publication URL", requires=IS_EMPTY_OR(IS_URL())),
                Field('evidence', 'string', label="Evidence *"),                
                Field('notes', 'string', label ="Notes"),
                
                 
                 Field('creation_time','datetime',required=True,default=request.now,requires=IS_NOT_EMPTY(),  writable=False),
                 Field("analyst_id", db.analyst_data,required=True,requires=IS_IN_DB(db, db.analyst_data.id,'%(email)s'), default =  db(db.analyst_data.user_id == auth.user.id).select(db.analyst_data.id)[0].id if auth.user else 0 ,  writable=False),
                 Field('last_update','datetime',required=True,default=request.now, update=request.now,writable=False),
                 Field("last_user", db.analyst_data,required=True,requires=IS_IN_DB(db, db.analyst_data.id,'%(email)s'),update= db(db.analyst_data.user_id == auth.user.id).select(db.analyst_data.id)[0].id if auth.user else 0 , default =  db(db.analyst_data.user_id == auth.user.id).select(db.analyst_data.id)[0].id if auth.user else 0 , writable=False),
                 )

#db.result_variant_data.sample_data_id.represent = lambda id,var: db.sample_data(id).bab_number
db.result_variant_data.analyst_id.represent = lambda id,var: db.analyst_data(id).email if (id!= None) else None
db.result_variant_data.last_user.represent = lambda id,var: db.analyst_data(id).email if (id!= None) else None

#db.define_table('input_form',
#                #Field('sample_id',db.sample_data,required=True,requires=IS_IN_DB(db(db.sample_data.user_id == auth.user), db.sample_data.id)),
#                Field('input_file','upload',required=True,requires=IS_NOT_EMPTY(), label = "variants file (VARFILE or MERCURY xls)"),
#                #Field('mother','upload', label = "mother"),
#                #Field('father','upload',label = "father"),
#                #Field('relative1','upload',label = "relative1"),
#                #Field('relative2','upload',label = "relative2"),
#                #Field('relative3','upload',label = "relative3"),
#                Field('min_vR','integer', default = 5, label = "Min. number of variant reads (min_vR)"),
#                Field('min_tR','integer', default = 10, label = "Min. number of total reads (min_tR)"),
#                
#                Field('PhS', 'integer',  label='min. Phred score'),
#                Field('TGP_freq' , 'double',default = 0.01, label = "max. frequency in TGP"),
#                Field('esp5400_freq', 'double', default = 0.01, label='max. frequency in esp'),
#                Field('maxMendMutHom', 'integer', default = 5, label='max. MendelianMutationDB homozygous'),
#                Field('maxMendMutHet', 'integer', default = 40, label='max. MendelianMutationDB heterozygous'),
#                
#                Field('only_OMIM_disease', 'boolean', default= False),                
#                Field('Phylop_pred', 'string',requires=IS_NULL_OR(IS_IN_SET(['conserved'])), default= ''),
#                Field('LTR_pred', 'string',requires=IS_NULL_OR(IS_IN_SET(['deleterious'])), default= ''),
#                Field('Sift_pred', 'string',requires=IS_NULL_OR(IS_IN_SET(['damaging'])), default= ''),
#                Field('Mt_pred', 'string',requires=IS_NULL_OR(IS_IN_SET(['damaging'])), default= ''),
#                
#                 Field('gene_list',db.gene_list,requires=IS_NULL_OR(IS_IN_DB(db(db.gene_list.owner_id == auth.user), db.gene_list.id,'%(gene_list_name)s')), label="Annotate with my gene list"),
#                 Field('geneTerm', 'string', label='Get gene list from UCSC for the term'),
#                Field('filter_genes', 'boolean', default = False, label='Remove variants from other genes'),
#                )

db.define_table('input_form',
                Field('input_file','upload',required=True,requires=IS_NOT_EMPTY(), label = "variants file (_ll.csv)"),                
                 Field('gene_list',db.gene_list,requires=IS_NULL_OR(IS_IN_DB(db(db.gene_list.owner_id == auth.user), db.gene_list.id,'%(gene_list_name)s')), label="Annotate with my gene list"),
                 Field('geneTerm', 'string', label='Get gene list from UCSC for the term'),
                
                )


db.define_table('gene_analyzer_data',
                Field('gene_name', 'text'),
                 Field('user_id',db.auth_user, default = auth.user.id if auth.user else 0,  writable=False),                 
                 )




db.define_table('request_data',
                Field('requested_by', 'string' ,label="Requested by (email)",  requires=IS_EMAIL()),
                
                
                Field('project_name', 'string'),
                Field('description', 'text'),
                Field('list_of_genes', 'string', label="List of genes (comma separated)"),
                Field('attachment', 'upload', label="Attachment (gene list)"),
                Field('expected_inheritance_model', 'string',requires=IS_NULL_OR(IS_IN_SET(["recessive", "dominant", "x-linked" ,"unknown"]))),
                Field('expected_phenotype', 'string'),
                
                Field('destination', 'string',requires=IS_NULL_OR(IS_IN_SET(['CMG', "WGL", "MGL", "CMG/MGL/WGL", "CMG/MGL", "CMG/WGL", "MGL/WGL" ]))),
                Field('response', 'text'),
                Field('results', 'upload', label="Raw results"),
                
                Field('status','string',requires=IS_NULL_OR(IS_IN_SET(["waiting_for_initial_approval", "sent_to_WGL","ready_waiting_for_final_approval", "returned_to_colaborator"])), default= 'waiting_for_initial_approval' ),
                Field('analyst_assigned',db.auth_user, default = auth.user.id if auth.user else 0),
                Field('user_id',db.auth_user, default = auth.user.id if auth.user else 0,  writable=False),
                
                Field('creation_time','datetime',required=True,default=request.now,requires=IS_NOT_EMPTY(),  writable=False),
                Field('last_update','datetime',required=True,default=request.now, update=request.now,writable=False),
    
                )



##########


db.define_table('restore_request',
                #Field("bab_number","string"),
                Field('sample_data_id', db.sample_data,required=True,requires=IS_NULL_OR(IS_IN_DB( db, db.sample_data.id,'%(bab_number)s')), label="Select sample name"),
                Field('project_data_id', db.project_data,required=True,requires=IS_NULL_OR(IS_IN_DB( db, db.project_data.id,'%(name)s')), label="Or select all samples from the project"),
                 
                Field("bam","boolean"),
                Field("fastq","boolean"),
                Field("vcf","boolean"),
                
                Field('request_time','datetime',required=True,default=request.now,requires=IS_NOT_EMPTY(), writable=False),
                Field("analyst_id", db.analyst_data,required=True,requires=IS_IN_DB(db, db.analyst_data.id,'%(email)s'),update= db(db.analyst_data.user_id == auth.user.id).select(db.analyst_data.id)[0].id if auth.user else 0 , default =  db(db.analyst_data.user_id == auth.user.id).select(db.analyst_data.id)[0].id if auth.user else 0 , writable=False),
                Field('restored', 'boolean', default=False, writable=False),
                
                )

db.define_table('restore_data',
                Field('sample_data_id', db.sample_data,required=True,requires=IS_IN_DB( db, db.sample_data.id,'%(bab_number)s')),
                Field("bam_original_path","string"),
                Field("fastq1_original_path","string"),
                Field("fastq2_original_path","string"),
                Field("vcf_snps_original_path","string"),
                Field("vcf_indels_original_path","string"),
                Field("chad_server_path", "string"),
                
                Field("bam_chad_server","boolean"),
                Field("fastq1_chad_server","boolean"),
                Field("fastq2_chad_server","boolean"),
                Field("vcf_snps_chad_server","boolean"),
                Field("vcf_indels_chad_server","boolean"),

                Field("bam_alive","boolean"),
                Field("fastq1_alive","boolean"),
                Field("fastq2_alive","boolean"),
                Field("vcf_snps_alive","boolean"),
                Field("vcf_indels_alive","boolean"),
                
                Field('last_update','datetime',required=True,default=request.now,requires=IS_NOT_EMPTY()),
                
                
                )


db.define_table('ashg_data',
                Field("programNumber","string"),
                Field("sessionType","string"),
                Field("sessionTitle","string"),
                Field("title","string"),
                Field("authors","string"),
                Field("selGenes", "string"),                
                Field("content","text"),
                Field("Lupski","string"),
                             
                
                )


#db.define_table('bab_data',
#                Field('bab_number','string', required=True, unique=True, label="BAB number"),
#                Field('barcode','string', unique=True, label="Barcode"),
#                Field('patient_name','string', required=True, unique=True, label="Patient Name"),
#                Field('sex','string', required=True,requires=IS_IN_SET([ 'male', 'female'] )),
#                Field('dob','date',   label="Date of birth [yyyy-mm-dd]"),
#                Field('doa','date',   label="Date of arrival [yyyy-mm-dd]"),
#                Field('referral_physician','string', label="Physician"),               
#                Field('phenotype','string'),
#                 Field('user_id',db.auth_user, default = auth.user.id if auth.user else 0,  writable=False),  
#                #migrate=False         
#                )
#
#db.define_table('test',
#                Field("test1","string"),
#                Field("test2","text"),
#                Field("test3","date"),
#                Field("test4","integer"))
#db.define_table('intersect_form',
#                Field('sample1_id',db.sample_data,required=True,requires=IS_IN_DB(db(db.sample_data.user_id == auth.user), db.sample_data.id,'%(bab_number)s'), label="sample 1"),
#                Field('sample2_id',db.sample_data,required=True,requires=IS_IN_DB(db(db.sample_data.user_id == auth.user), db.sample_data.id,'%(bab_number)s'), label="sample 2"),
#)




#########

#db.define_table('physician', 
#                Field('name','string', required=True, unique=True, label="Name"),)
#
#db.define_table('patient_data',
#                Field('user_id',db.auth_user, default = auth.user.id if auth.user else 0),
#                Field('bab_number','string', required=True, unique=True, label="BAB number"),
#                Field('pheno_db_number','string'),
#                Field('patient_name','string', required=True, unique=True, label="Patient Name"),
#                Field('sex','string', required=True,requires=IS_IN_SET([ 'male', 'female'] )),
#                Field('dob','date',   label="Date of birth [yyyy-mm-dd]"),
#                Field('doa','date',   label="Date of arrival [yyyy-mm-dd]"),
#                Field('dos','date',   label="Date of Sending [yyyy-mm-dd]"),
#                Field('dop','date',   label="Date of Presentation [yyyy-mm-dd]"),
#                Field('referral_physician',db.physician, requires=IS_IN_DB(db, db.physician.id,'%(name)s')),
#                Field('inheritance','string',requires= IS_IN_SET(['AD','AR', 'Sporadic']), label="Likely inheritance model"),
#                Field('phenotype','string'),
#               #Field('pheno_db','boolean'),
#                Field('decision','string'),
##                Field('upload_file','upload'),
#                
#                              )
#
#db.patient_data.referral_physician.represent = lambda id, var: db.physician(id).name
#
#db.define_table('patient_relation',
#                Field('patient_1',db.patient_data,required=True,requires=IS_IN_DB(db(db.patient_data.user_id == auth.user), db.patient_data.id,'%(bab_number)s')),
#                Field('relation_type','string',required=True, requires=IS_IN_SET([ 'mother of','father of','sibling of'] )),
#                Field('patient_2',db.patient_data,required=True,requires=IS_IN_DB(db(db.patient_data.user_id == auth.user), db.patient_data.id,'%(bab_number)s')),
#                )
#
#db.patient_relation.patient_1.represent = lambda id, var: db.patient_data(id).bab_number
#db.patient_relation.patient_2.represent = lambda id, var: db.patient_data(id).bab_number

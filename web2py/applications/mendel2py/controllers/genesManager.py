'''
Created on May 1, 2013

@author: tgambin
'''

import csv

appDir = "/home/va/workspace/variant_analyzer/web2py/applications/mendel2py/"
rDir = appDir +  "modules/R/"
uploadDir = appDir + "uploads/"
outputDir = appDir + "output/"

@auth.requires_login()
@auth.requires_membership('mendel')
def index():
    
    def onAccept(form):
        found_genes = []
        not_found_genes = []
        input_file = (db(db.gene_list.id ==form.vars.id ).select(db.gene_list.ALL)[0]).input_file
        ff  =uploadDir + input_file
        csvReader = csv.reader(open(ff), delimiter='\t')
        for line in csvReader: 
            print line
            if len(line)> 0:
                genes = db(db.int_refseq_gene.name == line[0]).select(db.int_refseq_gene.ALL)
                if len(genes)> 0:
                    print "found " + line[0]
                    found_genes.append(line[0])
                    db.gene_group.insert(int_refseq_gene_id = genes[0].id, gene_list_id = form.vars.id)
                else:
                    print "not found " + line[0]
                    not_found_genes.append(line[0])
                    
        #if len(found_genes)>0:
            #session.flash = "Following genes have been added to the group '"+form.vars.gene_list_name+"': " + ",".join(found_genes)
        if len(not_found_genes)> 0:
            session.flash = "Following genes were not found: " + ",".join(not_found_genes)
        pass

    query=(db.gene_list )
    gene_list_create = SQLFORM.grid(query,oncreate=onAccept)
    return (dict (gene_list_create=gene_list_create))

@auth.requires_login()
@auth.requires_membership('mendel')
def showGroups():
    query=(db.gene_group )
    gene_group_select = SQLFORM.grid(query, create=False)
    return (dict (gene_group_select=gene_group_select))

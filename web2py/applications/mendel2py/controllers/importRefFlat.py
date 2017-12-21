'''
Created on May 27, 2009

@author: tgambin
'''
import itertools
import csv
import os, re, datetime, copy
import ftplib
import os
import sys, zipfile, os.path
import gzip

#import applications.welcome.modules.imidlog as imidlog
exec("from applications.%s.modules.utils import *" % request.application)


response.view='generic.html'

#table refFlat
#"A gene prediction with additional geneName field."
#    (
#    string  geneName;           "Name of gene as it appears in Genome Browser."
#    string  name;               "Name of gene"
#    string  chrom;              "Chromosome name"
#    char[1] strand;             "+ or - for strand"
#    uint    txStart;            "Transcription start position"
#    uint    txEnd;              "Transcription end position"
#    uint    cdsStart;           "Coding region start"
#    uint    cdsEnd;             "Coding region end"
#    uint    exonCount;          "Number of exons"
#    uint[exonCount] eimport gzip
# xonStarts; "Exon start positions"
#    uint[exonCount] exonEnds;   "Exon end positions"
#    )
#

########## Converts chromosme to int ##########

@auth.requires_login()
@auth.requires_membership('mendel')
def chrToInt(chr):
    ret = None
    if (chr.lower() == "chrx"):
        ret = 23
    elif (chr.lower() == "chry"):
        ret = 24
    elif (chr.lower() == "chrm"):
        ret = 25
    else:
        try:
            chr = chr.replace("chr" , "")
            chr = chr.replace("Chr" , "")
            ret = int(chr)
        except ValueError:
            ret = None
    return ret

################################################

@auth.requires_login()
@auth.requires_membership('mendel')
def readGenesFromRefFlat(fileName, type):
    genes = []
    csvReader = csv.reader(open(fileName), delimiter='\t')


    for line in csvReader:
        success = 1;
        j = 0 
        tmp = []
        # cells - parsing to int

        for cell in line:
            if ((type == "refFlat" and (j in [0, 1, 2, 4, 5, 9, 10])) or
                (type == "knownGene" and (j in [0, 1, 3, 4,  8, 9])) ):
                tmp.append(cell)
            if (type == "knownGene" and j ==0):
                tmp.append(cell)
            j += 1
        genes.append(tmp)
    
    return genes

@auth.requires_login()
@auth.requires_membership('mendel')
def readDictFromFile(fileName, type):
    dict = {}
    csvReader = csv.reader(open(fileName), delimiter='\t')


    for line in csvReader:
        tmp = []
        # cells - parsing to int
        j = 0
        for cell in line:
            if (j in [0,1]):
                tmp.append(cell)
            j += 1

        if (type == "refSeq"):
            if(dict.get(tmp[1], None) == None):
                dict [tmp[1]] = tmp[0]
        else:
            if(dict.get(tmp[0], None) == None):
                dict [tmp[0]] = tmp[1]
    return dict

@auth.requires_login()
@auth.requires_membership('mendel')
def isInt(x):
    try:
        int(x)
        return True

    except:
        return False

@auth.requires_login()
@auth.requires_membership('mendel')
def splitExons(exonStarts, exonStops):
    starts = filter(lambda(x): isInt(x)  , exonStarts.split(','))
    stops = filter(lambda(x): isInt(x) , exonStops.split(','))
    
        
    assert (len(starts) == len(stops))
    
    exons = []
    i = 0
    for s in starts:
        exons.append([int(starts[i]) , int(stops[i])])
        i += 1 
    
    return exons



###### MAIN

@auth.requires_login()
@auth.requires_membership('mendel')
def deleteRefSeqGenes():
    intervalsDeleted = 0
    # need testing ...
    c = 0  
    for i in db(db.int_refseq_exon.id > 0).select(db.int_refseq_exon.interval_id):
        c = c + 1
#        db(db.interval_overlap.interval_id_1 == i.interval_id).delete()
#        db(db.interval_overlap.interval_id_2 == i.interval_id).delete()
        intervalsDeleted = intervalsDeleted + db(db.interval_data.id == i.interval_id).delete()
        if (c % 100 == 0):
            db.commit()   
            imidlog.log( "exons deleted: " + str(c))
    
    db.commit()
    #import pdb;pdb.set_trace()
    imidlog.log("all exons intervals deleted");
    
    for c,i in enumerate(db(db.int_refseq_gene.id > 0).select(db.int_refseq_gene.interval_id)):
#        db(db.interval_overlap.interval_id_1 == i.interval_id).delete()
#        db(db.interval_overlap.interval_id_2 == i.interval_id).delete()
        intervalsDeleted = intervalsDeleted + db(db.interval_data.id == i.interval_id).delete()
        if (c % 100 == 0):
            db.commit()   
            imidlog.log( "refseq gene deleted: %s intervals_del: %d"%(str(c),intervalsDeleted))
    
    db.commit()    
        
    imidlog.log("all genes intervals deleted")
    
    genesDeleted = 0
    exonsDeleted = 0
    genesDeleted = genesDeleted +db(db.int_refseq_gene.id >= 0).delete()
    exonsDeleted = exonsDeleted +db(db.int_refseq_exon.id >= 0).delete()
    msg= "All refseq genes deleted (genesDeleted=%d exonsDeleted=%d intervalsDeleted=%d)" % (genesDeleted,exonsDeleted,intervalsDeleted)
    imidlog.log(msg)
    db.commit()
    return {'Message':msg}

@auth.requires_login()
@auth.requires_membership('mendel')
def getGenes(fileName, type):
        genes = readGenesFromRefFlat(fileName, type)
        genes = map (lambda (x): [x[0] ,x[1], chrToInt(x[2]) , int(x[3]), int(x[4]), splitExons(x[5], x[6]) ], genes)
        # remove those, for which chr is None 
        genes = filter (lambda(x): x[2] != None , genes)
        return genes;

@auth.requires_login()
@auth.requires_membership('mendel')
def importRefSeq(knownGeneFile, refSeqFile, knownToRefSeqFile):
    
    knownGenes = getGenes(knownGeneFile , "knownGene")
    refSeq = readDictFromFile(refSeqFile, "refSeq")
    knownToRefSeq = readDictFromFile(knownToRefSeqFile , "knownToRefSeq")
    imidlog.log("importRefSeq: files read")
   # assert(0==1)
    
    delmsg = deleteRefSeqGenes()

    #import pdb;pdb.set_trace()
    
    counter =0
    for g in knownGenes:
        
        geneName = g[0]
        if(knownToRefSeq.get(geneName, None) != None):
            if(refSeq.get(knownToRefSeq[geneName], None) != None):
                geneName= refSeq[knownToRefSeq[geneName]]
            
                
        if counter % 100==0: 
            imidlog.log("nr of genes: " + str(counter))
            db.commit()
        counter += 1
        
        gene_interval_id = db.interval_data.insert(chr=g[2], startPos=g[3], stopPos=g[4], int_type = g_interval_data_types['int_refseq_gene'])
        addOverlaps(db,gene_interval_id )
        
        
        
        gene_id = db.int_refseq_gene.insert(interval_id=gene_interval_id, name=geneName)
        tmp = (g[5]) # exons
        for t in tmp: # add geneName, chr,  exonStart, exonStop...
           exon_interval_id = db.interval_data.insert(chr=g[2], startPos=t[0], stopPos=t[1] , int_type = g_interval_data_types['int_refseq_exon'])
           #Overlaps are not added for exons
           #addOverlaps(db,exon_interval_id )
        
           db.int_refseq_exon.insert(interval_id=exon_interval_id , int_refseq_gene_id=gene_id)
           
    db.commit()
    delmsg.update(upload="upload success!")
    imidlog.log("importRefSeq completed! delmsg=%s"%str(delmsg))
    return delmsg

@auth.requires_login()
@auth.requires_membership('mendel')
def ungzipFile(inFile, outFile):
    zfile = gzip.GzipFile(inFile)
    content = zfile.read()
    zfile.close()
    fileUngziped =outFile
    ungziped = open (outFile, "wb")
    ungziped.write(content)
    
@auth.requires_login()
@auth.requires_membership('mendel')
def downloadFromFtp(host, remoteFile,outFile ):
    imidlog.log("importRefSeq: downloading files from ftp")
    f = ftplib.FTP(host, "anonymous", "password")
    file =  outFile 
    f.retrbinary("RETR %s" % remoteFile, open(file, "w").write)
    f.close()
    # unzip file
    
@auth.requires_login()
@auth.requires_membership('mendel')
def index():
    form = FORM(INPUT(_type='submit',  _value='update refSeq from UCSC'))
    message = ''
    if form.accepts(request.vars, session):
        host = 'hgdownload.cse.ucsc.edu'
       
       
        
        ##################### New database session
        session._unlock(response);
        session.forget();
        execfile(os.path.join(request.folder,'models/db.py'))
        ########################################3
        
        refFlatFile = 'refFlat.txt'
        knownGeneFile = 'knownGene.txt'
        knownToRefSeq = 'knownToRefSeq.txt'
        outDir = 'applications/mendel2py/uploadsFTPs/'
        outFileRefFlat = outDir + refFlatFile
        outFileKnownGene = outDir + knownGeneFile
        outFileKnownToRefSeq = outDir + knownToRefSeq
        remotePath = '/goldenPath/hg19/database/'
        
        
        
        downloadFromFtp(host,remotePath +refFlatFile +'.gz',  outFileRefFlat + '.gz')
        ungzipFile( outFileRefFlat + '.gz',  outFileRefFlat)
        
        downloadFromFtp(host,remotePath +knownGeneFile +'.gz',  outFileKnownGene + '.gz')
        ungzipFile( outFileKnownGene + '.gz',  outFileKnownGene)
        
        downloadFromFtp(host,remotePath +knownToRefSeq +'.gz',  outFileKnownToRefSeq + '.gz')
        ungzipFile( outFileKnownToRefSeq + '.gz',  outFileKnownToRefSeq)
        
        
        importRefSeq(outFileKnownGene , outFileRefFlat, outFileKnownToRefSeq)
        response.flash = 'upload success!'
   
    return dict(form=form);


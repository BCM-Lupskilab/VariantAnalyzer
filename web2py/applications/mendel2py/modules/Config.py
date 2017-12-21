'''
Created on May 31, 2009

@author: tgambin
'''

class Config:
    '''
    classdocs
    '''
    #'/home/imid/imid2py-prod/www/ucsc_imid_tracks/'
    
    #Toronto CNVs
    #TorCNV_host = 'http://projects.tcag.ca/variation/downloads'
    #TorCNV_remoteFile = 'variation.hg18.v8.aug.2009.txt'
    #TorCNV_outDir = 'applications/welcome/uploadsFTPs/'
    #TorCNV_outFile = TorCNV_outDir + 'variation.hg18.v8.aug.2009.txt'    
    
    #UCSC
    ucscURL = 'https://genome.ucsc.edu/'
    #ucscURL = 'http://genome-mirror.binf.ku.dk/'
    #ucscURL = 'http://genome-mirror.bscb.cornell.edu/'
    #ucscURL = 'http://genome-mirror.duhs.duke.edu/'
    ucscCustomTrack = 'cgi-bin/hgTracks'
    #decipherSearchPosition = 'https://decipher.sanger.ac.uk/perl/application/search?userinput='
    
    #myIpAddress = 'bioputer.mimuw.edu.pl:8443'
    httpPref="http://"
    
    localRemoteUser = 'ucscuser'
    localRemotePassword = 'klduio3'
    
    #localRemoteAccessAddress = "bioputer.mimuw.edu.pl:8441"
    #nonHttpsAddress="bioputer.mimuw.edu.pl:8442"
    
    #serverLocalRootPath = '/home/imid/imid2py-prod/www/ucsc_imid_tracks/'
    #serverLocalHomePath = '/home/imid/imid2py-prod/imid2py-test/'
    
    
    #pathTo_wkhtmltopdf = '/home/imid/bin/wkhtmltopdf-amd64';
    #pathTo_wkhtmltoimage = '/home/imid/bin/wkhtmltoimage-amd64';
    
    
    #URL Path below links to the serverLocalRootPath
    localUCSCurl = 'ucsc_imid_tracks' 
    localReportsUrl = 'imid_reports' 
    hgVersion = 'hg19'
    
    logFilePath = '/var/log/mendelLog/'
    
    #Max Concurrent jobs:
    maxConcurrentJobs  = 5
     

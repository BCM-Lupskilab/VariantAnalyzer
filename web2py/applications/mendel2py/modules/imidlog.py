'''
Created on 2009-06-29

@author: maciek
'''

import os,datetime
from applications.mendel2py.modules.Config import Config

logFileName = 'imidlog.txt'

def log(message):
    #TODO do we need implement locking mechanism (semaphor) for multiple threads??
    datestr=datetime.datetime.strftime(datetime.datetime.utcnow(),'%y/%m/%d %H:%M:%S')    
    file = open(os.path.join(Config.logFilePath,logFileName),'a')
    file.write('%s : %s\n' % (datestr,message))
    file.close()
    print('IMIDLOG: %s : %s' % (datestr,message))
    pass

def logfilepath():
    return Config.logFilePath
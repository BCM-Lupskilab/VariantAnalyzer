'''
Created on May 1, 2013

@author: tgambin
'''

response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%(Tomasz Gambin)s <%(gambin@bcm.edu)s>' % settings
response.meta.keywords = settings.keywords
response.meta.description = settings.description
response.menu = [
(T('Home'),URL('default','index')==URL(),URL('default','index'),[]),
(T('Data'),URL('sampleManager','index')==URL(),URL('sampleManager','index'),[
         (T('Samples'),URL('sampleManager','index')==URL(),URL('sampleManager','index'),[]),
         (T('Results'),URL('resultManager','index')==URL(),URL('resultManager','index'),[]),
         
         (T('ASHG 2014 abstracts'),URL('ashg','index')==URL(),URL('ashg','index'),[]),
         
         
         (T('Search requests'),URL('requestManager','index')==URL(),URL('requestManager','index'),[]),
         (T('Restore requests'),URL('restore','index')==URL(),URL('restore','index'),[]),
         
         #(T('BAB database'),URL('babSample','index')==URL(),URL('babSample','index'),[]),
         
         #(T('Patients'),URL('patientManager','index')==URL(),URL('patientManager','index'),[]),
         #(T('Relations'),URL('relationManager','index')==URL(),URL('relationManager','index'),[]),
         (T('Genes'),URL('relationManager','index')==URL(),URL('genesManager','index'),[
               (T('Import gene list'),URL('genesManager','index')==URL(),URL('genesManager','index'),[]),
               (T('Show existing gene groups'),URL('genesManager','showGroups')==URL(),URL('genesManager','showGroups'),[]),
                                                                                           ]),
                                                                             
          ]),
    
(T('Analysis'),False,URL(),[
                            (T('Single patient'),URL('test','index')==URL(),URL('test','index'),[
                                                (T('custom gene list annotation'),URL('test','index')==URL(),URL('test','index'),)]),
                            (T('Cohort analysis'),URL('geneAnalyzer','index')==URL(),URL('geneAnalyzer','index'),[
                                                (T('Get all mutations by gene name'),URL('geneAnalyzer','index')==URL(),URL('geneAnalyzer','index'),[])]),
                                              #  (T('Compound heterozygous'),URL('test','index')==URL(),URL('test','index'),[]),
                                              #  (T('Homozygous'),URL('test','index')==URL(),URL('test','index'),[])
                                                

                            #(T('Family analysis'),URL('test','index')==URL(),URL('test','index'),[
                            #                  (T('Trio analysis'),URL('test','index')==URL(),URL('test','index'),[
                            #                         (T('Recessive'),URL('test','index')==URL(),URL('test','index'),[]),
                            #                         (T('De novo'),URL('test','index')==URL(),URL('test','index'),[]),
                            #                                                                    ]),
                             #                   (T('Other'),URL('test','index')==URL(),URL('test','index'),[
                              #                       (T('Intersect variants'),URL('test','intersect')==URL(),URL('test','intersect'),[]),
                               #                      (T('Recessive'),URL('test','index')==URL(),URL('test','index'),[]),
                                #                     (T('De novo'),URL('test','index')==URL(),URL('test','index'),[]),
                                 #                                                               ]),
                                  #      ]),
                            ]),
#(T('Reports'),URL('report_manager','index')==URL(),URL('report_manager','index'),[]),
                            
]
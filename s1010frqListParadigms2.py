'''
Created on 15 Apr 2019

@author: qumtie
'''

import os, sys, re
import mdParadigms2
from collections import defaultdict
from builtins import int




class clFrqListParadigms(object):
    '''
    open frequency dictionary; read into memory, load Paradigms class
    
    '''


    def __init__(self, FFrqList):
        '''
        Constructor
        '''
        sys.stderr.write('initialising \n')
        self.DFrqList = {}
        sys.stderr.write(str(sys.getsizeof(self.DFrqList)) + '\n')
        self.frqListReader(FFrqList)
        sys.stderr.write(str(sys.getsizeof(self.DFrqList)) + '\n')
        
        OParadigms = mdParadigms2.clParadigms('mdParadigms2.txt')
        self.DInfl = OParadigms.getInfl() # dictionary of inflections 
        self.DClass = OParadigms.getClass() # dictionary of classes
        
        # not used... 
        self.DHypotheses = defaultdict(int) # dictionary of frozensets - sum of word form frequencies as value; lemma as index??? or: convert to list?
        
        self.LHypotheses4WFRanked = [] # list of ranked hypotheses for each word form
        self.DParadigms = defaultdict(list) # main data structure
        
        
        return


    def frqListReader(self, FFrqList):
        for SLine in FFrqList:
            SLine = SLine.strip()
            try:
                (SFrq, SWord) = re.split(' ', SLine, 1)
            except:
                continue
            
            if int(SFrq) > 3:
                self.DFrqList[SWord] = int(SFrq)
            
        
        
        return
    
    
    def printData(self):
        sys.stderr.write('checking hypotheses \n\n')
        IConfirmed = 0
        ICntAll = 0
        
        
        for (k, v) in sorted(self.DFrqList.items(), key=lambda x: x[1], reverse=True) :
            # find the top confirmed hypothesis
            ICntAll += 1
            if ICntAll % 10000 == 0: sys.stderr.write('hyp:: ' + k + ' : ' + str(v) + '\n')
            if v > 1:
                # sys.stdout.write(k + '\t' + str(v) + '\n')
                LSplits = self.splitByInfl(k, self.DInfl)
                if ICntAll % 10000 == 0: sys.stderr.write('LSplits:: ' + k + ' : ' + str(LSplits) + '\n')
                DLocHypotheses = defaultdict(float) # ranked local hypotheses: which one gets more matches 
                # rank all splits!!!
                for TSplit in LSplits:
                    # for each specific split of a word form...
                    # possibility: the same paradigm available for different splits of the same word form???
                    (SStem, SInfl, LClassNCateg) = TSplit
                    
                    for (SClass, Categs, Example) in LClassNCateg:
                        # for each set of class categories predicted by the split, e.g.:
                        # ою    [('D1h', 'n115.N.ins.sing.fem', 'фабрик'), ('Ah', 'a315.A.ins.sing.fem', 'гарн'), ('As', 'a315.A.ins.sing.fem', 'синь'), ('Aj', 'a315.A.ins.sing.fem', 'безкрай'), ('Ap', 'a315.A.ins.sing.fem', 'братов')]
                        
                        
                        # BConfirmHypothesis = False
                        # generate projected word forms, and test if they are found in a corpus
                        LHypotheses = self.genByInfl(SStem, SClass)
                        if ICntAll % 10000 == 0: sys.stderr.write('LHypotheses1:: ' + k + ' : ' + str(LHypotheses) + '\n')
                        
                        (LHypotheses2, ICountMatches4split, IProjMatches4split, ICountPC) = self.lookupParadigm(LHypotheses)
                        if ICntAll % 10000 == 0: sys.stderr.write('LHypotheses2:: ' + k + ' : ' + str(LHypotheses2) + '\n')
                        if ICntAll % 10000 == 0: sys.stderr.write('m: %(ICountMatches4split)d :: no: %(IProjMatches4split)d :: pc: %(ICountPC).4f\n' % locals())
                        # and rank -- highest to lowest ??
                        
                        # threshold approach is rejected, in favour of the top-ranked approach...
                        # if ICountPC > 0.2:
                        if ICountMatches4split > 1:
                            IConfirmed += 1
                            # now rank and take top
                            # if IConfirmed % 50000 == 0: sys.stderr.write(str(IConfirmed) + ' : ' + str(THyp2) + '\n')
                            # if IConfirmed % 50000 == 0: sys.stderr.write(str(IConfirmed) + ' : ' + '\n')
                            # BConfirmHypothesis = True
                            # SetHyp = frozenset(LHypotheses)
                            # SetHyp = frozenset(LHypotheses2)
                            TParadigmProj = (k, tuple(LHypotheses2)) # tuple -- immutable, can be an index
                            ### DLocHypotheses[SetHyp] += 1 # how many els matched?
                            # add to the dictionary with the proportion score
                            DLocHypotheses[TParadigmProj] = ICountPC
                        
                        # remove to a better place ???
                        # self.LHypotheses4WFRanked.append(DLocHypotheses) # list of dictionaries with frq for matches ???

                LLocHypothesesRanked = sorted(DLocHypotheses.items(), key=lambda x: x[1], reverse=True)
                if len(LLocHypothesesRanked) > 0:
                    TTSplitTop = LLocHypothesesRanked[0] # what to do if several ranked the same at the top :: euristics for hypothesis? # evaluation by sampling...
                    self.LHypotheses4WFRanked.append(TTSplitTop)
                else:
                    if ICntAll % 10000 == 0:
                        sys.stderr.write('LLocHypothesesRanked = 0 :: ' + k + ' : ' + str(LLocHypothesesRanked) + '\n')
                if ICntAll % 10000 == 0: sys.stderr.write('LLocHypothesesRanked:: ' + k + ' : ' + str(LLocHypothesesRanked) + '\n')
                if ICntAll % 10000 == 0: sys.stderr.write('TTSplitTop:: ' + k + ' : ' + str(TTSplitTop) + '\n')
                
                
                            ## self.DHypotheses[SetHyp] += 1
            # sys.stdout.write(str(LHypotheses) + '\n\n')
            # record in a dictionary and print separately...
        sys.stderr.write('confirmed paradigms :: %(IConfirmed)d :: %(IConfirmed)d :: %(IConfirmed)d\n' % locals())

        return
    
    def lookupParadigm(self, LHypotheses):
        LHypotheses2 = []
        ICountMatches4split = 0
        IProjMatches4split = 0

        for (SWordForm, SWordSplitForm, SCat, SClass, SExamp) in LHypotheses:
            if SWordForm in self.DFrqList.keys():
                THyp2 = (SWordForm, SWordSplitForm, SCat, SClass, SExamp, 'FOUND')
                ICountMatches4split += 1
                # + record 'found' or 'generated' --- to be able to count found items...
            else:
                THyp2 = (SWordForm, SWordSplitForm, SCat, SClass, SExamp, '-proj')
                IProjMatches4split += 1
                # pass
            LHypotheses2.append(THyp2)
        # end of loop: morph hypotheses for a specific split
        ICountPC = float(ICountMatches4split) / float(ICountMatches4split + IProjMatches4split)
        return (LHypotheses2, ICountMatches4split, IProjMatches4split, ICountPC)
    
    
    def printHypotheses(self):
        sys.stderr.write('writing paradigms...\n')
        j = 0
        # sys.stdout.write(str(sorted(self.DHypotheses.items(), reverse = False)) + '\n\n')

        for (k, v) in sorted(self.DHypotheses.items(), key=lambda x: x[1], reverse = True):
        # for (k, v) in sorted(self.DHypotheses.items(), reverse = False):
            j+=1;
            if j% 50000 == 0: 
                # sys.stderr.write(str(k) + '\n')
                sys.stderr.write('.')
            sys.stdout.write(str(sorted(k)) + '\n\n')
            LKeys = list(k)
            LKeysSorted = sorted(LKeys, key=lambda y: y[1])
            TLemma = LKeysSorted[0]
            SLemma = TLemma[0]
            SFrq = str(v)
            for el in sorted(LKeys, key=lambda y: y[1]):
                (SWordForm, SPos, SPattern, SFound) = el
                # sys.stdout.write(str(el) + '\t' + str(v) + '\n')
                sys.stdout.write('%(SWordForm)s %(SLemma)s %(SPos)s %(SPattern)s %(SFound)s %(SFrq)s\n' % locals())
            sys.stdout.write('\n')
            
                
    def printHypothesesList(self):
        sys.stderr.write('writing paradigms list...\n')
        j = 0
        # for DEl in sorted(self.LHypotheses4WFRanked):
        for DEl in self.LHypotheses4WFRanked:
            if len(DEl.items()) > 0: j+=1
            # if j% 10000 == 0: sys.stderr.write(str(DEl) + '\n')
            # if j% 10000 == 0: sys.stderr.write('.')
            
            # sys.stdout.write(str(sorted(DEl.items())) + '\n\n')
            for (k, v) in sorted(DEl.items(), key=lambda x: x[1], reverse=True):
                sys.stdout.write(str(k) + ' : ' + str(v) + '\n')
            sys.stdout.write('\n')
            
            
            
            '''
            LKeys = list(k)
            LKeysSorted = sorted(LKeys, key=lambda y: y[1])
            TLemma = LKeysSorted[0]
            SLemma = TLemma[0]
            SFrq = str(v)
            for el in sorted(LKeys, key=lambda y: y[1]):
                (SWordForm, SPos, SPattern, SFound) = el
                # sys.stdout.write(str(el) + '\t' + str(v) + '\n')
                sys.stdout.write('%(SWordForm)s %(SLemma)s %(SPos)s %(SPattern)s %(SFound)s %(SFrq)s\n' % locals())
            sys.stdout.write('\n')
            '''
        return
    
    def printTopParadigmList(self):
        sys.stderr.write('writing paradigms list...\n')
        # j = 0
        for TTop in self.LHypotheses4WFRanked:
            sys.stdout.write(str(TTop) + '\n')
        sys.stdout.write('\n')
             
        # LHypotheses4WFRanked
        
        return
    
    
    def mergeTopParadigmList(self):
        sys.stderr.write('merging paradigms\n')
        for (TWFormPar, FScore) in self.LHypotheses4WFRanked:
            (SWForm, TPar) = TWFormPar
            self.DParadigms[TPar].append((SWForm, FScore))
            
            # self.DParadigms[TPar]
            # sys.stdout.write(str(SWForm) + '\n') 
            # sys.stdout.write(str(TPar) + '\n')
            # sys.stdout.write(str(FScore) + '\n\n')
        
        sys.stderr.write('printing paradigms\n')
        for (TTPar, LVal) in self.DParadigms.items():
            # sys.stdout.write(str(TPar) + '\t' + str(LVal) + '\n')
            TEntryLemma = TTPar[0]
            SVal = str(LVal)
            (WFormLemma, WFormSplitLemma, SCatsLemma, SClassLemma, SExampLemma, SFoundLemma) = TEntryLemma
            for TEntry in TTPar:
                (WForm, WFormSplit, SCats, SClass, SExamp, SFound) = TEntry
                
                sys.stdout.write('%(WForm)s %(WFormLemma)s %(SCats)s %(SClass)s %(SExamp)s %(SFound)s %(WFormSplit)s %(SVal)s\n' % locals())
            
            # sys.stdout.write(str(TTPar) + '\t' + str(LVal) + '\n')

        
        # self.DParadigms
        return
    
        

    
    def splitByInfl(self, SWord, DInfl):
        '''
        returns splits by inflection (empty inflection not used now)
        split word; then form hypotheses by inflection class...
        '''
        LSplits = []
        for SKey, LValue in DInfl.items():
            if SKey == '': continue
            m = re.search('^(.+?)(' + SKey + ')$', SWord)
            if m == None: continue
            TMGroups = m.groups() # match groups
            TGroups = (TMGroups[0], TMGroups[1], LValue)
            
            # TGroups = TGroups + tuple(SValue)
            LSplits.append(TGroups)
        # the list of tuples returned
        # sys.stderr.write(str(LSplits) + '\n')
        return LSplits
    
    def genByInfl(self, SStem, SClass):
        
        LTHypotheses = []
        
        LTInflectCategs = self.DClass[SClass]
        for (SInfl, SCats, SExamp) in LTInflectCategs:
            THypoth = (SStem + SInfl, SStem +  '|' + SInfl, SCats, SClass, SExamp) # full form; split form, category, infl class, example
            LTHypotheses.append(THypoth)
        
        
        return LTHypotheses






if __name__ == '__main__':
    '''
    the first argument should be a frequency glossary of word forms in the format generated from corpus by shell commands:
    
    
    '''
    # SFDebug = open(sys.argv[2] + '_debug.txt', 'w')
    FFrqList = open(sys.argv[1], 'rU')
    
    OFrqListParadigms = clFrqListParadigms(FFrqList)
    OFrqListParadigms.printData()
    # OFrqListParadigms.printHypotheses()
    # OFrqListParadigms.printHypothesesList()
    # OFrqListParadigms.printTopParadigmList() # dictionary is needed here: merge paradigms confirmed from different sources ???
    OFrqListParadigms.mergeTopParadigmList()
    
    
    
'''
Created on 26 Oct 2014

@author: qumtie
'''
import sys, os, re
from collections import defaultdict
FDebug = open('uaparadigms-debug.txt', 'w')
class clParadigms(object):
	'''
	reading the list of paradigms with features; index by ending; splitting function, etc.
	'''


	def __init__(self, SFileName=''):
		'''
		Constructor
		'''
		if SFileName=='': SFileName='mdParadigms2.txt'
		
		self.DParInfl = defaultdict(list)
		self.DParClass = defaultdict(list)
		FInText = open(SFileName, 'rU')
		for SLine in FInText:
			SLine = SLine.rstrip()
			if SLine == '': continue
			if re.match('\#', SLine): continue
			if re.match('[ \t]+', SLine): continue
			
			LLine = re.split('[\t]+', SLine)
			try:
				(SWords, SFeat) = LLine[:2]
				LWords = re.split(' +', SWords)
			except:
				sys.stderr.write('split error: %(SLine)s\n' % locals())
				LWords = []
				SFeat = ''
			
			# print(SFeat)
			for SWord in LWords:
				LVariants = re.split('/', SWord)
				# print('\t variants:')
				for SVariant in LVariants:
					# print('\t\t' + SVariant)
					
					try:
						(SStem, SInfl) = re.split('\-', SVariant, 1)
						(SInflEnd, SInflClass) = re.split('\~', SInfl)
					except:
						print('ERROR: '+ SVariant)
						(SStem, SInflEnd, SInflClass) = ('', '', '')
					# print('\t\tstem:' + SStem + '\t' + 'infl:' + SInflEnd + '\tclass:' + SInflClass)
					
					TInflValue = (SInflClass, SFeat, SStem)
					TClassValue = (SInflEnd, SFeat, SStem)
					self.DParInfl[SInflEnd].append(TInflValue)
					self.DParClass[SInflClass].append(TClassValue)
				
			
						
			# print(str(LWords) + '\t' + SFeat)
		self.printDict(self.DParInfl)
		self.printDict(self.DParClass)
			
	def getInfl(self):
		return self.DParInfl
	
	def getClass(self):
		return self.DParClass
		
	def printDict(self, D2Print):
		for Key, Value in sorted(D2Print.items(), key=lambda a:a[1], reverse=False):
			FDebug.write(str(Key) + '\t' + str(Value) + '\n')
			
		return


		
if __name__ == '__main__':
	clParadigms(sys.argv[1])

		
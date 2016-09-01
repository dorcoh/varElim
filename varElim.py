"""
	Machine Learning 097209
	Homework 2 - Question 5
	Variable elimination algorithm assignment

	By:
		Dor Cohen
		Zeev Gutman
		Adi Omari
"""
import itertools
import random
import copy
import sys
import collections

class Factor():
	""" 
		Factor data structure:
			- variable list , e.g: ['A','B','C']
			- a list of key-value tuples (dictionary), e.g: [ ((F,F,F),0.2), ((F,F,T),0.9), ... ]
			* scalar factor (only value) also can be represented by empty var list and one key-value pair
	"""
	def __init__(self, varList, keyValues = None, scalar=False):
		# size of factor
		self.size = len(varList)
		# list of variables
		self.varList = varList
		# value only or factor
		self.scalar = scalar

		# create random values automatically (for testing)
		if keyValues == None:
			# list of tuples of all permutations [ (F,F,F) , (F,F,T) ... ]
			self.tuples = self.generatePerms(self.size)
			# assign some random values to permutations, e.g: [ ((F,F,F),1) , ((F,F,T),5) , ... ]
			random.seed(134)
			self.keyValues = self.assignRandValues(self.tuples)
		
		# or insert key-values manually
		# hashable list (tuples)
		else:
			self.keyValues = keyValues

		# create the mapping of variables (dictionary)
		self.dict = dict(self.keyValues)
		
	def generatePerms(self, length):
		# create all permutations
		perms = list()
		for perm in itertools.product([False, True], repeat=length):
			perms.append(perm)
		return perms

	def assignRandValues(self, tuples, default=0):
		# assign random values for new factors
		keyValues = list()
		for t in tuples:
			val = random.randint(0,10)
			w = tuple((t,val))
			keyValues.append(w)
		return keyValues

	def printFactor(self):
		print self.varList
		for k in sorted(self.dict):
			print k, self.dict[k]
		print

	def printNames(self):
		print self.varList

	def getSize(self):
		return self.size

	def getVarlist(self):
		return self.varList

	def getDict(self):
		return self.dict

	def inFactor(self,var):
		if var in self.varList:
			return True
		else:
			return False

	def isScalar(self):
		return self.scalar


def restrict(factor, variable, value):
	"""
	IN:
		Factor instance
		variable - to be restricted
		value - of the the variable
	OUT:
		(Factor) restricted factor
	"""
	print "Restrict {0} = {1}".format(variable,value)
	
	oldDict = factor.getDict()
	varList = factor.getVarlist()
	
	# if factor size is 1
	if not factor.isScalar() and len(varList) == 1:
		varList = []
		key = (value,)
		keyValTuple = [((key, oldDict[key]))]
		# return factor instance that contains only value (e.g: 0.25)
		return Factor(varList,keyValTuple,True)

	# otherwise need to remove some variable
	
	# position of var to be removed
	varPos = 0
	for v in varList:
		if v == variable:
			varList.remove(variable)
			break
		varPos += 1

	# restrict variable
	newFactor = []
	for k in oldDict:
		if k[varPos] == value:
			# generate a new key
			key = tuple([e for i, e in enumerate(k) if i not in [varPos]])
			# add to new dictionary
			newFactor.append((key, oldDict[k]))

	return Factor(varList,newFactor)

def productFactor(factor1, factor2):
	"""
		FUNCTION ASSUMES VALIDITY (common variable and one of the cases below)
		FUNCTION ASSUMES |factor1| >= |factor2|
	IN:
		2 Factor instances
	OUT:
		(Factor) factor1 * factor2
	"""
	a = factor1.getVarlist()
	b = factor2.getVarlist()
	print "Multiply {0} in {1}".format(a,b)

	aSize = factor1.getSize()
	bSize = factor2.getSize()
	dictA = factor1.getDict()
	dictB = factor2.getDict()

	# case 0
	# one factor and one scalar
	# e.g ['A'] * 0.25
	if factor2.isScalar():
		for k in dictA:
			for kb in dictB:
				dictA[k] *= dictB[kb]
		return Factor(a,dictA.items())

	# case 1
	# factors are of the same size
	# factors have same variables
	# e.g ['A','B'] * ['A','B']
	if aSize == bSize:
		if collections.Counter(a) == collections.Counter(b):
			# iterate and multiply same rows
			for key in sorted(dictA):
				dictA[key] = dictA[key]*dictB[key]
			return Factor(a,dictA.items())

	# case 2
	# one factor of size > 1 , one of size 1
	# there is a common variable in their scope
	# e.g ['A','B'] * ['B']

	# get the common var
	if bSize == 1:
		if b[0] in a:
			comVar = b[0]
			idx = a.index(comVar)
			# iterate over dict keys and multiply on right cols
			for key in sorted(dictA):
				if key[idx] == True:
					dictA[key] *= dictB[(True,)]
				else:
					dictA[key] *= dictB[(False,)]
			return Factor(a,dictA.items())

	# case 3
	# both factors are of size > 1
	# one of them is contained in the other (same order)
	# e.g: ['A','B','C'] * ['B','C']
	con = contains(a,b)
	if con:
		start = con[0]
		end = con[1]
		# multiply
		for key in sorted(dictA):
			reducedKey = key[start:end]
			dictA[key] *= dictB[reducedKey]
		return Factor(a,dictA.items())

	# case 4
	# both factors are of size > 1
	# they have common vars in their scope
	# and there's a new variable in the smaller one
	# e.g ['A','B','C'] * ['B','C','E']

	# create new variable list - 
	# union on both factors
	varList = sorted( ( list(set(a) | set(b)) ) )
	# find the commmon range
	comRange = commonRange(a,b)
	if comRange:
		# variables range in original factor
		start,end = comRange[0],comRange[1]
		# generate all permutations
		perms = list(itertools.product([False,True], repeat=len(varList)))
		# create a list of (key,value)
		listOfTuples = []
		for p in perms:
			listOfTuples.append((p,0))
		# init new dictionary of bigger size
		newDict = dict(listOfTuples)
		# assign values
		for k in sorted(newDict):
			#print k,k[0:aSize],k[start:]
			newDict[k] = dictA[k[0:aSize]]*dictB[k[start:end+1]]
		return Factor(varList, newDict.items())

def contains(big, small):
	""" 
			check if small list is subset of big list
			e.g ['A','B','C'] * ['B','C'] 
		In:
			2 lists of variables, ,|big| > |small|
		Out: 
			False if not a subset
			else: common variables index range (in factor1)
			(start,end+1)
	"""
	for i in xrange(len(big)-len(small)+1):
		for j in xrange(len(small)):
			if big[i+j] != small[j]:
				break
		else:
			return i, i+len(small)
	return False

def commonRange(big, small):
	""" 
		** check if small list is partly contained in big list
		** e.g ['A','B','C'] * ['B','C','E'] **
		In:
			2 list of variables, |big| > |small|
		Out: 
			False if not contained
			else: common variables index range (in factor1) 
			(start,end+1)
	"""
	start = None
	j = 0
	for i in xrange(len(big)):
		if big[i] != small[j]:
			continue
		else:
			if start == None:
				start = i
			j+=1

	if start == None:
		return False
	end = j+1
	return (start,end)

def sumout(factor, variable):
	"""
	IN:
		Factor instance
	OUT:
		(Factor) sums out a variable from the factor
	"""
	print "Sum out {0} in factor:".format(variable)
	factor.printNames()
	
	varList = factor.getVarlist()

	# get position of var to be summed
	varPos = 0
	for v in varList:
		if v == variable:
			varList.remove(variable)
			break
		varPos += 1

	# positions of other variables
	posList = [i for i in range(0,factor.getSize()) if i != varPos]

	# create new tuple dictionary
	perms = list()
	for perm in itertools.product([False, True], repeat=len(varList)):
		perms.append((perm,0))
	perms = dict(perms)

	oldDict = factor.getDict()

	# sum out variable
	for k in oldDict:
		# extract new key to sum to dict
		key = tuple([e for i, e in enumerate(k) if i in posList])
		# sum
		perms[key] += oldDict[k]

	# return new Factor instance
	# scalar
	if not factor.isScalar() and len(varList)==0:
		return Factor(varList, perms, True)
	# regular factor
	else:
		return Factor(varList, perms)

def normalize(factor):
	"""
	IN:
		Factor instance
	OUT:
		(Factor) normalized factor
	"""
	print "Normalize factor: "
	factor.printNames()

	varList = factor.getVarlist()
	oldDict = factor.getDict()
	
	# sum
	z = 0
	for k in oldDict:
		z += oldDict[k]

	# normalize
	for k in oldDict:
		oldDict[k] = float(oldDict[k])/z

	# return normalized Factor instance
	return Factor(varList,oldDict.items())

def inference(factorList, queryVariables, hiddenVars, evidenceList):
	"""
			Procedure to inference probability, e.g P(A|B=b,C=c)
		In:
			factorList - list of Factor instances
			queryVariables - list of vars
			hiddenVars - list of ordered vars to eliminate
			evidenceList - list of evidence tuples, e.g [ ('A',True), ..]
	""" 
	print "Factor list: {0}".format([x.getVarlist() for x in factorList])
	print "Query variable: {0}".format(queryVariables)
	print "Evidence = {0}".format(evidenceList)
	print "******************************************"
	nL()

	factors = []	
	if evidenceList:
		print "Restriction part:"
		nL()
		# iterate over all factors
		for f in factorList:
			# iterate over all evidence
			for e in evidenceList:
				# apply evidence to factor
				if f.inFactor(e[0]):
					f = restrict(f,e[0],e[1])
					f.printFactor()
			# applied all evidence to current factor
			# append to list
			factors.append(f)
	else:
		# no evidence
		factors = copy.deepcopy(factorList)
	
	print "Sum product elimination part:"
	nL()
	for var in hiddenVars:
		if var in queryVariables:
			continue
		# list of relevant factors to multiply
		currentFactors = varInFactors(factors,var)
		if currentFactors:
			print "Currently eliminating variable: {0}".format(var)
			# more than one relevant factor
			# multiply relevant factors between themselves
			# while there's a valid multiplication
			if len(currentFactors) > 1:
				multiplyLoop(currentFactors,factors)

			# if only one factor left then sumout and append to factors list
			if len(currentFactors) == 1:
				newFac = sumout(currentFactors[0],var)
				print "Result:"
				newFac.printFactor()
				# remove old factor from list
				if currentFactors[0] in factors:
					factors.remove(currentFactors[0])
				factors.append(newFac)

	# factors left: involving query vars only
	# assumes only one query var exists
	if len(queryVariables):
		# get relevant factors
		query = queryVariables[0]
		currentFactors = varInFactors(factors,query)
		# add also values (scalars) to list
		for f in factors:
			if f.getSize() == 0:
				currentFactors.append(f)

		# multiply
		if len(currentFactors) > 1:
			multiplyLoop(currentFactors,factors)
		
		# if got here - no more factors to multiply
		# append result to factor
		for f in currentFactors:
			factors.append(f)

	# normalize part
	if len(factors) == 1:
		norm = normalize(factors[0])
		nL()
		print "Result:"
		norm.printFactor()

def multiplyLoop(currentFactors,factors):
	"""
			Procedure to multiply all valid factors in currentFactors
		IN:
			currentFactors - list of current factors to multiply
			factors - main list of factors
	"""
	# while there's a valid multiplication to be done
	while (relevantProductFactors(currentFactors)):
		# search through all permutations
		perms = list(itertools.permutations(range(0,len(currentFactors)),2))
		for i in range(0,len(perms)):
			w, j = perms[i][0], perms[i][1]
			a, b = currentFactors[w],currentFactors[j]
			if canMultiply(a,b):
				prod = productFactor(a,b)
				print "Result:"
				prod.printFactor()
				# remove mutliplied factors from list
				if a in factors:
					factors.remove(a)
				if b in factors:
					factors.remove(b)
				# remove from current factors list
				currentFactors.remove(a)
				currentFactors.remove(b)
				# append to current factors
				currentFactors.append(prod)
				break
	return

def relevantProductFactors(currentFactors):
	"""
		IN:
			Current factors in product
		OUT:
			True - Is any combination of multiplication is valid
			False - o.w
	"""
	perms = list(itertools.permutations(range(0,len(currentFactors)),2))
	for p in perms:
		w, j = p[0], p[1]
		a, b = currentFactors[w],currentFactors[j]
		if canMultiply(a,b):
			return True
	return False

def varInFactors(factors, var):
	"""
	IN:
		Factors instances list
	OUT:
		list of all factors that this var is in their scope
	"""
	inScope = []
	for f in factors:
		if f.inFactor(var):
			inScope.append(f)
	return inScope


def canMultiply(factor1, factor2):
	"""
	IN:
		two factors instances
	OUT:
		true if can multiply them using function productFactor
		(checks all valid cases for function)
		false o.w
	"""
	# |factor1| >= |factor2| -must always hold
	if factor1.getSize() < factor2.getSize():
		return False
	# case 0
	if not factor1.isScalar() and factor2.isScalar():
		return True
	# case 1
	if sameFactor(factor1,factor2):
		return True
	# case 2
	if canJoinFactors(factor1,factor2):
		return True
	# case 3
	if contains(factor1.getVarlist(), factor2.getVarlist()):
		return True
	# case 4
	if commonRange(factor1.getVarlist(), factor2.getVarlist()):
		return True
	return False

def canJoinFactors(factor1, factor2):
	"""
	IN:
		two factors instances
	OUT:
		true if can join e.g ['A','B'] * ['B', 'C']
		false if cant e.g ['B','C'] * ['A','B']
		(order matters)
	"""
	aList = factor1.getVarlist()
	bList = factor2.getVarlist()

	if aList[len(aList)-1] != bList[0]:
		return False
	return True

def sameFactor(factor1, factor2):
	"""
	IN:
		two factors instances
	OUT:
		true - if they are identical e.g ['A','B'] * ['A','B']
		false - o.w
	"""
	if factor1.getSize() != factor2.getSize():
		return False
	aList = factor1.getVarlist()
	bList = factor2.getVarlist()
	for i in xrange(len(aList)):
		if aList[i] != bList[i]:
			return False
	return True

def nL(count=1):
	# prints new lines
	for i in range(0,count):
		print

def initFactors(toPrint=False):
	# procedure to init factors for our bayes network
	global Travel, Fraud, Fp, Ip, Oc, Crp

	travelProbs = [((True,),0.05),((False,),0.95)]
	Travel = Factor(['Trav'],travelProbs)
	
	fraudProbs = [((False,False),0.996),((False,True),0.99),((True,False),0.004), ((True, True), 0.01)]
	Fraud = Factor(['Fraud', 'Trav'], fraudProbs)
	
	fpProbs = [ ((False,False,False),0.99), ((False, False, True), 0.1), ((False,True,False),0.9), ((False,True,True),0.1), ((True,False,False),0.01), ((True,False,True),0.9), ((True,True,False),0.1), ((True,True,True),0.9)]
	Fp = Factor(['FP','Fraud','Trav'], fpProbs)
	
	ipProbs = [ ((False,False,False),0.999), ((False,False,True),0.99), ((False,True,False),0.989), ((False,True,True),0.98), ((True,False,False),0.001), ((True,False,True),0.01), ((True,True,False),0.011), ((True,True,True),0.02)]
	Ip = Factor(['IP','Fraud','OC'], ipProbs)
	
	ocProbs = [ ((True,),0.6), ((False,),0.4) ]
	Oc = Factor(['OC'], ocProbs)

	crpProbs = [ ((False,False),0.999), ((False,True),0.9), ((True,False),0.001), ((True,True),0.1) ]
	Crp = Factor(['CRP', 'OC'], crpProbs)

	if toPrint:
		Travel.printFactor()
		Fraud.printFactor()
		Fp.printFactor()
		Ip.printFactor()
		Oc.printFactor()
		Crp.printFactor()

def main():
	
	print "******************************************"
	print "		Q1"
	print "******************************************"
	print "(submitted also bayes net on paper)"
	nL()
	initFactors(True)
	nL()

	# order of elimination
	order = ['Trav','FP','Fraud','IP','OC','CRP']

	# question 2 (a)
	print "******************************************"
	print "		Q2-A"
	print "******************************************"
	initFactors()
	facListA = [Travel, Fraud]
	order = ['Trav','FP','Fraud','IP','OC','CRP']
	evidenceA = None
	inference(facListA,['Fraud'],order,evidenceA)
	print "Q2-A Answer: The probability of fraud purchase is 0.0043"
	nL()

	# question 2 (b)	
	print "******************************************"
	print "		Q2-B"
	print "******************************************"
	initFactors()
	facListB = [Travel, Fraud, Fp, Ip, Oc, Crp]
	evidenceB = [('FP',True),('CRP',True),('IP',False)]
	inference(facListB,['Fraud'],order,evidenceB)
	print "Q2-B Answer: the probability of fraud purchase now is 0.01498 - bigger than before"
	nL()

	# question 3
	print "******************************************"
	print "		Q3"
	print "******************************************"
	initFactors()
	facListC = [Travel, Fraud, Fp, Ip, Oc, Crp]
	evidenceC = [('FP',True),('CRP',True),('IP',False), ('Trav',True)]
	inference(facListC,['Fraud'],order,evidenceC)	
	print "Q3 Answer: The probability of fraud purchase is 0.00989 - lower than before (Q2-b)"
	nL()

	# question 4
	print "******************************************"
	print "		Q4"
	print "******************************************"
	initFactors()
	facListD = [Travel, Fraud, Fp, Ip, Oc, Crp]
	evidenceD = [('CRP',True),('IP',True)]
	inference(facListD,['Fraud'],order,evidenceD)
	print "Q4 Answer: I can only influence the probability by CRP variable"
	print "so I can buy a computer related item in the week before"
	print "if I wouldn't, the probability of fraud purchase is 0.01"
	nL()
	"""
	*** my tests here, not relevant ***

	# create an instance of a (random) factor sorted by alphabetical order
	print "Restrict factor:"
	facA = Factor(['B','A','C'])
	facA.printFactor()
	nL()
	# restrict factor
	resFac = restrict(facA,'B',True)
	resFac.printFactor()
	nL(2)
	
	resFac = restrict(resFac,'A',True)
	resFac.printFactor()
	nL(2)

	resFac = restrict(resFac,'C',True)
	resFac.printFactor()
	nL(2)

	# create 2 factors and compute product
	print "Factor product:"
	facB = Factor(['A','C'])
	facC = Factor(['C','D'])
	facB.printFactor()
	facC.printFactor()
	nL()
	
	prod = productFactor(facB,facC)
	prod.printFactor()
	nL(2)


	# sum out a variable out of factor
	print "Sums out variable:"
	facD = Factor(['A','B','C'])
	facD.printFactor()
	nL()
	facE = sumout(facD,'A')
	facE.printFactor()
	nL(2)

	
	# normalize a factor
	print "Normalize a factor:"
	facF = Factor(['A','B','C'])
	facF.printFactor()
	nL()
	facG = normalize(facF)
	facG.printFactor()	
	
	
	# var elimination
	facH = Factor(['A','B','C'])
	facG = Factor(['C','D'])
	facH.printFactor()
	facG.printFactor()
	
	evidence = [('B',True),('C',False)]
	facList = list()
	facList.append(facH)
	facList.append(facG)
	queryVar = ['A']
	order = ['B','C','D']

	inference(facList,['A'],order,evidence)
	"""

if __name__ == "__main__":
	main()
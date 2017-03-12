# Assignment 1: Language Modeling: trigram WORD model
# author: Brian Delhaisse
# Python 2.7.5

import random
import re
import unicodedata
from nltk.tokenize import *


def preprocessing(filename, sort, preProcessLevel):
	if sort=='file':
		myFile = open(filename,'r')
		text = myFile.read()
		myFile.close()
	elif sort=='url':
		from urllib import urlopen
		text = urlopen(filename).read()
	elif sort=='string':
		text = filename

	# preprocessing
	text = unicodedata.normalize('NFKD',unicode(text, 'utf-8')).encode('ascii','ignore')
	if preProcessLevel >= 2:
		text = text.lower()
		text = re.sub('[^a-z0-9]', ' ', text).split()
	elif preProcessLevel >= 1:
		text = re.sub('[^a-zA-Z0-9.,:;\']', ' ', text).split()
	else:
		text = word_tokenize(text)

	return text


def buildModel(filename, sort='file', preProcessLevel=0):

	text = preprocessing(filename,sort,preProcessLevel)
	N = len(text)

	# Building the language model
	dico = {}
	for i in xrange(2,N):
		t = (text[i-2],text[i-1])
		if t in dico:
			if text[i] in dico[t][0]:
				dico[t][0][text[i]][0] += 1.0
			else:
				dico[t][0][text[i]] = [1.0, 0.0]
			dico[t][2] += 1.0
		else:
			dico[t] = [{text[i]:[1.0, 0.0]}, 0.0, 1.0]

	# computing the probabilities and cumulative probabilities
	acc1 = 0.0
	for key1 in dico:
		acc2 = 0.0
		for key2 in dico[key1][0]:
			dico[key1][0][key2][0] /= dico[key1][2]
			acc2 += dico[key1][0][key2][0]
			dico[key1][0][key2][1] = acc2
		dico[key1][2] /= (N-2)
		acc1 += dico[key1][2]
		dico[key1][1] = acc1

	return dico


def saveModel(filename, dico):
	f = open(filename, 'w')
	for key1 in dico:
		for key2 in dico[key1][0]:
			f.write(key1[0]+"\t"+key1[1]+"\t"+key2+"\t"+str(dico[key1][0][key2][0])+"\n")
	f.close()


def generateOutput(dico, length):
	words = []

	def binarySearch(dico, value):
		first, last = 0, len(dico)-1
		keys = dico.keys()

		if value <= dico[keys[0]][1]:
			return keys[0]

		while first <= last:
			mid = first + (last-first)/2

			if dico[keys[mid-1]][1] < value <= dico[keys[mid]][1]:
				return keys[mid]
			elif value < dico[keys[mid]][1]:
				last = mid-1
			else:
				first = mid+1

	rand = random.random()
	index1 = binarySearch(dico, rand)
	words = [index1[0], index1[1]]

	for i in xrange(length-2):
		rand = random.random()
		index2 = binarySearch(dico[index1][0], rand)
		words.append(index2)
		index1 = (index1[1], index2)
		if index1 not in dico:
			rand = random.random()
			index1 = binarySearch(dico, rand)

	return ' '.join(words)
	#return ''.join(words)


def checkModel(filename, listOfModels, sort='file', preProcessLevel=0):
	text = preprocessing(filename, sort, preProcessLevel)
	N = len(text)

	perplexity = []
	for model in listOfModels:
		p = 1.0
		totMatch = 0
		for i in xrange(2,N):
			t = (text[i-2],text[i-1])
			if t in model:
				if text[i] in model[t][0]:
					p *= 1.0 / model[t][0][text[i]][0]**(1.0/N)
					totMatch += 1
				else:
					N1 = len(model[t][0])
					p *= N1**(1.0/N)
			else:
				N2 = len(model)
				p *= N2**(1.0/N)

		perplexity.append([p,totMatch])

	return perplexity




filename1 = "rawEng.txt"
filename2 = "rawFr.txt"
filename3 = "rawIt.txt"
testFileName = "testEng.txt"

dico1 = buildModel(filename1, preProcessLevel=2)
dico2 = buildModel(filename2, preProcessLevel=2)
dico3 = buildModel(filename3, preProcessLevel=2)

#saveModel("dataEng.txt", dico1)
#saveModel("dataFr.txt", dico2)
#saveModel("dataIt.txt", dico3)

print "\nEnglish:"
print generateOutput(dico1, 100)
print "\nFrench:"
print generateOutput(dico2, 100)
print "\nItalian:"
print generateOutput(dico3, 100)

perplexity = checkModel(testFileName, [dico1,dico2,dico3])
perplexity = [i[0]/(i[1]+1.0) for i in perplexity]
print "\nKind of Perplexity: ", perplexity
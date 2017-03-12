# Assignment 1: Language Modeling: trigram letter model
# author: Brian Delhaisse
# Python 2.7.5

import random
import re
import unicodedata


def preprocessing(filename):
	# reading file
	myFile = open(filename,'r')
	text = myFile.read()
	myFile.close()

	# preprocessing
	text = unicodedata.normalize('NFKD',unicode(text, 'utf-8')).encode('ascii','ignore')
	text = text.lower()
	text = re.sub('[^a-z]', ' ', text)
	text = ' '.join(text.split())

	l = []
	for c in text:
		n = ord(c)-97
		if n < 0:
			n += 91
		l.append(n)
	text = l
	
	return text


def buildModelLetter(filename):
	
	text = preprocessing(filename)
	N = len(text)
	V = 27

	# Building the language model
	# tab[0] will be used to compute the perplexity (smoothing), tab[1] will be used to generate text (cumulative prob.).
	tab = [[[[0.0 for k in xrange(28)] for j in xrange(27)] for i in xrange(27)] for d in xrange(2)]
	for i in xrange(2,N):
		tab[0][text[i-2]][text[i-1]][text[i]] += 1

	# computing the probabilities
	probL1 = [[0.0 for i in xrange(27)] for d in xrange(2)]
	acc1 = 0.0
	for i in xrange(27):
		totL1 = 0.0
		for j in xrange(27):
			tab[0][i][j][27] = sum(tab[0][i][j])
			totL1 += tab[0][i][j][27]
			acc2 = 0.0
			for k in xrange(27):
				if tab[0][i][j][k] != 0.0:
					acc2 += (tab[0][i][j][k] / tab[0][i][j][27])
					tab[1][i][j][k] = acc2
				tab[0][i][j][k] = (tab[0][i][j][k] + 1) / (tab[0][i][j][27] + V)
		probL1[0][i] = totL1/N
		if probL1[0][i] != 0.0:
			acc1 += probL1[0][i]
			probL1[1][i] = acc1
		acc2 = 0.0
		for j in xrange(27):
			if tab[0][i][j][27] != 0.0:
				tab[0][i][j][27] /= totL1
				acc2 += tab[0][i][j][27]
				tab[1][i][j][27] = acc2

	return [tab, probL1]


def checkModel(testFilename, listOfModels):
	text = preprocessing(testFilename)
	N = len(text)

	perplexity = []
	for model in listOfModels:
		p = ( 1.0 / model[1][0][text[0]] )**(1.0/N)
		p *= ( 1.0 / model[0][0][text[0]][text[1]][27] )**(1.0/N)
		for i in xrange(2,N):
			p *= ( 1.0 / model[0][0][text[i-2]][text[i-1]][text[i]] )**(1.0/N)

		perplexity.append(p)

	return perplexity


def saveModel(filename, model):
	f = open(filename, 'w')
	tab, probL1 = model[0], model[1]

	def fct(arg):
		if arg == 26:
			f.write("<space>\t")
		else:
			f.write(chr(arg+97)+"\t")

	for i in xrange(27):
		for j in xrange(27):
			acc = 0.0
			for k in xrange(27):
				fct(i)
				f.write(str(probL1[0][i])+"\t")
				fct(j)
				f.write(str(tab[0][i][j][27])+"\t")
				fct(k)
				if tab[1][i][j][k] != 0.0:
					f.write(str(tab[1][i][j][k] - acc)+"\n")
					acc = tab[1][i][j][k]
				else:
					f.write(str(0.0)+"\n")
	f.close()


def generateOutput(model, length):
	letters = []
	tab, probL1 = model[0], model[1]

	def app(index):
		if index < 26:
			letters.append(chr(index+97))
		else:
			letters.append(' ')

	def search(tab, value):
		for i in xrange(27):
			if value <= tab[i]:
				return i

	def give2Indexes(tab, probL1):
		rand = random.random()
		id1 = search(probL1[1], rand)
		rand = random.random()
		for j in xrange(27):
			if rand <= tab[1][id1][j][27]:
				id2 = j
		return id1, id2

	id1, id2 = give2Indexes(tab, probL1)
	app(id1)
	app(id2)

	for i in xrange(length-2):
		rand = random.random()
		id3 = search(tab[1][id1][id2], rand)
		app(id3)
		id1, id2 = id2, id3
		if tab[0][id1][id2][27] == 0.0:
			id1, id2 = give2Indexes(tab, probL1)

	return ''.join(letters)



filename1 = "rawEng.txt"
filename2 = "rawFr.txt"
filename3 = "rawIt.txt"
testFileName = "testEng.txt"
#testFileName = "testFr.txt"
saveFileName = "data"
model1 = buildModelLetter(filename1)
model2 = buildModelLetter(filename2)
model3 = buildModelLetter(filename3)
listOfModels = [model1, model2, model3]
for i in xrange(3):
	saveModel(saveFileName+str(i+1)+".txt", listOfModels[i])
	print generateOutput(listOfModels[i], 300)
	print "\n"
perplexity = checkModel(testFileName, listOfModels)
print "Perplexity: ", perplexity


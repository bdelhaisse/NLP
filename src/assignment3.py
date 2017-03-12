# Assignment 3: Word Sense Disambiguation
# author: Brian Delhaisse
# Python 2.7.5
# references: course

#import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords

# Preprocessing: remove punctuation, put the sentence in lower case, and remove the stop words from the sentence.
# @return a list of words
def preprocess_sentence(sentence):
	import string
	sentence = ''.join(word for word in sentence if word not in tuple(string.punctuation))
	sentence = sentence.lower()
	stop = stopwords.words('english')
	#from nltk.stem.porter import PorterStemmer
	#porter = PorterStemmer() #porter.stem(i)
	return [i for i in sentence.split() if i not in stop]


# Compute the SIMPLIFIED Lesk algorithm (as described in the book "Speech and Language Processing" 
#	by Daniel Jurafsky & James H. Martin, 2nd edition, chap 20, section 4.1)
# From the book: "In general, Simplified Lesk seems to work better than orginal Lesk" (chap20, section 4.1)
def simplified_lesk(word, sentence):
	senses = wn.synsets(word)
	best_sense = senses[0].definition() # The first member of the list is the primary (most frequent) sense. See documentation.
	max_overlap = 0
	context = set(sentence.split() if isinstance(sentence, str) else sentence) - set(word)

	# Compute the overlapping
	def compute_overlap(signature):
		val = 0
		for w in signature:
			if w in context: #O(1)
				val = val + 1
		return val

	for sense in senses:
		signature = sense.definition().split() # for definitions
		for example in sense.examples(): # for examples
			signature = signature + example.split()
		signature = set(signature)
		overlap = compute_overlap(signature)
		if overlap > max_overlap:
			max_overlap = overlap
			best_sense = sense.definition()

	return best_sense


# Compute the ORIGINAL Lesk algorithm
# "The original Lesk algorithm is slightly more indirect. Instead of comparing a target word's signature with the context words, 
# the target signature is compared with the signatures of each of the context words." 
# ("Speech and Language Processing" by Daniel Jurafsky & James H. Martin, 2nd edition, chap 20, section 4.1)
def original_lesk(sentence):
	sentence = preprocess_sentence(sentence)
	context = {w:{} for w in sentence}
	for w in sentence:
		for sense in wn.synsets(w):
			context[w][sense] = preprocess_sentence(sense.definition()) # for definition
			for example in sense.examples(): # for examples
				context[w][sense] = context[w][sense] + preprocess_sentence(example)
			context[w][sense] = set(context[w][sense])

	for word in sentence:
		senses = wn.synsets(word)
		max_overlap = 0
		best_sense = senses[0]
		dico = {sense:0 for sense in senses}
		for otherWord in sentence:
			if word != otherWord:
				for sense in senses:
					for w1 in context[word][sense]:
						for otherSense in context[otherWord].keys():
							if w1 in context[otherWord][otherSense]: #O(1)
								dico[sense] = dico[sense] + 1

		# finding the best sense
		for sense in senses:
			if dico[sense] > max_overlap:
				max_overlap = dico[sense]
				best_sense = sense

		# removing other senses
		for sense in senses:
			if sense != best_sense:
				context[word].pop(sense)

	# computing a dictionary 
	dico = {word: context[word].keys()[0].definition() for word in sentence}
	return dico

def print_senses(word):
	senses = wn.synsets(word)
	for sense in senses:
		print sense.definition()
		print sense.examples()

# Main code
sentence = "Time flies like an arrow."
sent = preprocess_sentence(sentence)
print 'SIMPLIFIED LESK: \n '
for word in sent:
	print 'for the word \'%s\':' % word
	#print print_senses(word)
	print 'the best sense is: %s \n' % simplified_lesk(word, sent)

print '========================================================'
print 'ORIGINAL LESK: \n '
dico = original_lesk(sentence)
for w in sent:
	print 'for the word \'%s\':' % w
	print 'the best sense is: %s \n' % dico[w]
# Assignment 2a: Practical Orientation - chart parser
# author: Brian Delhaisse
# Python 2.7.5
# references: http://www.nltk.org/book/ch08.html + course + wikipedia

import nltk

# List of sentences
listSent = ["I gave an apple to the teacher", "I gave the teacher a very heavy book", "I gave the policeman a flower",\
	"Mary thinks that I gave a policeman a flower", "I persuaded Harry to give the policeman a flower", \
	"John is eager to please", "John is easy to please", "This is the dog that chased the cat", \
	"This is the cat that the dog chased", "This is the cat that Mary said that the dog chased"]
# Supp: "This is easy", "This is very easy", "John is persuaded that Mary said that the dog chased the cat"

# Grammar in CNF (Chomsky Normal Form)
grammar = nltk.CFG.fromstring("""
	S -> NP VP
	NP -> D N | D ANP
	ANP -> AP N | Adj N
	AP -> Adv Adj
	VP -> V NP | V PP | V DOP | V SP | V NRP | V ParP | V VP | V AP | V Adj
	PP -> P NP
	DOP -> NP PP | NP NP
	SP -> Sub S
	NRP -> NP RP
	RP -> RPr VP | RPr S
	ParP -> NP ParVP | Adj ParVP | AP ParVP
	ParVP -> Par VP
	NP -> 'I' | 'This'
	RPr -> 'that'
	Sub -> 'that'
	NP -> 'Mary' | 'John' | 'Harry'
	D -> 'an' | 'a' | 'the'
	N -> 'apple' | 'teacher' | 'book' | 'policeman' | 'cat' | 'dog' | 'flower'
	VP -> 'gave' | 'give' | 'please' | 'is' | 'chased' | 'thinks' | 'said' | 'persuaded'
	V -> 'gave' | 'give' | 'please' | 'is' | 'chased' | 'thinks' | 'said' | 'persuaded'
	P -> 'to'
	Par -> 'to'
	Adj -> 'heavy' | 'easy' | 'eager'
	Adv -> 'very'
	""")

# Create a chart parser based on the CKY algorithm
# @return: table - the parse table
# @return: tree - the parse tree
def createParseTableAndTree(tokens, grammar, trace=False):
	# Useful variables
	N = len(tokens)
	table = [[None for i in xrange(N+1)] for j in xrange(N+1)] # This table will contain the lexical/phrasal categories
	dic = {} # this dictionary will contain as keys the right hand side (rhs), and as value the left hand side (lhs) of the grammar.
	for p in grammar.productions():
		rhs = p.rhs() if len(p.rhs())>1 else (p.rhs()[0], None)
		if rhs in dic: # Ex: A word could belong to multiple lexical categories
			dic[rhs].append(p.lhs())
		else:
			dic[rhs] = [p.lhs()]
	tree = {} # this dictionnary will contain the decisions we made.

	# fill the table
	for j in xrange(1,N+1): #[1,N], position going left to right.
		for i in xrange(j-1,-1,-1): #[j-1,0], position going down to top.
			if i==(j-1): # diagonal elements
				prod = dic[(tokens[i],None)]
				for p in prod:
					if ((p,None) in dic) and all(item not in prod for item in dic[(p,None)]):
						prod = prod + dic[(p,None)]
				table[i][j] = prod
			else: # non diagonal elements
				var = range(i+1,j) if (j-2) >= (i+1) else range(i+1,j-2,-1)
				for k in var: #[i+1,j-1], span.
					if (table[i][k] != None) and (table[k][j] != None):
						for elem1 in table[i][k]:
							for elem2 in table[k][j]:
								if (elem1, elem2) in dic: #add a category in a cell of the table
									if table[i][j] == None:
										table[i][j] = dic[(elem1, elem2)] #replace the value
									else:
										table[i][j] = table[i][j] + dic[(elem1, elem2)] #concatenate
									if trace:
										print "(table[%s][%s] table[%s][%s] table[%s][%s]) = (%s %3s %3s)" % \
										(i, j, i, k, k, j, dic[(elem1, elem2)][0], elem1, elem2)
									tree[(dic[(elem1, elem2)][0],i,j)] = [(elem1,i,k), (elem2,k,j)]
	
	# Construct the tree string, that is the tree in parentheses notation
	def constructTreeString(elem):
		if elem[1]==(elem[2]-1):
			if all(item != elem[0] for item in dic[(tokens[elem[1]],None)]):
				return "(%s (%s %s))" % (elem[0], dic[(tokens[elem[1]],None)][0], tokens[elem[1]])
			return "(%s %s)" % (elem[0], tokens[elem[1]])
		else:
			l = tree[elem]
			return "(%s %s %s)" % (elem[0], constructTreeString(l[0]), constructTreeString(l[1]))

	# Construct the tree
	if (nltk.grammar.Nonterminal("S"),0,N) in tree:
		treeString = constructTreeString((nltk.grammar.Nonterminal("S"),0,N))
		tree = nltk.Tree.fromstring(treeString)
	else:
		print 'Error: the sentence cannot be recognized by the grammar'

	return table, tree


# Display the grammar
def displayGrammar(grammar):
	print '\nGrammar:'
	print grammar

# Display the parse tree using the NLTK chart parser
def displayParseTreeNLTK(tokens, grammar):
	parser = nltk.ChartParser(grammar)
	trees = parser.parse(tokens)
	for elem in trees:
		print elem

# display the parse tree
def displayParseTree(tree, draw = False, filename=''):
	print '\nParse tree: '
	print tree
	if draw:
		tree.draw()
	if filename!='':
		cf = nltk.draw.util.CanvasFrame()
		tc = nltk.draw.TreeWidget(cf.canvas(),tree)
		cf.add_widget(tc,10,10) # (10,10) offsets
		cf.print_to_file(filename+'.ps')
		cf.destroy()

# display the parse table (taken from http://www.nltk.org/book/ch08.html and slightly modified)
def displayParseTable(table):
	print '\nChart Table: '
	print '    ' + ' '.join([("%-10d" % i) for i in range(1, len(table))]) 
	for i in range(len(table)-1):
		print "%d " % i,
		for j in range(1, len(table)):
			print "%-10s" % (table[i][j] or '.'), 
		print

def printParseTableLatex(table):
	print '\\begin{table}[H]'
	print '\centering'
	print '\\begin{tabular}{' + '|c'*len(table) + '|}'
	print '   \hline & ' + ' & '.join([("%d" % i) for i in range(1, len(table))]) + ' \\\\'
	for i in range(len(table)-1):
		print "   \hline %d" % i,
		for j in range(1, len(table)):
			print " & %s" % (table[i][j] or ''), 
		print '\\\\'
	print '   \hline'
	print '\\end{tabular}'
	print '\\end{table}'

# Main code
displayGrammar(grammar)
for i in xrange(len(listSent)):
	print '\n\n\n%s) Sentence: %s' % (i+1,listSent[i])
	sent = listSent[i].split()
	table, tree = createParseTableAndTree(sent, grammar, trace=False)
	displayParseTable(table)
##	printParseTableLatex(table)
##	displayParseTreeNLTK(sent, grammar) # Using nltk, which use the Earley algo
	displayParseTree(tree) 
##	displayParseTree(tree, draw=True)
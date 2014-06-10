# code dependencies
import kb_services
import parsing
import verbalization
import planner
# network toolkit
import networkx as nx
# regular expressions 
import re
# drawing
import networkx.drawing
import matplotlib.pyplot as plt


def diff(a, b):
        b = set(b)
        return [aa for aa in a if aa not in b]


#######################
# grounds every np from the sentence
def sentence_grounder(G, sentence):
	sentence = parsing.ontology_words_mapping(sentence)
	print "key words substitution: ", sentence
	words, ranked_tags = parsing.pos_tagger(G, sentence)	
	print "part-of-speech tags: ", ranked_tags[0]
	chunked_pos, chunked_words, noun_phrases = parsing.constituent_chunker(parsing.grammar_np_simple, words, ranked_tags[0])
	
	print "chunked pos: ", chunked_pos
	print "chunked words: ", chunked_words
	print "noun phrases: ", noun_phrases

	solved_nps = []
	solved = True
	for each in noun_phrases:
		names = noun_phrase_grounder(G, each[0], each[1]) 
		if names == []:
			solved = False
			print "noun phrase: ", each, " can not be grounded"
		solved_nps.append(names)
	print "solved noun phrases: ", solved_nps

	if solved: 
		sem_types = semantic_type_of_nps(G, chunked_pos, chunked_words, solved_nps)
		print "semantic types: ", sem_types
	else:
		print "SOMETHING WRONG! no object matched with the noun phrase"
		sem_types = []
	return chunked_pos, chunked_words, sem_types, solved_nps, solved

def noun_phrase_grounder(G, words, pos):	
	# case if it is a simple or complex noun phrase
	is_simple = parsing.parser_cyk(parsing.grammar_np_simple, pos)
	if is_simple:
		grounded_objs = solve_simple_np(G, words, pos)
	else:
		grounded_objs = solve_complex_np(G, words, pos)

	# get a quantifier three cases all, one or defined by a integer
	if grounded_objs != []:
		if 'existencial' in pos:
			return [grounded_objs[0]]
		elif 'universal' in pos:
			return grounded_objs
		elif 'number' in pos:
			if int(words[pos.index('number')]) < len(grounded_objs):
				return grounded_objs[0:int(words[pos.index('number')])]
			else:
				return grounded_objs
		elif 'idf_pro' in pos:
			return [grounded_objs[0]]
		else:
			return grounded_objs
	else:
		print 'NO OBJECT MATCHED THE DESCRIPTION!'
		return grounded_objs

def solve_simple_np(G, words, pos):
	nouns = []
	adjs = []
	vrbs = []
	objs = []
	for i in range(len(words)):
		if pos[i] == 'noun':
			nouns.append(words[i])
		elif pos[i] == 'adj':
			adjs.append(words[i])
		elif pos[i] == 'vrb':
			vrbs.append(words[i])
		elif pos[i] == 'idf_pro':
			nouns.append('stuff')
	print 'nouns: ', nouns, '   adjs: ', adjs, '   vrbs: ', vrbs
	# collect all objects of class
	if len(nouns) > 0:
		obj_candidates = kb_services.all_objects(G, nouns[0])
		#print 'candidate objects: ', obj_candidates
		# filter objects that has correct properties
		if len(adjs) > 0:
			for each_obj in obj_candidates:
				if kb_services.verify_satisfability_of_objclss(G, each_obj, adjs):
					objs.append(each_obj)
		# filter objects that are object of action verb
		elif len(vrbs) > 0:
			for each_obj in obj_candidates:
				obj_actions = kb_services.get_attribute(G, each_obj, 'is_object_of_action')
				if "is_object_of_action" in obj_actions and vrbs[0] in obj_actions["is_object_of_action"]:
					objs.append(each_obj)
					
		else:
			objs = obj_candidates[:]
	return objs





def semantic_type_of_nps(G, pos, words, nps):
	np_count = 0
	semantic_types = words[:]
	for i in range(0,len(words)):
		if re.match('NOUN_PHRASE_[0-9]+', words[i]):
			#print "lol found", nps[np_count][0]
			semantic_types[i] = kb_services.semantic_type(G, nps[np_count][0])
			np_count += 1
		else:
			semantic_types[i] = kb_services.semantic_type(G, words[i])
	return semantic_types



def test_solver(sentence):
	G = kb_services.load_semantic_network()
	pos, words, sem, nps, solved = sentence_grounder(G, sentence)	
	print pos, words, sem, nps, solved
	


def test_np_grounding(sentence):
	G = kb_services.load_semantic_network()

	sentence = parsing.ontology_words_mapping(sentence)
	print "key words substitution: ", sentence
	words, ranked_tags = parsing.pos_tagger(G, sentence)	
	print "part-of-speech tags: ", ranked_tags[0]
	chunked_pos, chunked_words, noun_phrases = parsing.constituent_chunker(parsing.grammar_np_simple, words, ranked_tags[0])
	
	print "chunked pos: ", chunked_pos
	print "chunked words: ", chunked_words
	print "noun phrases: ", noun_phrases
	print 'now solving nps::::::::::::'
	solved_nps = []
	solved = True
	for each in noun_phrases:
		print 'grounded objects! ', noun_phrase_grounder(G, each[0], each[1]) 
		


test_solver("bring valerie something to eat")


#test_solver()
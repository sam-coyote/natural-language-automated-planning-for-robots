# code dependencies
import kb_services
import parsing
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
# 1) mapping words to ontology vocabulary
# 2) sintactical analisys
# 3) solve syntactical well formed noun phrases
def sentence_grounder(G, sentence):
	sentence = parsing.ontology_words_mapping(sentence)
	print "key words substitution: ", sentence
	
	words, ranked_tags = parsing.pos_tagger(G, sentence)	
	print "part-of-speech tags: ", ranked_tags[0]
	
	np_interpretation = parsing.constituent_chunker(parsing.grammar_np_simple, words, ranked_tags[0])
	print "chunked pos: ", np_interpretation[0]
	print "chunked words: ", np_interpretation[1]
	print "noun phrases: ", np_interpretation[2]

	solved_nps = []
	solved = True
	for each in np_interpretation[2]:
		names = noun_phrase_grounder(G, each[0], each[1]) 
		if names == []:
			solved = False
			print "noun phrase: ", each, " can not be grounded"
		solved_nps.append(names)
	print "-----> solved noun phrases: ", solved_nps

	if solved: 
		# obtain all combinations using solved noun phrases
		# subtitutes solved noun phrases into the sentence
		words_np_solved = []
		i = 0
		for each_word in np_interpretation[1]:
			if re.match('NOUN_PHRASE_[0-9]+', each_word):
				words_np_solved.append(solved_nps[i])
				i += 1
			else:
				words_np_solved.append(each_word)
		#print "substituted solved nps: ", words_np_solved
		packed_words = []
		for each_word in words_np_solved:
			if not isinstance(each_word, list):
				packed_words.append([each_word])
			else:
				packed_words.append(each_word)

		#print "packed in lists:::: ", packed_words
		all_words = parsing.all_combinations(packed_words)
		print "-----> all combinations: ", all_words
		
		# up to here all direct grounded commands are contructed therefore
		# they can be further separated in NPs and PPs for verb pattern matching
		
		for each_utterance in all_words:
			pp_interpretation = parsing.pp_chunker(parsing.grammar_pp, each_utterance, np_interpretation[0], [])
			print "------------"
			print "chunked pos: ", pp_interpretation[0]
			print "chunked words: ", pp_interpretation[1]
			#print "noun phrases: ", pp_interpretation[2]
			print "prepositional phrases: ", pp_interpretation[3]
			print "------------"
			
		
		#sem_types = semantic_type_of_nps(G, np_interpretation[0], np_interpretation[1], solved_nps)
		#print "semantic types: ", sem_types
	else:
		print "SOMETHING WRONG! no object matched with the noun phrase"
		sem_types = []
	return np_interpretation[0], np_interpretation[1], solved


def verb_pattern_matching(G, pos, words):
	return False

# solve noun phrases
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




# pack information for interpretation
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



#test_solver("bring valerie something to eat")


#test_solver()
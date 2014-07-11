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

def intersection(a,b):
	b = set(b)
	return [aa for aa in a if aa in b]
# 
interpreted_verbs = [
	#
	# Assertions
	#
	# assertion object is attribute value
	# arity 6: 1 adv_class, 1 verb is, 1 "the", 1 attribute, 1 "of", 1 object 
	{"arity": 4,
	# objects to solved (find grounded reference)
	"solve": ["object", "attribute", "value"],
	# sintactical forms of the verb
	"action": ["is", "are"],
	# description of element actor: 
	#[]: no special keywords, [noun]: constituent, [person, robot]: sem type, [robot]: default 
	"object": [[], ["noun"], ["stuff", "person"], []],
	"attribute": [[], ["att"], ["attribute"], []],
	"value": [[], ["adj"], ["attribute"], []],
	"dependency": "( ASSERT O: object ATT: attribute VALUE: value )"
	},

	{"arity": 3,
	# objects to solved (find grounded reference)
	"solve": ["object",  "value"],
	# sintactical forms of the verb
	"action": ["is", "are"],
	# description of element actor: 
	#[]: no special keywords, [noun]: constituent, [person, robot]: sem type, [robot]: default 
	"object": [[], ["noun"], ["stuff", "person"], []],
	"value": [[], ["adj"], ["attribute"], []],
	"dependency": "( ASSERT O: -object- ATT: =kb_services.all_superclasses(G,'-value-')[0] VALUE: -value- )"
	},

	#
	# Questions
	#

	# question what is the attribute of object
	# arity 6: 1 adv_class, 1 verb is, 1 "the", 1 attribute, 1 "of", 1 object 
	{"arity": 6,
	# objects to solved (find grounded reference)
	"solve": ["adv_what", "attribute", "object"],
	# sintactical forms of the verb
	"action": ["is", "are"],
	# description of element actor: 
	#[]: no special keywords, [noun]: constituent, [person, robot]: sem type, [robot]: default 
	"attribute": [[], [], ["attribute"], []],
	#[to]: special keyword, [noun]: constituent, [place]: sem type, [exit]: default 
	"adv_what": [["what"], ["adv_class"], [], []],
	#[to]: special keyword, [noun]: constituent, [place]: sem type, [exit]: default 
	"object": [[], ["noun"], ["stuff"], []],
	"dependency": "( CONSULT adv_what O: object ATT: attribute )"
	},

	# what is att_value
	{"arity": 3, 
	"solve": ["adv_what", "attribute"],
	"action": ["is", "are"],
	"attribute": [[], ["adj"], ["attribute"], []],
	"adv_what": [["what", "who"], ["adv_class"], [], []],
	"dependency": "( CONSULT all_objects_with: VALUE: attribute )"
	},

	# what is attribute att_value
	{"arity": 4,
	"solve": ["adv_what", "attribute", "value"],
	"action": ["is", "are"],
	"value": [[], ["adj"], ["attribute"], []],
	"attribute": [[], ["att"], ["attribute"], []],
	"adv_what": [["what", "who"], ["adv_class"], [], []],
	"dependency": "( CONSULT all_objects_with: ATT: attribute VALUE: value )"
	},

	# what is attribute att_value
	{"arity": 3,
	"solve": ["adv_where", "object"],
	"action": ["is", "are"],
	"object": [[], ["noun"], ["stuff", "person"], []],
	"adv_where": [["where"], ["adv_loc"], [], []],
	"dependency": "( CONSULT location_of object: object )"
	},

	#
	# Commands
	#
	{"arity": 2,
	# bring a drink
	"action": ["align", "arrange", "orient"],
	"solve": ["object"],
	"object": [[], ["prep_phrase"], ["item", "person"], []],
	# (get ACTOR OBJECT_TO_ALIGN DESTINATION)
	"dependency": "( align justina -object- =kb_services.get_attribute(G,'-object-','in')['in'][0] )"
	},

	{"arity": 2,
	# bring a drink
	"action": ["bring", "fetch", "get"],
	"solve": ["object"],
	"object": [[], ["noun"], ["item"], []],
	# (get ACTOR OBJECT SOURCE DESTINATION)
	"dependency": "( get justina -object- =kb_services.get_attribute(G,'-object-','in')['in'][0] =kb_services.get_attribute(G,'justina','in')['in'][0] )"
	},

	{"arity": 3,
	# get a drink to sam / get me a coke
	"action": ["bring", "fetch", "get"],
	"solve": ["destination", "object"],
	"destination": [[], ["noun", "prep_phrase"], ["person"], []],
	"object": [[], ["noun"], ["item"], []],
	# (get ACTOR OBJECT SOURCE DESTINATION)
	"dependency": "( get justina -object- =kb_services.get_attribute(G,'-object-','in')['in'][0] =kb_services.get_attribute(G,'-destination-','in')['in'][0] )"
	},

	{"arity": 3,
	# get a drink to the livingroom
	"action": ["bring", "fetch", "get"],
	"solve": ["destination", "object"],
	"destination": [["to"], ["prep_phrase"], ["place"], []],
	"object": [[], ["noun"], ["item"], []],
	# (get ACTOR OBJECT SOURCE DESTINATION)
	"dependency": "( get justina -object- =kb_services.get_attribute(G,'-object-','in')['in'][0] -destination- )"
	},

	{"arity": 3,
	# get a drink from the livingroom
	"action": ["bring", "fetch", "get"],
	"solve": ["source", "object"],
	"source": [["from"], ["prep_phrase"], ["place"], []],
	"object": [[], ["noun"], ["item"], []],
	# (get ACTOR OBJECT SOURCE DESTINATION)
	"dependency": "( get justina -object- -source- =kb_services.get_attribute(G,'justina','in')['in'][0] )"
	},

	{"arity": 3,
	# get a drink to the livingroom
	"action": ["bring", "fetch", "get"],
	"solve": ["destination", "object"],
	"destination": [["to"], ["prep_phrase"], ["place"], []],
	"object": [[], ["noun"], ["item"], []],
	# (get ACTOR OBJECT SOURCE DESTINATION)
	"dependency": "( get justina -object- =kb_services.get_attribute(G,'-object-','in')['in'][0] -destination- )"
	},

	{"arity": 4,
	# get sam a drink from the kitchen
	"action": ["bring", "fetch", "get"],
	"solve": ["destination", "object", "source"],
	"destination": [[], ["noun"], ["person"], []],
	"object": [[], ["noun"], ["item"], []],
	"source": [["from"], ["prep_phrase"], ["place", "container", "item"], []],
	# (get ACTOR OBJECT SOURCE DESTINATION)
	"dependency": "( get justina -object- -source- =kb_services.get_attribute(G,'-destination-','in')['in'][0] )"
	},


	{"arity": 2,
	"action": ["go", "walk", "navigate"],
	"solve": ["destination"],
	"destination": [["to"], ["prep_phrase"], ["place"], []],
	# (go SOURCE DESTINATION)
	"dependency": "( go here -destination- )"
	},

	{"arity": 2,
	"action": ["go", "walk", "navigate"],
	"solve": ["destination"],
	"destination": [["to"], ["prep_phrase"], ["item", "person"], []],
	# (go SOURCE DESTINATION)
	"dependency": "( go here =kb_services.get_attribute(G,'-destination-','in')['in'][0] )"
	},


	{"arity": 3,
	"action": ["go", "walk", "navigate"],
	"solve": ["destination", "source"],
	"destination": [["to"], ["prep_phrase"], ["place"], []],
	"source": [["from"], ["prep_phrase"], ["place"], []],
	# (go SOURCE DESTINATION)
	"dependency": "( go -source- -destination- )"
	},

	{"arity": 3,
	"action": ["go", "walk", "navigate"],
	"solve": ["destination", "source"],
	"destination": [["to"], ["prep_phrase"], ["item", "person"], []],
	"source": [["from"], ["prep_phrase"], ["place"], []],
	# (go SOURCE DESTINATION)
	"dependency": "( go -source- =kb_services.get_attribute(G,'-destination-','in')['in'][0] )"
	},

	{"arity": 3,
	"action": ["go", "walk", "navigate"],
	"solve": ["destination", "source"],
	"destination": [["to"], ["prep_phrase"], ["place"], []],
	"source": [["from"], ["prep_phrase"], ["item", "person"], []],
	# (go SOURCE DESTINATION)
	"dependency": "( go =kb_services.get_attribute(G,'-source-','in')['in'][0] -destination- )"
	},

	{"arity": 3,
	"action": ["go", "walk", "navigate"],
	"solve": ["destination", "source"],
	"destination": [["to"], ["prep_phrase"], ["item", "person"], []],
	"source": [["from"], ["prep_phrase"], ["item", "person"], []],
	# (go SOURCE DESTINATION)
	"dependency": "( go =kb_services.get_attribute(G,'-source-','in')['in'][0] =kb_services.get_attribute(G,'-destination-','in')['in'][0] )"
	},

	{"arity": 2,
	"action": ["go", "walk", "navigate"],
	"solve": ["destination"],
	"destination": [["to"], ["prep_phrase"], ["item", "person"], []],
	# (go SOURCE DESTINATION)
	"dependency": "( go here =kb_services.get_attribute(G,'-destination-','in')['in'][0] )"
	},





	{"arity": 3,
	"action": ["give", "hand"],
	"solve": ["destination", "item"],
	"destination": [[], ["noun"], ["person"], []],
	"item": [[], ["noun"], ["item"], []],
	# (give ITEM PERSON LOCATION)
	"dependency": "( give -item- -destination- =kb_services.get_attribute(G,'-destination-','in')['in'][0] )"
	},

	{"arity": 4,
	"action": ["give", "hand"],
	"solve": ["destination", "item", "source"],
	"destination": [[], ["noun"], ["person"], []],
	"source": [["from"], ["prep_phrase"], ["place"], []],
	"item": [[], ["noun"], ["item"], []],
	# (give ITEM PERSON LOCATION)
	"dependency": "( give -item- -destination- -source- )"
	},





	{"arity": 2,
	"action": ["take", "grasp"],
	"solve": ["object"],
	"object": [[], ["noun"], ["item"], []],
	# (grasp OBJECT)
	"dependency": "( grasp -object- )"
	},


	#falta find/lookfor, move/put, point, leave

	{"arity": 3,
	"action": ["put", "puts", "move", "moves"],
	"solve": ["destination", "object"],
	"destination": [[], ["prep_phrase", "noun"], ["place", "person"], []],
	"object": [[], ["noun"], ["item"], []],
	"dependency": "( move A: robot O: -object- D: -destination- )"
	},


	
]


#######################
# match the fragmented grounded sentence to a conceptual dependency 
def generate_dependency(G, sentence_dict):
	used_objects = []
	solved_dependency = ''
	solved = False
	#print "--------->   recibe esto: ", sentence_dict
	# sentence_dict dict keys: words, constituents, objects, types
	for each_verb in interpreted_verbs:
		for each_action_paraphrasis in each_verb["action"]:
			if not solved and each_action_paraphrasis in sentence_dict["words"] and len(sentence_dict["words"]) == each_verb["arity"]:
				#print "ok! trying to interpret sentence using: ", each_verb
				solved_elements = {element: "" for element in each_verb["solve"]}
				# loading defaults
				for each in solved_elements:
					if each_verb[each][3] != []:
						solved_elements[each] = each_verb[each][3][0]
				# overwriting defaults if an element match
				for each_to_solve in each_verb["solve"]:
					#print "trying to solve :", each_to_solve
					# need to check 4 things:
					#print "contains the keywords: ", each_verb[each_to_solve][0]
					#print "is from constituent: ", each_verb[each_to_solve][1]
					#print "is semantic type: ", each_verb[each_to_solve][2]
					#print "default: ", each_verb[each_to_solve][3]
					for each_object in sentence_dict["objects"]:
						if each_object not in used_objects:
							inx = sentence_dict["objects"].index(each_object)
							#print "has the keywords: ", sentence_dict["words"][inx]
							#print "is from constituent: ", sentence_dict["constituents"][inx]
							#print "is semantic type: ", sentence_dict["types"][inx]
							#print "default: ", "naaat"
							condition_of_match = len(intersection(sentence_dict["words"][inx], each_verb[each_to_solve][0])) > 0 or each_verb[each_to_solve][0] == []
							condition_of_match = condition_of_match and (sentence_dict["constituents"][inx] in each_verb[each_to_solve][1] or each_verb[each_to_solve][1] == [])
							condition_of_match = condition_of_match and (len(intersection(sentence_dict["types"][inx], each_verb[each_to_solve][2])) > 0 or each_verb[each_to_solve][2] == [])
							if condition_of_match:
								print "-------> ", each_object, " can solve ", each_to_solve
								solved_elements[each_to_solve] = each_object
								used_objects.append(each_object)

				# checking if all elements match to something
				solved = True
				print "elements solved: ", solved_elements
				for each_element in solved_elements:
					if solved_elements[each_element] == "":
						solved = False
						used_objects = []
						print "matching verb pattern failed, will try another"

				if solved:
					# substituting solved objects to dependency
					solved_dependency = each_verb["dependency"]
					for each in solved_elements:
						solved_dependency = re.sub('-'+each+'-', solved_elements[each], solved_dependency)

					print "-----> planner primitive before evaluation of code: ", solved_dependency
					

					#print "evaluating expressions: "
					terms = solved_dependency.split(' ')
					#print "terms are: ", terms
					join_list = []
					for each in terms:
						if each[0] == "=":
							print "trying evaluation of: ", each[1:]
							join_list.append(eval(each[1:]))
						else:
							join_list.append(each)

					solved_dependency = " ".join(join_list)
					#print "solved_final_hiper_dependency: ", join_list

							
	if solved_dependency == '':
		return "sorry, did not match any verb interpretation..."
	else:
		return solved_dependency



# grounds every np from the sentence
# 1) mapping words to ontology vocabulary
# 2) sintactical analisys
# 3) solve syntactical well formed noun phrases
def sentence_grounder(G, sentence):
	sentence = parsing.ontology_words_mapping(sentence)
	#print "key words substitution: ", sentence
	
	words, ranked_tags = parsing.pos_tagger(G, sentence)	
	#print "part-of-speech tags: ", ranked_tags[0]
	
	np_interpretation = parsing.constituent_chunker(parsing.grammar_np_simple, words, ranked_tags[0])
	#print "chunked pos: ", np_interpretation[0]
	#print "chunked words: ", np_interpretation[1]
	#print "noun phrases: ", np_interpretation[2]

	# constituent level
	constituent_level = np_interpretation[1][:]

	solved_nps = []
	solved = True
	for each in np_interpretation[2]:
		names = noun_phrase_grounder(G, each[0], each[1]) 
		if names == []:
			solved = False
			#print "noun phrase: ", each, " can not be grounded"
		solved_nps.append(names)
	#print "-----> solved noun phrases: ", solved_nps

	if solved: 
		# obtain all combinations using solved noun phrases
		# subtitutes solved noun phrases into the sentence
		words_np_solved = []
		chunked_constituents = []
		i = 0
		for each_word in np_interpretation[1]:
			if re.match('NOUN_PHRASE_[0-9]+', each_word):
				words_np_solved.append(solved_nps[i])
				chunked_constituents.append(np_interpretation[2][0])
				i += 1
			else:
				words_np_solved.append(each_word)
				chunked_constituents.append(each_word)
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
		#print "-----> all combinations POS: ", np_interpretation[0]
		
		# up to here all direct grounded commands are contructed therefore
		# they can be further separated in NPs and PPs for verb pattern matching
		analized_sentences = []
		for each_utterance in all_words:
			pp_interpretation = parsing.pp_chunker(parsing.grammar_pp, each_utterance, np_interpretation[0], [])
			
			# pointer alias
			pos_tags_pp = pp_interpretation[0]
			words_pp = pp_interpretation[1]


			#print "------------"
			#print "constituent_level: ", pp_interpretation[0]
			#print "chunked words: ", pp_interpretation[1]
			#print "noun phrases: ", pp_interpretation[2]
			#print "prepositional phrases: ", pp_interpretation[3]

			object_level = []
			# solving prepositional phrases
			pp_names = []
			for each_pp in pp_interpretation[3]:
				pp_names.append(prepositional_phrase_grounder(G, each_pp[0], each_pp[1])[0]) 
				if pp_names == []:
					solved = False
					print "noun phrase: ", each, " can not be grounded"
				#solved_nps.append(names)
			#print "-----------PPPPPP", pp_names
			if solved: 
				# obtain all combinations using solved prep phrases
				# subtitutes solved prep phrases into the sentence
				i = 0
				for each_word in pp_interpretation[1]:
					if re.match('PREP_PHRASE_[0-9]+', each_word):
						object_level.append(pp_names[i])
						i += 1
					else:
						object_level.append(each_word)

			# semantic classes
			semantic_types = [kb_services.all_superclasses(G, each) for each in object_level]
			
			#print "----->  object_level: ", object_level
			#print "----->  constituent_level: ", pp_interpretation[0] 
			#print "----->  semantic types: ", semantic_types

			## cut
			# packing words into constituents
			i=0
			#print "original words:", words
			pp_chunked = parsing.pp_chunker(parsing.grammar_pp, each_utterance, np_interpretation[0], [])
			chunked_final_words = []
			#print "....", pp_chunked[1]
			for each_word in pp_chunked[1]:
					if re.match('PREP_PHRASE_[0-9]+', each_word):
						chunked_final_words.append(pp_chunked[3][i][0])
						i += 1
					else:
						chunked_final_words.append(each_word)
			#print "------------chunked pp final words", chunked_final_words
			np_chunked = parsing.constituent_chunker(parsing.grammar_np_simple, chunked_final_words, pp_chunked[0])
			chunked_final_words = []
			i=0
			for each_word in np_chunked[1]:
					if isinstance(each_word, str) and re.match('NOUN_PHRASE_[0-9]+', each_word):
						chunked_final_words.append(np_chunked[2][i][0])
						i += 1
					else:
						chunked_final_words.append(each_word)
			
			constituent_level = np_chunked[0][:]


			## cut
			print "sentence ", sentence, " features:"
			print "--> ", chunked_final_words
			print "--> ", constituent_level
			print "--> ", object_level
			print "--> ", semantic_types
			analized_sentences.append({"words":chunked_final_words, "constituents": constituent_level, "objects": object_level, "types":semantic_types})
		return analized_sentences
	else:
		print "SOMETHING WRONG! no object matched with the noun phrase"
		sem_types = []
		return []


# solve noun phrases
def noun_phrase_grounder(G, words, pos):	
	# case if it is a simple or complex noun phrase
	is_simple = parsing.parser_cyk(parsing.grammar_np_simple, pos)
	if is_simple:
		#print "solving simple noun phrase..."
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


# solve noun phrases
def prepositional_phrase_grounder(G, words, pos):	
	if len(pos) == 2 and pos[1] == "noun":
		return [words[1]]
	else:
		return []
		

def solve_simple_np(G, words, pos):
	print "solving np: ", words
	nouns = []
	adjs = []
	atts = []
	vrbs = []
	objs = []
	for i in range(len(words)):
		if pos[i] == 'noun':
			if  len(nouns) == 0:
				nouns.append(words[i])
			else:
				adjs.append(words[i])
		elif pos[i] == 'adj':
			adjs.append(words[i])
		elif pos[i] == 'att' or pos[i] == 'prep_loc':
			atts.append(words[i])
		elif pos[i] == 'vrb':
			vrbs.append(words[i])
		elif pos[i] == 'idf_pro':
			nouns.append('stuff')
	print 'nouns: ', nouns, '   adjs: ', adjs, '   vrbs: ', vrbs, '   atts: ', atts
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
	print "solved np:", objs
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
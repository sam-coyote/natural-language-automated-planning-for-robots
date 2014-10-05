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
	if isinstance(a, str):
		a = [a]
	a = set(a)
	return [bb for bb in b if bb in a]
# 
meaning_mapping_patterns = [
	#
	# Assertions
	#

# verb give in present
	{
	
	# parameters to be solved 
	"params": ["what_action", "who", "what_object", "to_whom"],
	
	# [[]:keywords, []:constituent, []:sem type, []: default
	"what_action": [["give", "gives"], ["vrb"], [], []],
	"who": [[], ["noun"], ["person"], []],
	"what_object": [[], ["noun"], ["item"], []],
	"to_whom": [["to"], ["prep_phrase"], ["person", "robot"], []],

	"conceptual_dependency": '(ATRANS TIME: present RELATION:possesion OBJECT: -what_object- FROM: -who- TO: -to_whom-)',
	"verbal_confirmation": '-what_object- is now with -to_whom- right?',
	"planner_confirmed": '(action SAY message "ok, got it" =kb_services.add_edges_from_list([["-object-","owned_by","-to_whom-"]],"../ontologies/context_knowledge.txt" 0 0)',
	"planner_not_confirmed": '(action SAY message "ok, please try to rephrase" 0 0)'
	},







	# recieve
	{
	# parameters to be solved 
	"params": ["what_action", "who", "what_object", "from_whom"],
	
	# [[]:keywords, []:constituent, []:sem type, []: default
	"what_action": [["recieve", "recieves"], ["vrb"], [], []],
	"who": [[], ["noun"], ["person", "robot"], []],
	"what_object": [[], ["noun"], ["item"], []],
	"from_whom": [["from"], ["prep_phrase"], ["person"], []],

	"conceptual_dependency": '(ATRANS TIME: present RELATION:possesion OBJECT: -what_object- FROM: -from_whom- TO: -who-)',
	"verbal_confirmation": '-what_object- is now with -who- right?',
	"planner_confirmed": '(action SAY message "ok, got it" =kb_services.add_edges_from_list([["-object-","owned_by","-who-"]],"../ontologies/context_knowledge.txt" 0 0)',
	"planner_not_confirmed": '(action SAY message "ok, please try to rephrase" 0 0)'
	}
	
]


#######################
# match the fragmented grounded sentence to a conceptual dependency 
def generate_dependency(G, sentence_dict):
	used_objects = []
	solved_dependency = ''
	solved = False
	# recibe un diccionario con campos "constituents", "objects", "types", "words", 
	#la primeras dos son listas de strings y las otras son lista de listas

	print "7::       ------------------------------------"
	print "assigning a meaning to the sentence"

	# list of interpretations of each meaning pattern
	# 
	print "WTF... ", len(meaning_mapping_patterns)
	interpretations_list = []
	id_pattern = 0
	for each_pattern in meaning_mapping_patterns:
		# init template interpretation
		id_pattern =+ 1
		matched_elements = [[each, ""] for each in each_pattern["params"]]
		#print "hey! elementos a machear: ", matched_elements
		current_interpretation = {"id_pattern": id_pattern, "rank":0.0, "matched_elements":matched_elements, "conceptual_dependency": each_pattern["conceptual_dependency"], "verbal_confirmation": each_pattern["verbal_confirmation"], "planner_confirmed": each_pattern["planner_confirmed"], "planner_not_confirmed": each_pattern["planner_not_confirmed"]}
		used_params = []
		for each_param in each_pattern["params"]:
			params_matched = []
			# try fetch an element from sentence metadata to match a parameter
			for object_index in range(0, len(sentence_dict["objects"])):
				current_words = sentence_dict["words"][object_index]
				current_constituent = sentence_dict["constituents"][object_index]
				current_types = sentence_dict["types"][object_index]
				current_object = sentence_dict["objects"][object_index]
				#print "trying to match ", current_object, " with ", each_param
				# verifying for each_param
				if each_param not in used_params:
					#check words
					veri_words = len(intersection(current_words, each_pattern[each_param][0])) > 0 or each_pattern[each_param][0] == []
					#print 'palabras clave: ', veri_words
					#check constituyente
					veri_const = current_constituent in each_pattern[each_param][1] or each_pattern[each_param][1] == []
					#print 'contituyente: ', veri_const
					#check semantic type
					veri_type = len(intersection(current_types, each_pattern[each_param][2])) > 0 or each_pattern[each_param][2] == []
					#print 'tipos semanticos: ', veri_type
					
					if veri_type and veri_const and veri_words:
						for each_element in current_interpretation["matched_elements"]:
							if each_element[0] == each_param:
								each_element[1] = current_object
								used_params.append(each_param)
								current_interpretation["rank"] +=  1.0/len(current_interpretation["matched_elements"])
		interpretations_list.append(current_interpretation)

	print "Total of interpretations: ", len(interpretations_list)

	ranked_interpretations = sorted(interpretations_list, key=lambda k: k["rank"], reverse=True)

	for each_inter in ranked_interpretations:
		print "matched: ", each_inter["matched_elements"]
		print "rank: ", each_inter["rank"]
		print "____"















# grounds every np from the sentence
# 1) mapping words to ontology vocabulary
# 2) sintactical analisys
# 3) solve syntactical well formed noun phrases
def sentence_grounder(G, sentence):
	sentence = parsing.ontology_words_mapping(sentence)
	print "1::       ------------------------------------"
	print "key words substitution: ", sentence
	
	words, ranked_tags = parsing.pos_tagger(G, sentence)	
	print "2::       ------------------------------------"
	print "part-of-speech tags: ", ranked_tags[0]
	
	np_interpretation = parsing.constituent_chunker(parsing.grammar_np_simple, words, ranked_tags[0])
	print "3::       ------------------------------------"
	print "noun phrases segmentation"
	print "chunked pos: ", np_interpretation[0]
	print "chunked words: ", np_interpretation[1]
	print "noun phrases: ", np_interpretation[2]

	


	# constituent level
	constituent_level = np_interpretation[1][:]

	solved_nps = []
	solved = True
	for each in np_interpretation[2]:
		names = noun_phrase_grounder(G, each[0], each[1]) 
		if names == []:
			solved = False
			print "noun phrase: ", each, " can not be grounded"
		solved_nps.append(names)
	
	print "4::       ------------------------------------"
	print "grounded noun phrases: ", solved_nps

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

		print "5::       ------------------------------------"
		print "Separated sentences: ", all_words
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
					print "prepositional phrase: ", each, " can not be grounded"
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

			print "6::       ------------------------------------"
			print "sentence: ", sentence, " features the metadata:"
			print "words: ", chunked_final_words
			print "constituents: ", constituent_level
			print "objects: ", object_level
			print "types: ", semantic_types


			analized_sentences.append({"words":chunked_final_words, "constituents": constituent_level, "objects": object_level, "types":semantic_types})
		

		# return a list of dicionaries that
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


# generate message from dictionary
def generate_nl_response_from_dict(dictio):
	response = ""
	if dictio == {}:
		response = "not information about that, sorry"
	else:
		for each in dictio:
			print "HEY ", each, "  ", dictio[each]
			response +=" is " + each + " " + " and ".join(dictio[each])
	return response

def generate_nl_response_from_list(ls):
	response = ""
	if ls == []:
		response = "not any known object, sorry"
	else:
		if len(ls) == 1:
			response = ls.pop() + " is "
		else:
			for i in range(0, len(ls) - 1):
				response += ls.pop() + ", "
			response += "and " + ls.pop() + " are "
	return response
#test_solver("bring valerie something to eat")

print generate_nl_response_from_list([])
#test_solver()
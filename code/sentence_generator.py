import random

import kb
import parsing
import interpretation
import re


def generate_np(G):
	graph, quantifiers = kb.verify_node(G, ['*'], ['tag'], ['universal', 'existencial'])
	quantifiers = kb.list_diff(quantifiers, ['universal', 'existencial'])
	#print "quantifiers: ", quantifiers
	
	graph, determiners = kb.verify_node(G, ['*'], ['tag'], ['det'])
	determiners = kb.list_diff(determiners, ['det'])
	#print "determiners: ", determiners

	graph, adjetives = kb.inherited_objects_of_class(G, "attribute")
	adjetives = kb.list_diff(adjetives, ['attribute', 'location'])
	#print "adjetives: ", adjetives

	graph, place_preposition = kb.inherited_objects_of_class(G, "location")
	place_preposition = kb.list_diff(place_preposition, ['location'])
	#print "adjetives: ", adjetives
	adjetives = kb.list_diff(adjetives, place_preposition)

	graph, nouns = kb.inherited_subclasses_of_class(G, "stuff")
	nouns = kb.list_diff(nouns, ['stuff'])
	#print "nouns: ", nouns

	graph, places = kb.inherited_subclasses_of_class(G, "place")
	place = kb.list_diff(nouns, ['place'])
	#print "nouns: ", nouns

	graph, attributes = kb.inherited_subclasses_only_of_class(G, "attribute")
	attributes = kb.list_diff(attributes, ['attribute', 'is_kind_of', 'is_object_of', 'location'])
	#print "attributes: ", attributes

	include_quantifier = random.randint(0, 100) > 66
	include_determiner = (not include_quantifier) and random.randint(0, 100) > 66
	include_first_adjetive = random.randint(0, 100) > 50 
	include_second_adjetive = include_first_adjetive and random.randint(0, 100) > 50 
	include_complement = random.randint(0,100) > 50
	include_place = random.randint(0,100) > 50
	include_complement_attribute = include_complement and random.randint(0,100) > 50
	np = ''
	if include_quantifier:
		np += quantifiers[random.randint(0, len(quantifiers)-1)] + ' '
	
	if include_determiner:
		np += determiners[random.randint(0, len(determiners)-1)] + ' '
	
	if include_first_adjetive:
		np += adjetives[random.randint(0, len(adjetives)-1)] + ' '
	
	if include_second_adjetive:
		np += adjetives[random.randint(0, len(adjetives)-1)] + ' '
	
	np += nouns[random.randint(0, len(nouns)-1)]

	if include_complement:
		np += ' that is '
		if include_place:
			np += place_preposition[random.randint(0, len(place_preposition)-1)] + ' the '
			np += places[random.randint(0, len(places)-1)]
		else:
			adj = []
			attr = ''
			while len(adj) == 0 or attr == 'location':
				attr = attributes[random.randint(0, len(attributes)-1)]
				graph, adj = kb.inherited_objects_of_class(G, attr)
				adj = kb.list_diff(adj, [attr])	
			if include_complement_attribute:
				np += attr + ' '
			np += adj[random.randint(0, len(adj)-1)]
	np = re.sub('_', ' ', np)
	return np

def generate_statement(G):
	type_of_statement = random.randint(0, 1)
	
	if type_of_statement == 0:
		# statement of location
		
		graph, place_preposition = kb.inherited_objects_of_class(G, "location")
		place_preposition = kb.list_diff(place_preposition, ['location'])
		np1 = generate_np(G)
		np2 = generate_np(G)
		location_relation = place_preposition[random.randint(0, len(place_preposition)-1)]
		statement = np1 + ' is ' + location_relation + ' ' + np2
		
	elif type_of_statement == 1:
		#statement of aditional attribute
		graph, attributes = kb.inherited_subclasses_only_of_class(G, "attribute")
		attributes = kb.list_diff(attributes, ['attribute', 'is_kind_of', 'is_object_of', 'location'])
		include_complement_attribute = random.randint(0,100) > 50
		adj = []
		attr = ''
		statement = generate_np(G) + ' is '
		while len(adj) == 0 or attr == 'location':
			attr = attributes[random.randint(0, len(attributes)-1)]
			graph, adj = kb.inherited_objects_of_class(G, attr)
			adj = kb.list_diff(adj, [attr])	
		if include_complement_attribute:
			statement += attr + ' '
		statement += adj[random.randint(0, len(adj)-1)]
	else:
		statement = 'o.O'
	return statement

def generate_question(G):
	type_of_question = random.randint(0, 2)
	
	# question of location
	if type_of_question == 0:
		np1 = generate_np(G)
		question = 'where is ' + np1 +'?'

	# question the value of an attribute
	elif type_of_question == 1:
		np1 = generate_np(G)
		graph, attributes = kb.inherited_subclasses_only_of_class(G, "attribute")
		attr = 'attribute'
		while attr =='attribute' or attr == 'is_kind_of' or attr == 'is_object_of' or attr == 'location':
			attr = attributes[random.randint(0, len(attributes)-1)]	
		question = 'what is the ' + attr + ' of ' + np1 + '?'
	
	# verification of statement
	elif type_of_question == 2:
		np1 = generate_np(G)
		adj = []
		graph, attributes = kb.inherited_subclasses_only_of_class(G, "attribute")
		while len(adj) == 0:
			attr = attributes[random.randint(0, len(attributes)-1)]
			graph, adj = kb.inherited_objects_of_class(G, attr)
			adj = kb.list_diff(adj, [attr])
		adjetive = adj[random.randint(0, len(adj)-1)]
		question = 'is ' + np1 + ' ' + attr + ' ' + adjetive + '?'

	return question

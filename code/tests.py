# code dependencies
import kb_services
import parsing
import interpretation
import planner_bridge
# network toolkit
import networkx as nx
# regular expressions 
import re
# drawing
import networkx.drawing
import matplotlib.pyplot as plt


bateria_ejemplos = [
"place green pyramid on top of red brick"
]



G = kb_services.load_semantic_network()

for each_example in bateria_ejemplos:
	analized_sentences = interpretation.sentence_grounder(G, each_example)	

	commands = []
	for each_caracterized_sentence in analized_sentences:

		print "sentence ready to be matched::       ------------------------------------"
		print "generatiing meaning expressions from ", each_caracterized_sentence["objects"]
		commands.append(interpretation.generate_dependency(G, each_caracterized_sentence))

#	print "commands to planner..."	
#	for each in commands:
#		print "sent to planner: ", each
#		print "planner response:"
#		planner_bridge.launch_planner(each)
		
	
# knowledge basesolved_elements[each_element]

# code dependencies
import kb_services
import parsing
import interpretation
# network toolkit
import networkx as nx
# regular expressions 
import re
# drawing
import networkx.drawing
import matplotlib.pyplot as plt

G = kb_services.load_semantic_network()
sentence = "align to table 1"



analized_sentences = interpretation.sentence_grounder(G, sentence)	
#print "inicio:::::::", analized_sentences
commands = []
for each_caracterized_sentence in analized_sentences:
	commands.append(interpretation.generate_dependency(G, each_caracterized_sentence))
#print eval("kb_services.get_attribute(G, 'sam', 'in')")['in']
print "commands to planner..."	
for each in commands:
	print each
	
# knowledge basesolved_elements[each_element]

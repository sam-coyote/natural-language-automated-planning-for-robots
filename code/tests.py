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
sentence = "move a beer in kitchen_table to the table in bedroom 2"

# high-level, system-level tests



# medium-level, feature-level tests



# low-level tests
analized_sentences = interpretation.sentence_grounder(G, sentence)	
#print "inicio:::::::", analized_sentences
commands = []
for each_caracterized_sentence in analized_sentences:
	commands.append(interpretation.generate_dependency(G, each_caracterized_sentence))
#print eval("kb_services.get_attribute(G, 'sam', 'in')")['in']
print "commands to planner or so..."	
for each in commands:
	print each
	
# knowledge base

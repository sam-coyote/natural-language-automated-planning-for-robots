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
sentence = "bring me all beers from the fridge"

# high-level, system-level tests



# medium-level, feature-level tests



# low-level tests
pos, words, solved = interpretation.sentence_grounder(G, sentence)	
#print pos, words, sem, nps, solved
# knowledge base
#print 'get all attributes and values: ', kb_services.get_attribute(G, 'sam', 'shape')

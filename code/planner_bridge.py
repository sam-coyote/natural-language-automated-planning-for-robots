import clips
import kb_services
# network toolkit
import networkx as nx
# regular expressions 
import re
# drawing
import networkx.drawing
import matplotlib.pyplot as plt





# carga todo el conocimienoto implicito y explicito a partir de una ontologia en G
def load_facts_file_to_clips():
	G = kb_services.load_semantic_network()
	# get all nouns
	nouns = kb_services.all_subclasses(G, 'stuff') + kb_services.all_objects(G, 'stuff')
	facts_to_load = []
	for each_noun in nouns:
		att_dict = kb_services.get_attribute(G, each_noun, 'attribute')
		#print att_dict
		for each_attribute in att_dict:
			if each_attribute == 'nop':
				facts_to_load.append("(fact " + each_noun + " " + each_attribute + " " + att_dict[each_attribute][0] + ")")

			else:
				for each_value in att_dict[each_attribute]:
					#print "(fact " + each_noun + " " + each_attribute + " " + each_value + ")"
					facts_to_load.append("(fact " + each_noun + " " + each_attribute + " " + each_value + ")")

	for each_fact in facts_to_load:
		fi = clips.Assert(each_fact)
	fi = clips.Assert("(id_count 1)")

def load_expert_shell():
	clips.BatchStar("robot_planner.clp")
	clips.Reset()




def execute():
	print "loaded:"
	#clips.PrintFacts()
	clips.PrintRules()
	clips.DebugConfig.WatchAll()
	clips.Run()
	t = clips.TraceStream.Read()
	s = clips.StdoutStream.Read()

	
	

	
	#print "-------------------------"
	#print "ACTIVATION TRACE"
	#print t
	
	print "-------------------------"
	print "PLANNING OUTPUT"
	print s

	 


def launch_planner(com):
	load_expert_shell()
	load_facts_file_to_clips()
	fi = clips.Assert(com)
	execute()

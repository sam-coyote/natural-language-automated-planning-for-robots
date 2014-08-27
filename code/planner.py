import clips
import kb
# network toolkit
import networkx as nx
# regular expressions 
import re
# drawing
import networkx.drawing
import matplotlib.pyplot as plt

initial_facts =[
	"(fact robot status base ok)",
	"(fact robot status vision ok)",
	"(fact robot status grasp ok)",
	"(id_count 1)"]


def load_facts_file_to_clips(file_name):
	file = open(file_name, 'r')
	relations = []
	lines = file.readlines()
	for line in lines:
		if re.match('\([\?\w]+\s+\w+\s+\w+\)\s+', line):
			relation = re.split('[^a-zA-Z0-9\?_]+', line)[1:4]
			relations.append(relation)
			#print relation
	file.close()

	for each in relations:
		facto = "(fact " + each[0] + " " + each[1] + " " + each[2] + ")"
		#print "asserted fact: ", facto
		fi = clips.Assert(facto)
		

def load_initial_facts(command_fact):
	fi = clips.Assert(command_fact)
	for each in initial_facts:
		fi = clips.Assert(each)

def load_expert_shell():
	clips.BatchStar("basic_planner.clp")
	clips.Reset()
	
def execute():
	#clips.PrintFacts()
	#clips.PrintRules()
	clips.Run()
	s = clips.StdoutStream.Read()
	#clips.PrintFacts()
	print s



def catch_command(G, CD_command):
	CD_command = clean_cd_dict(CD_command)
	print_cd_dict(CD_command)

	if CD_command["type_attribute"] == ['fetch'] and CD_command["actor"] == ['self']:
		plan_fetch(G, CD_command)
	
	elif CD_command["type_attribute"] == ['take'] and CD_command["actor"] == ['self']:
		plan_take(G, CD_command)

	elif CD_command["type_attribute"] == ['move_align'] and CD_command["actor"] == ['self']:
		plan_align(G, CD_command)

	elif CD_command["type_attribute"] == ['tell'] and CD_command["actor"] == ['self']:
		plan_tell(G, CD_command)



def plan_fetch(G, cd_dictionary):
	print "launching planner!!!"
		
	# adding room to get the object (se puede usar una funcion en vez de repetir codigo)
	room = "unknown"
	for each in cd_dictionary["from"]:
		if kb.is_type(G, "room", each):
			room = each
	
	obj_align = "unknown"
	for each in cd_dictionary["from"]:
		if kb.is_type(G, "person", each) or kb.is_type(G, "container", each) or kb.is_type(G, "surface", each):
			obj_align = each

	# adding places to deliver
	room_del = "unknown"
	for each in cd_dictionary["to"]:
		if kb.is_type(G, "room", each):
			room_del = each
	
	obj_align_del = "unknown"
	for each in cd_dictionary["to"]:
		if kb.is_type(G, "person", each) or kb.is_type(G, "container", each) or kb.is_type(G, "surface", each):
			obj_align_del = each

	# adding up
	if cd_dictionary["actor"] == ["self"]:
		command_fact = "(request 0 fetch " + cd_dictionary["object"][0] + " " + room + " " + obj_align + " " + room_del + " " + obj_align_del + " 1)" 
		print "to planner! ", command_fact
		lauch_planner(command_fact)
	else:
		print "to verbalizer: Sentence not a robot command"
#test_symbolic_planner()


def plan_take(G, cd_dictionary):
	print "launching planner!!!"
		
	# adding room to get the object (se puede usar una funcion en vez de repetir codigo)
	room = "unknown"
	for each in cd_dictionary["from"]:
		if kb.is_type(G, "room", each):
			room = each
	
	obj_align = "unknown"
	for each in cd_dictionary["from"]:
		if kb.is_type(G, "person", each) or kb.is_type(G, "container", each) or kb.is_type(G, "surface", each):
			obj_align = each

	# adding up
	if cd_dictionary["actor"] == ["self"]:
		command_fact = "(request 0 take " + cd_dictionary["object"][0] + " " + room + " " + obj_align + " 1)" 
		print "to planner! ", command_fact
		lauch_planner(command_fact)
	else:
		print "to verbalizer: Sentence not a robot command"
#test_symbolic_planner()

def plan_align(G, cd_dictionary):
	print "launching planner!!!"
		
	# adding room to get the object (se puede usar una funcion en vez de repetir codigo)
	if kb.is_type(G, "room", cd_dictionary["object"]):
		if cd_dictionary["actor"] == ["self"]:
			command_fact = "(request 0 move_to_room " + cd_dictionary["object"][0] + " 1)" 
			print "to planner! ", command_fact
			lauch_planner(command_fact)
		else:
			print "to verbalizer: Sentence not a robot command"
	else:
		room = "unknown"
		for each in cd_dictionary["from"]:
			if kb.is_type(G, "room", each):
				room = each

		# adding up
		if cd_dictionary["actor"] == ["self"]:
			command_fact = "(request 0 goto " +  room + " " + cd_dictionary["object"][0] + " 1)" 
			print "to planner! ", command_fact
			lauch_planner(command_fact)
		else:
			print "to verbalizer: Sentence not a robot command"

def plan_tell(G, cd_dictionary):
	print "launching planner!!!"
		
	# adding room to get the object (se puede usar una funcion en vez de repetir codigo)
	room = "unknown"
	for each in cd_dictionary["from"]:
		if kb.is_type(G, "room", each):
			room = each
	
	message = cd_dictionary["obj_attribute"][0]
	# adding up
	if cd_dictionary["actor"] == ["self"]:
		command_fact = "(request 0 tell " + cd_dictionary["object"][0] + " " + room + " " + message + " 1)" 
		print "to planner! ", command_fact
		lauch_planner(command_fact)
	else:
		print "to verbalizer: Sentence not a robot command"

def lauch_planner(command_fact):
	load_expert_shell()
	load_initial_facts(command_fact)
	load_facts_file_to_clips("background_knowledge.txt")
	load_facts_file_to_clips("context_knowledge.txt")
	execute()


def clean_cd_dict(cd_dictionary):
	cd_dictionary["type"] = list(set(cd_dictionary["type"]))
	cd_dictionary["type_attribute"] = list(set(cd_dictionary["type_attribute"]))
	cd_dictionary["actor"] = list(set(cd_dictionary["actor"]))
	cd_dictionary["object"] = list(set(cd_dictionary["object"]))
	cd_dictionary["obj_attribute"] = list(set(cd_dictionary["obj_attribute"]))
	cd_dictionary["from"] = list(set(cd_dictionary["from"]))
	cd_dictionary["to"] = list(set(cd_dictionary["to"]))
	return cd_dictionary


def print_cd_dict(cd_dictionary):
	
	print "#############################################"
	if cd_dictionary["type"] != []:
		print "TYPE OF DEPENDENCY: ", cd_dictionary["type"]
	if cd_dictionary["type_attribute"] != []:
		print "ATTRIBUTE OF DEPENDENCY: ", cd_dictionary["type_attribute"]
	if cd_dictionary["actor"] != []:
		print "ACTOR: ", cd_dictionary["actor"]
	if cd_dictionary["object"] != []:
		print "OBJECT: ", cd_dictionary["object"]
	if cd_dictionary["obj_attribute"] != []:
		print "ATTRIBUTE OF OBJECT: ", cd_dictionary["obj_attribute"]
	if cd_dictionary["from"] != []:
		print "FROM: ", cd_dictionary["from"]
	if cd_dictionary["to"] != []:
		print "TO: ", cd_dictionary["to"]
	print "#############################################"
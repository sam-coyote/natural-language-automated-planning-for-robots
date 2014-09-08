

;inferencia sobre conocimiento

(defrule det_access
	(declare (salience 90))
	; if
	(fact ?room1 is_object_of room)
	(fact ?room2 is_object_of room)
	(test (not (eq ?room1 ?room2)))
	(fact ?door is_object_of door)
	(fact ?door connect ?room1)
	(fact ?door connect ?room2)
	(fact ?door functional_status open)
	
	=>

	; then
	(assert (fact ?room1 connected_to ?room2))
	)




;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;primitive tasks

(defrule execute_say
	; head of action
	?fact_request <- (action SAY message ?message 0 ?idpost)
	
	; preconditions

	=>

	; commands to other modules
	(printout t "Speech generation module - generate speech: " ?message  crlf)

	; efects +

	; efects -
	(retract ?fact_request)
	
	;unlock pending task
	(assert (unlock_requests ?idpost))
	)




(defrule execute_go
	; head of action
	?fact_request <- (action GO location ?place 0 ?idpost)
	
	; preconditions
	?fact_precond <-(fact justina in ?currentplace)
	?fact_att <- (justina attention ?some)

	=>

	; commands to other modules
	(printout t "Navegation module - move robot from: " ?currentplace " to: " ?place crlf)
	
	; efects -
	(retract ?fact_precond)
	(retract ?fact_att)
	; efects +
	(assert (justina in ?place))
	(assert (justina attention none))

	;unlock pending task
	(retract ?fact_request)
	)





(defrule execute_aproach
	; head of action
	?fact_request <- (action APROACH object ?object 0 ?idpost)
	
	; preconditions
	?fact_precond1 <-(fact justina in ?currentplace)
	?fact_precond2 <-(fact ?object in ?currentplace)

	=>

	; commands to other modules
	(printout t "Navegation module - aproach to object: " ?object " in: " ?currentplace crlf)
	(printout t "Robots attention on " ?object crlf)
	
	;unlock pending task
	(retract ?fact_request)
	
	; efects -
	
	; efects +
	(assert (fact justina attention ?object))

	)


(defrule execute_recognize
	; head of action
	?fact_request <- (action RECOGNIZE object ?object 0 ?idpost)
	
	; preconditions
	(fact justina attention ?something)
	(fact ?object on ?something)
	(fact ?object is_object_of ?objclass)

	=>

	; commands to other modules
	(printout t "Recognition module - look for objects: " ?objclass " in: " ?something crlf)
	(printout t "Robot find " ?object crlf)
	
	;unlock pending task
	(retract ?fact_request)
	
	; efects -
	
	; efects +
	(assert (fact ?object graspable yes))

	)


(defrule execute_grasp
	; head of action
	?fact_request <- (action GRASP object ?object 0 ?idpost)
	
	; preconditions
	(fact ?object graspable yes)
	?fact_on <- (fact ?object on ?somewhere)
	=>

	; commands to other modules
	(printout t "Arm module - grasp item: " ?object crlf)
	
	;unlock pending task
	(retract ?fact_request)
	
	; efects -
	(retract ?fact_on)
	
	; efects +
	(assert (fact justina carry ?object))

	)



(defrule execute_drop
	; head of action
	?fact_request <- (action DROP 0 ?idpost)
	
	; preconditions
	?fact_carry <-(fact justina carry ?object)
	=>

	; commands to other modules

	(printout t "Speech generation module - generate speech: i will drop the cargo " ?object  crlf)
	(printout t "Arm module - put down item: " ?object  crlf)
	
	;unlock pending task
	(retract ?fact_request)
	
	; efects -
	(retract ?fact_carry)
	
	; efects +

	)






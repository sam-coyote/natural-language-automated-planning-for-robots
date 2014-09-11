

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

; complex activities

(defrule execute_move_object
	; head of action
	?fact_request <- (action FETCH object ?obj location ?loc destination ?dest 0 ?idpost)
	?fact_id <- (id_count ?current_id)
	
	; preconditions

	=>

	; unfolding activity
	
	(assert (action TAKEOBJECT object ?obj location ?loc 0 (+ ?current_id 1)))
	(assert (action GO location ?dest (+ ?current_id 1) (+ ?current_id 2)))
	(assert (action DROP (+ ?current_id 2) ?idpost))
	
	
	; efects +
	
	
	; efects -
	(retract ?fact_request)
	
	;unlock pending task
	;(assert (unlock_requests ?idpost))
	(assert (id_count (+ ?current_id 2)))
	(retract ?fact_id)
	)







;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; medium complexity

(defrule execute_take_object
	; head of action
	?fact_request <- (action TAKEOBJECT object ?obj location ?loc 0 ?idpost)
	?fact_id <- (id_count ?current_id)
	(fact ?obj on ?furniture)
	; preconditions

	=>

	; unfolding activity
	(assert (action GO location ?loc 0 (+ ?current_id 1)))
	(assert (action APROACH object ?furniture (+ ?current_id 1) (+ ?current_id 2)))
	(assert (action RECOGNIZE object ?obj (+ ?current_id 2) (+ ?current_id 3)))
	(assert (action GRASP object ?obj (+ ?current_id 3) ?idpost))


	
	; efects +
	
	
	; efects -
	(retract ?fact_request)
	
	;unlock pending task
	;(assert (unlock_requests ?idpost))
	(assert (id_count (+ ?current_id 3)))
	(retract ?fact_id)
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


(defrule execute_go_room
	(declare (salience 100))
	; head of action
	?fact_request <- (action GO location ?place 0 ?idpost)
	
	; preconditions
	?fact_precond <-(fact justina in ?currentplace)
	(fact ?currentplace is_object_of room)
	(fact ?place is_object_of room)
	(fact ?place connected_to ?currentplace)
	=>

	; commands to other modules
	(printout t "Navegation module - move robot from room: " ?currentplace " to room: " ?place crlf)
	
	; efects -
	(retract ?fact_precond)

	; efects +
	(assert (fact justina in ?place))
	(assert (fact justina attention none))

	;unlock pending task
	(retract ?fact_request)
	(assert (unlock_requests ?idpost))

	
	;?fact_att <- (fact justina attention ?some)
	;(retract ?fact_att)
	)





;(defrule execute_go
;	; head of action
;	?fact_request <- (action GO location ?place 0 ?idpost)
;	
;	; preconditions
;	?fact_precond <-(fact justina in ?currentplace)
;	
;
;	=>
;
;	; commands to other modules
;	(printout t "Navegation module - move robot from: " ?currentplace " to: " ?place crlf)
;	
;	; efects -
;	(retract ?fact_precond)
;
;	; efects +
;	(assert (fact justina in ?place))
;	(assert (fact justina attention none))
;
;	;unlock pending task
;	(retract ?fact_request)
;	(assert (unlock_requests ?idpost))
;
;	
;	;?fact_att <- (fact justina attention ?some)
;	;(retract ?fact_att)
;	)





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
	(assert (unlock_requests ?idpost))
	
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
	(assert (unlock_requests ?idpost))
	
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
	(printout t "Robot carries item: " ?object crlf)
	
	;unlock pending task
	(retract ?fact_request)
	(assert (unlock_requests ?idpost))
	
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




(defrule unlock_request_4
	?blocked_req <-(unlock_requests ?id)
	?blocked_fact <- (action ?type ?param1 ?p1 ?id ?req_id)
	=>
	(retract ?blocked_fact ?blocked_req)
	(assert (action ?type ?param1 ?p1 0 ?req_id)) 
)


(defrule unlock_request_2
	?blocked_req <-(unlock_requests ?id)
	?blocked_fact <- (action ?type ?id ?req_id)
	=>
	(retract ?blocked_fact ?blocked_req)
	(assert (action ?type 0 ?req_id)) 
)


(defrule execute_emergent_open_door
	(declare (salience -100))
	; head of action
	?fact_request <- (action GO location ?place 0 ?idpost)
	
	; preconditions
	?fact_precond <-(fact justina in ?currentplace)
	(fact ?currentplace is_object_of room)
	(fact ?place is_object_of room)
	
	(not (fact ?place connected_to ?currentplace))
	(fact ?door connect ?place)
	(fact ?door connect ?currentplace)
	=>

	; commands to other modules
	(printout t "Arm module - open door in: " ?door " in: " ?place crlf)
	
	; efects -
	;(retract ?fact_precond)

	; efects +

	;unlock pending task
	(assert (fact ?door functional_status open))

	)

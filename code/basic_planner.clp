
;second tier

(defrule fetch_unfold
	?fact_request <- (request 0 fetch ?object ?object_loc ?position_alignment ?delivery_loc ?delivery_alignment ?id)
	(id_count ?current_id)
	=>
	(assert (request 0 goto ?object_loc ?position_alignment (+ ?current_id 1)))
	(assert (request (+ ?current_id 1) observe ?object (+ ?current_id 2)))
	(assert (request (+ ?current_id 2) grasp ?object (+ ?current_id 3)))
	(assert (request (+ ?current_id 3) goto ?delivery_loc ?delivery_alignment (+ ?current_id 4)))
	(assert (request (+ ?current_id 4) hand_over ?object ?delivery_alignment (+ ?current_id 5)))
	(assert (request (+ ?current_id 5) dummy  (+ ?current_id 6)))
	
	(retract ?fact_request)
	(assert (id_count (+ ?current_id 4)))
	)


(defrule get_unfold
	?fact_request <- (request 0 take ?object ?object_loc ?position_alignment ?id)
	(id_count ?current_id)
	=>
	(assert (request 0 goto ?object_loc ?position_alignment (+ ?current_id 1)))
	(assert (request (+ ?current_id 1) observe ?object (+ ?current_id 2)))
	(assert (request (+ ?current_id 2) grasp ?object (+ ?current_id 3)))
	(assert (request (+ ?current_id 3) dummy  (+ ?current_id 4)))
	
	(retract ?fact_request)
	(assert (id_count (+ ?current_id 4)))
	)

;(defrule locate_blind
;	?fact_request <- (request 0 fetch ?object ?object_loc ?position_alignment ?delivery_loc ?delivery_alignment ?id)
;	)





;first tier

(defrule goto_unfold
	?fact_request <- (request 0 goto ?object_loc ?position_alignment ?id)
	(id_count ?current_id)
	=>
	(printout t "unfolding go "  crlf)
	(assert (request 0 move_to_room ?object_loc (+ ?current_id 1)))
	(assert (request (+ ?current_id 1) align_to_object ?position_alignment ?id))
	(retract ?fact_request)
	(assert (id_count (+ ?current_id 1)))
	)


(defrule tell_unfold
	?fact_request <- (request 0 tell ?person ?room ?message ?id)
	(id_count ?current_id)
	=>

	(assert (request 0 goto ?room ?person 1))
	(assert (request 1 speak ?message (+ ?current_id 1)))
	(retract ?fact_request)
	(assert (id_count (+ ?current_id 1)))
	)





;primitive actions

(defrule execute_speak
	?fact_request <- (request 0 speak ?message ?id)
	=>
	; send command to other modules
	(printout t " generate speech " ?message  crlf)
	; everything in order, facts are updated
	(retract ?fact_request)
	;unlock pending requests
	(assert (unlock_requests ?id))
	)

(defrule execute_move_to_room
	?fact_request <- (request 0 move_to_room ?object_loc ?id)
	?fact_current_loc <- (fact robot in ?current_room)
	(id_count ?current_id)
	=>
	; send command to other modules
	(printout t " move from " ?current_room " to " ?object_loc  crlf)
	; everything in order, facts are updated
	(retract ?fact_request)
	(retract ?fact_current_loc)
	(assert (fact robot in ?object_loc))
	;unlock pending requests
	(assert (unlock_requests ?id))
	)

(defrule execute_align_to_object
	?fact_request <- (request 0 align_to_object ?position_alignment ?id)
	(id_count ?current_id)
	=>
	; send command to other modules
	(printout t " align to object " ?position_alignment crlf)
	; everything in order, facts are updated
	(retract ?fact_request)
	(assert (fact robot aligned ?position_alignment))
	;unlock pending requests
	(assert (unlock_requests ?id))
	)

(defrule execute_observe
	?fact_request <- (request 0 observe ?object ?id)
	(id_count ?current_id)
	(fact ?object ?loc ?place)
	(fact ?loc is_object_of location)
	=>
	; send command to other modules
	(printout t " observe what is in sight and identifies " ?object " located in " ?place  crlf)
	; everything in order, facts are updated
	(retract ?fact_request)
	(assert (fact robot observe ?object))
	;unlock pending requests
	(assert (unlock_requests ?id))
	)


(defrule execute_grasp
	?fact_request <- (request 0 grasp ?object ?id)
	(id_count ?current_id)
	(fact robot aligned ?place)
	?fact_grasp <- (fact ?object ?loc ?place)
	(fact ?loc is_object_of location)
	=>
	; send command to other modules
	(printout t " grasp " ?object " from " ?place  crlf)
	; everything in order, facts are updated
	(retract ?fact_request)
	(retract ?fact_grasp)
	(assert (fact ?object in robot))
	;unlock pending requests
	(assert (unlock_requests ?id))
	)


(defrule execute_hand_over
	?fact_request <- (request 0 hand_over ?object ?align_to_object ?id)
	(id_count ?current_id)
	?fact_grasp <- (fact ?object in robot)
	=>
	; send command to other modules
	(printout t " hand over object " ?object " to " ?align_to_object  crlf)
	; everything in order, facts are updated
	(retract ?fact_request)
	(retract ?fact_grasp)
	(assert (fact ?object in ?align_to_object))
	;unlock pending requests
	(assert (unlock_requests ?id))
	)

(defrule execute_move_from_here
	?fact_request <- (request 0 move_from_here ?direction ?distance ?id)
	(id_count ?current_id)
	(not (exists  (fact robot aligned ?nop)))
	=>
	; send command to other modules
	(printout t " move " ?distance " centimeters to " ?direction  crlf)
	; everything in order, facts are updated
	(retract ?fact_request)
	;unlock pending requests
	(assert (unlock_requests ?id))
	)


(defrule dummy
	?fact_request <- (request 0 dummy ?id)
	=>
	; send command to other modules
	(printout t " take a break to think about life... " crlf)
	; everything in order, facts are updated
	(retract ?fact_request)
	)






; non semantic rules

(defrule unlock_request
	(unlock_requests ?id)
	=>
	(assert (unlock_id_1 ?id))
	(assert (unlock_id_2 ?id))
	(assert (unlock_id_3 ?id))
	(assert (unlock_id_4 ?id))
	(assert (unlock_id_5 ?id))
)

(defrule unlock_id_1
	(unlock_id_1 ?id)
	?blocked_fact <- (request ?id ?type ?p1 ?req_id)
	=>
	(retract ?blocked_fact)
	(assert (request 0 ?type ?p1 ?req_id)) 
)

(defrule unlock_id_2
	(unlock_id_2 ?id)
	?blocked_fact <- (request ?id ?type ?p1 ?p2 ?req_id)
	=>
	(retract ?blocked_fact)
	(assert (request 0 ?type ?p1 ?p2 ?req_id)) 
)

(defrule unlock_id_3
	(unlock_id_3 ?id)
	?blocked_fact <- (request ?id ?type ?p1 ?p2 ?p3 ?req_id)
	=>
	(retract ?blocked_fact)
	(assert (request 0 ?type ?p1 ?p2 ?p3 ?req_id)) 
)

(defrule unlock_id_4
	(unlock_id_4 ?id)
	?blocked_fact <- (request ?id ?type ?p1 ?p2 ?p3 ?p4 ?req_id)
	=>
	(retract ?blocked_fact)
	(assert (request 0 ?type ?p1 ?p2 ?p3 ?p4 ?req_id)) 
)

(defrule unlock_id_5
	(unlock_id_5 ?id)
	?blocked_fact <- (request ?id ?type ?p1 ?p2 ?p3 ?p4 ?p5 ?req_id)
	=>
	(retract ?blocked_fact)
	(assert (request 0 ?type ?p1 ?p2 ?p3 ?p4 ?p5 ?req_id)) 
)




; highly experimental! can cause severe performance drop down

(defrule explicit_class_default
	(declare (salience 99))
	(fact ?class is_kind_of ?parent)
	(fact ?parent ?relation ?value_parent)
	(not (fact ?class ?relation ?value_x))
	(not (eq ?relation is_kind_of))
	(not (eq ?relation is_object_of))
	=>
	; send command to other modules
	;(printout t "se deriva que " ?class " tiene " ?relation " con valor " ?value_parent crlf)
	(assert (fact ?class ?relation ?value_parent))
	)

(defrule explicit_object_default
	(declare (salience 99))
	(fact ?obj is_object_of ?class)
	(fact ?class ?relation ?value_class)
	(not (fact ?obj ?relation ?value_x))
	(not (eq ?relation is_kind_of))
	(not (eq ?relation is_object_of))
	=>
	; send command to other modules
	;(printout t "se deriva que " ?obj " tiene " ?relation " con valor " ?value_class crlf)
	(assert (fact ?obj ?relation ?value_class))
	)


(defrule explicit_object_default_loc
	(declare (salience 99))
	(fact ?obj is_object_of ?class)
	(fact ?class in ?place)
	(not (fact ?obj in ?value_x))
	=>
	; send command to other modules
	;(printout t "se deriva que " ?obj " tiene in con valor " ?value_class crlf)
	(assert (fact ?obj in ?place))
	)

(defrule lol
	(not (fact lol in lol))
	=>
	; send command to other modules
	(printout t "se deriva que no lol in lol"  crlf)
	)





;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;primitive tasks

(defrule execute_say
	; head of action
	?fact_request <- (action SAY message ?message 0 ?idpost)
	
	; preconditions

	=>

	; commands to other modules
	(printout t "generate speech: " ?message  crlf)

	; efects +

	; efects -
	(retract ?fact_request)
	
	;unlock pending task
	(assert (unlock_requests ?idpost))
	)






(defrule go_to_place
	; head of action
	?fact_request <- (action GO destination ?place 0 ?idpost)
	
	?fact_current_loc <- (fact robot in ?current_loc)
	(id_count ?current_id)
	
	=>

	; commands to other modules
	(printout t "navegation move to tag in map " ?place crlf)
	
	; efects + 

	; efects -
	
	;unlock pending requests
	(retract ?fact_request)
	(assert (unlock_requests ?id))
	)


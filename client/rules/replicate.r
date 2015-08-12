replicate {
    delay(*delay) {
	    replicate(*sourceNode,*destRootCollection,*destResource, *out_replicateID)
        #triggerReplication(*commandFile,*pid,*source,*destination)
	 }
}
INPUT *sourceNode="",*destRootCollection="",*destResource="",*policyId="",*delay=""
OUTPUT ruleExecOut,*out_replicateID

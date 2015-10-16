def performRequest_$$NUM$$(session):
    ## URL
    url = "$$URL$$"

    ## HTTP METHOD
    method = "$$METHOD$$"

    ## HEADERS
    headers={}
    $$HEADERS$$
    $$POST_DATA$$
    ## PERFORM REQ
    time_before = time.time()
    $$TRIGGER$$
    time_after = time.time()

    resp_time = (time_after-time_before)*1000.0
    return req.status_code, resp_time, req.text

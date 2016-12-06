
import swaf.engine
import swaf.resp
import swaf

# create a new filter named "header"
@swaf.filter('header')
def addHeader(req, next):

    '''this filter will add a simple heading to a text/plain string response
    body.'''

    # first, call the rest of the filter/handler chain to fulfill the
    # request and generate the response that we'll modify
    resp = next(req)
    
    # Make sure the response body is a string.  It could also be a file
    # object (or something that acts like a file object)
    if type(resp.get('body')) in (str, unicode):
        # add the heading
        resp['body'] = 'Heading\n-----------\n'+resp.get('body')
    
    # return the modified response
    return resp

# the 'header' string here requests that a filter named header be applied to
# this handler
@swaf.handler('/','header')
def root():
    return swaf.resp.ok('text/plain','hello world with header/footer') 


e = swaf.engine.Engine()
e.addHandler(root)
e.addFilter(addHeader) # only makes the filter available - doesn't apply it

application = e.wsgi

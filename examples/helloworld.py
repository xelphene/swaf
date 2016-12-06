
import swaf.engine
import swaf.resp
import swaf

@swaf.handler('/')
def root():
    return swaf.resp.ok('text/plain','hello world') 

e = swaf.engine.Engine()
e.addHandler(root)

application = e.wsgi

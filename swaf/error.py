
import inspect

class SWAFError(Exception):
	pass

class LeafUnknownParamError(SWAFError):
	def __init__(self, leafFunc, req):
		leafParams = set( inspect.getargspec(leafFunc)[0] )
		availKeys = set( req.keys() )
		unknownParams = list( leafParams.difference( availKeys ) )
		
		self.leafFunc = leafFunc
		self.unknownParams = unknownParams
	
	def __str__(self):
		if len(self.unknownParams)==1:
			err = '''
				The leaf handler %s.%s takes a parameter named %s 
				but no filter function added a key with this 
				name to the request dictionary.
			''' % (
				self.leafFunc.__module__,
				self.leafFunc.__name__,
				self.unknownParams[0]
			)
		else:
			err = '''
				The leaf handler %s.%s takes parameters named %s 
				but no filter function added keys with these 
				names to the request dictionary.
			''' % (
				self.leafFunc.__module__,
				self.leafFunc.__name__,
				', '.join(self.unknownParams)
			)
		err = err.replace('\n','')
		err = err.replace('\t','')
		err = err.strip()

		return err
		
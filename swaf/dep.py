
import copy

def findFilters1(node, resolve):

	'''given a swaf node, return a set containing the node and all nodes
	needed to call it (and all nodes needed to call those, and so on
	recurisively). If node is a string, the function resolve will be called
	with it and a node object will be expected as the return value.'''
	
	deps = set()
	
	if type(node)==str:
		node = resolve(node)
	
	deps.add(node)
	
	for child in node.swaf_filters:
		deps = deps.union( findFilters1(child, resolve) )
	
	return deps

def findFilters(filters, resolve):
	all = set()
	for f in filters:
		all = all.union(findFilters1(f, resolve))
	return all
	
def filterDepList(filters):
	g = DepGraph()
	for f in filters:
		g.declareFilter(f.swaf_filter_name)
	
	for f in filters:
		for d in f.swaf_filters:
			g.declareDep(f.swaf_filter_name, d)
	
	return g.flatten()


class DepGraph:
	def __init__(self):
		self._deps = {}
		self._rdeps = {}
		self._indeps = set()
		self._nodes = set()
		
	def declareFilter(self, name):
		if name in self._nodes:
			return
		assert not self._deps.has_key(name)
		assert not self._rdeps.has_key(name)
		assert name not in self._indeps
		assert name not in self._nodes
		self._deps[name] = set()
		self._rdeps[name] = set()
		self._indeps.add(name)
		self._nodes.add(name)
		
	def declareDep(self, cfilter, pfilter):
		'''cfilter depends on pfilter'''
		if pfilter not in self._nodes:
			raise AssertionError('pfilter=%s not in self._nodes=%s' % (
				repr(pfilter), repr(self._nodes)))
		assert cfilter in self._nodes
		assert self._deps.has_key(pfilter)
		assert self._rdeps.has_key(pfilter)
		assert self._deps.has_key(cfilter)
		assert self._rdeps.has_key(cfilter)

		self._deps[cfilter].add(pfilter)
		self._rdeps[pfilter].add(cfilter)
		if cfilter in self._indeps:
			self._indeps.remove(cfilter)

	def flatten(self):

		'''determine the correct evaluation order for this dep graph
		(destroys it in the process). returns a list of strings. Evalutate
		list[0] first.'''

		l = []
		while True:
			indeps = self._removeIndeps()
			if indeps == []:
				if len(self._nodes)!=0:
					raise AssertionError('cyclic dependancy graph')
				else:
					return l
			else:
				#l.append(indeps)
				l += indeps
	
	def _remove(self, filter):
		'''remove filter and all declarations of dependancy upon it.'''
		assert filter in self._indeps
		self._indeps.remove(filter)
		for n in self._rdeps[filter]:
			self._deps[n].remove(filter)
			if len(self._deps[n])==0:
				self._indeps.add(n)
		self._nodes.remove(filter)

	def _removeIndeps(self):
		'''remove all independant filters and return them'''
		
		indeps = list(copy.copy(self._indeps))
		for i in indeps:
			self._remove(i)
		return indeps

		
def closure(name='asdf'):
	def _closure():
		return name
	return _closure

def main():
	g = DepGraph()
	
	c = closure()
	
	g.declareFilter('a')
	g.declareFilter('b')
	g.declareFilter('c')
	g.declareFilter('d')
	g.declareFilter('x')
	g.declareFilter('w')
	g.declareFilter('y')
	g.declareFilter('z')
	g.declareFilter(c)
	
	g.declareDep('a','b')
	g.declareDep('a','c')
	g.declareDep('b','d')
	g.declareDep('d','x')
	g.declareDep('x','y')
	g.declareDep('x','z')
	g.declareDep('x','w')
	g.declareDep('a',c)

	#g.declareDep('d','a')
	
	print g.flatten()

if __name__ == '__main__':
	main()


import os
import logging
import mimetypes

import swaf
import swaf.router
import swaf.resp
from swaf.misc import Regex

@swaf.handler(swaf.router.NotFoundRoute)
def notFound():
	return swaf.resp.notFound()

class PkgFileServer:
	def __init__(self, pkg, notFoundResp=None):
		self.swaf_route = Regex('^/static/')
		self._root = os.path.join( pkg.__path__[0], 'static' )
		self._available = set()
		self._log = logging.getLogger('swaf.PkgFileServer')
		self.rescan()
		if notFoundResp==None:
			notFoundResp = swaf.resp.notFound()
		self.notFoundResp = notFoundResp
		self.swaf_description = 'static files server'
		
	
	def rescan(self):
		self._available = set()
		for dirpath, dirnames, filenames in os.walk(self._root):
			for fn in filenames:
				reldirpath = dirpath[len(self._root):]
				fp = os.path.join('/',reldirpath, fn)
				self._available.add(fp)
	
	def __call__(self, **req):
		if not req['path'].startswith('/static/'):
			self._log.error("misrouted request! %s does not start with '/static/'" % repr(req['path']))
			return self.notFoundResp
		
		rel = req['path'][len('/static/'):]
		
		if '/'+rel in self._available:
			full_path = os.path.join(self._root, rel)
			mime_type = mimetypes.guess_type(full_path)[0]
			return swaf.resp.ok(mime_type, open(full_path))
		else:
			return self.notFoundResp

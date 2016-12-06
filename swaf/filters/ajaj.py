
import swaf

def make_ajaj_filter(json_parse_error_response):
	import simplejson
	
	#def json_resp(data):
	#	try:
	#		data = simplejson.dumps(data)
	#	except ValueError, ve:
	#		raise ValueError('could not encode response data %s as JSON: %s' % (
	#			repr(data), str(ve)
	#		))
	#	return swaf.resp.ok('application/json', data)
	
	@swaf.filter('ajaj', 'rawpost require_method_post')
	def _ajaj_filter(req, next):
		body = req['body_str']
		assert type(body) == str
		try:
			data = simplejson.loads(body)
		except ValueError, ve:
			return json_parse_error_response
		
		req['json_body'] = data
		#req['json_resp'] = json_resp
		
		resp = next(req)
		#if not swaf.resp.is_a_resp(resp):
		#	try:
		#		body = simplejson.dumps(resp)
		#	except ValueError, ve:
		#		raise ValueError('resp %s does not look like a normal response and it could not be JSON encoded (error: %s)' % (
		#			repr(resp), str(ve)
		#		)
		#	return json_resp(body)
		#else:
		return resp
	
	return _ajaj_filter

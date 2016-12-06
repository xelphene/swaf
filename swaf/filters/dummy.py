
import swaf

def make_dummy_filter(name, deps):
	@swaf.filter(name, filters=deps)
	def _filter(req, next):
		return next(req)
	return _filter
	
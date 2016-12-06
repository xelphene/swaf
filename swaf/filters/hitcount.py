
import swaf
import psycopg2.extensions

def get_and_inc_hits_pg(dbh):
	previso = dbh.isolation_level
	
	dbh.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)
	cur = dbh.cursor()
	cur.execute('select numhits from hitcount limit 1');
	row = cur.fetchone()
	c = int(row[0])
	c += 1
	cur.execute('update hitcount set numhits=%d' % c)
	dbh.commit()
	
	dbh.set_isolation_level(previso)
	return c

@swaf.filter('hitcount_tmpl', filters='tmpl hitcount_count')
def hitcount_tmpl(req, next):
	outer_trender = req['trender']
	
	def trender(path, **kwargs):
		kwargs['hitcount'] = req['hitcount']
		return outer_trender(path, **kwargs)
	
	req['trender'] = trender
	return next(req)

@swaf.filter('hitcount_count', filters='dbh')
def hitcount_count(req, next):
	assert req.has_key('dbh')
	try:
		count = get_and_inc_hits_pg(req['dbh'])
	except:
		# TransactionRollbackError: could not serialize access due to concurrent update
		count = 931
	req['hitcount'] = count
	return next(req)
		
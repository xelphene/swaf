
import psycopg2
import swaf

def make_dbh_filter(hostname, database, username, password):
	dbh = psycopg2.connect(
		host = hostname,
		user = username,
		database = database,
		password = password
	)
	
	@swaf.filter('dbh')
	def add_dbh(req, next):
		req['dbh'] = dbh
		return next(req)
	
	return add_dbh

def make_dbh_filter_from_conf(conf, section='database'):
	dbh = psycopg2.connect(
		host = conf.get(section, 'host'),
		user = conf.get(section, 'username'),
		database = conf.get(section, 'database'),
		password = conf.get(section, 'password')
	)
	
	@swaf.filter('dbh')
	def add_dbh(req, next):
		req['dbh'] = dbh
		return next(req)
	
	return add_dbh

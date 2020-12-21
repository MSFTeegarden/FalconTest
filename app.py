server = 'server.database.windows.net'
database = 'db'
username = 'user'
password = 'password'
driver = '{ODBC Driver 17 for SQL Server}'
conn =
pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+data
base+';UID='+username+';PWD='+ password, autocommit=True)
cur = conn.cursor()
cur.execute('SELECT @@version')
db_version = cur.fetchone()[0]
print(db_version)
def create_destroy_session(id, action):
if (action == '/login'):
cur.execute("insert into sessions values (%d, '1', GETDATE(), NULL)" %
int(id))
Application Cache Performance Testing v1.0 20
elif (action == '/logout'):
cur.execute("update sessions set isActive = '0', inactiveDate = GETDATE()
where sessionID = %d" % int(id))
token = id
return token
def add_remove_view_item(id, item, action):
cur.execute("select sessionId from sessions where sessionID = %d andisActive
= '1'" % int(id))
r = cur.fetchall()
if (r):
cur.execute("select price from items where itemID = %d" % int(item))
r = cur.fetchall()
if (r):
if (action == '/add'):
cur.execute("insert into carts values (%d, %d, %.2f, GETDATE())" % (int(id),
int(item), float(r[0][0])))
cur.execute("select price from carts where sessionId = %d and itemId = %d" %
(int(id), int(item)))
r = cur.fetchall()
if (r):
cur.execute("delete from carts where sessionId = %d and itemId = %d" %
(int(id), int(item)))
else:
return False
return True
else:
return False
else:
return False
return True
class SessionResource(object):
def on_get(self, req, resp):
try:
r = create_destroy_session(req.params['id'], req.path)
except:
r = False
if (r):
resp.status = falcon.HTTP_200
resp.body = ('{"status": "Ok"}n')
else:
resp.status = falcon.HTTP_500
resp.body = ('{"status": "Error"}n')
class ItemResource(object):
def on_get(self, req, resp):
try:
r = add_remove_view_item(req.params['id'], req.params['item'], req.path)
except:
r = False
if (r):
Application Cache Performance Testing v1.0 21
resp.status = falcon.HTTP_200
resp.body = ('{"status": "Ok"}n')
else:
resp.status = falcon.HTTP_500
resp.body = ('{"status": "Error"}n')
class ClearAllResource(object):
def on_get(self, req, resp):
try:
cur.execute("truncate table carts")
cur.execute("truncate table sessions")
r = True
except:
r = False
if (r):
resp.status = falcon.HTTP_200
resp.body = ('{"status": "Ok"}n')
else:
resp.status = falcon.HTTP_500
resp.body = ('{"status": "Error"}n')
app = falcon.API()
session = SessionResource()
item = ItemResource()
clearall = ClearAllResource()
app.add_route('/login', session)
app.add_route('/logout', session)
app.add_route('/view', item)
app.add_route('/add', item)
app.add_route('/remove', item)
app.add_route('/clear', clearall)

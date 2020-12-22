#import libraries--falcon is a python web framework and pyodbc is used to connect to the database
import falcon
import sys
import time
import pyodbc

# connection parameters--replace with your own info
server = 'benchmarkingserver.database.windows.net'
database = 'MyDatabase'
username = 'kyle'
password = 'password1234!'
driver = '{ODBC Driver 17 for SQL Server}'

conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password, autocommit=True)
cur = conn.cursor()
cur.execute('SELECT @@version')
db_version = cur.fetchone()[0]
print(db_version)

def create_destroy_session(id, action):
    if (action == '/login'):
        cur.execute("insert into sessions values (%d, '1', GETDATE(), NULL)" %int(id))

    elif (action == '/logout'):
        cur.execute("update sessions set isActive = '0', inactiveDate = GETDATE()where sessionID = %d" % int(id))

    token = id
    return token

def add_remove_view_item(id, item, action):
    cur.execute("select sessionId from sessions where sessionID = %d andisActive= '1'" % int(id)) # check if session exists and is active
    r = cur.fetchall()
    if (r): #If the session is active
        cur.execute("select price from items where itemID = %d" % int(item)) #select item price from given itemID
        r = cur.fetchall()
        if (r): #If the price is found
            if (action == '/add'): #If add action, add price to cart in active session
                cur.execute("insert into carts values (%d, %d, %.2f, GETDATE())" % (int(id),int(item), float(r[0][0])))
                # Another if statement goes here?
                cur.execute("select price from carts where sessionId = %d and itemId = %d" %(int(id), int(item)))
                r = cur.fetchall()
                if (r):
                    cur.execute("delete from carts where sessionId = %d and itemId = %d" %(int(id), int(item)))
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

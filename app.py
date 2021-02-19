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
print(db_version, flush=True)
print('logged in', flush=True)  # Note: adding 'flush=True' after the print statement causes falcon to print the line to console.

def create_destroy_session(id, action): # This method handles the "login" and "logout" API calls
    if (action == '/login'):
        cur.execute("select sessionId from sessions where sessionID = %d" %int(id)) # see if session exists in database
        r = cur.fetchall()
        if (r):
            print(str(r), flush=True)
            print('session already exists', flush=True)
            cur.execute("update sessions set isActive = '1' where sessionID = %d" %int(id)) # update active status
        else:
            cur.execute("insert into sessions values (%d, '1', GETDATE(), NULL)" %int(id)) # if session doesn't exist, create new one
            print('new session created', flush=True)

    elif (action == '/logout'):
        cur.execute("update sessions set isActive = '0', inactiveDate = GETDATE() where sessionID = %d" % int(id)) # set session to inactive
        print('logout complete', flush=True)
    token = id
    return token # return the session ID

def add_remove_view_item(id, item, action): # this method handles the "view", "add", and "remove" API calls
    print('starting process', flush=True)
    cur.execute("select sessionId from sessions where sessionID = %d and isActive= '1'" % int(id)) # check if session exists and is active
    r = cur.fetchall()
    print('session check complete', flush=True)
    print(str(r), flush=True)
    
    if (r): #If the session is active
        
        if (action == '/view'):

            print('action: view', flush=True)
            cur.execute("select price from items where itemID = %d" % int(item)) #select item price from given itemID
            r = cur.fetchall()
            print('sucessful price check', flush=True)
            print(str(r[0][0]), flush=True)
            return str(r[0][0]) # return the price
        
        elif (action == '/add'):

            cur.execute("select price from items where itemID = %d" % int(item)) #select item price from given itemID
            r = cur.fetchall()
            if(r): # if the item exists
                cur.execute("select price from carts where sessionId = %d and itemId = %d" %(int(id), int(item))) # lookup item to see if is already in cart
                r = cur.fetchall()
                if(r):
                    cur.execute("insert into carts values (%d, %d, %.2f, GETDATE())" % (int(id),int(item), float(r[0][0]))) # add item to cart
                    return True
                else:
                    return False
            else:
                return False
        
        elif (action == '/remove'):

            cur.execute("select price from carts where sessionId = %d and itemId = %d" %(int(id), int(item))) # lookup item to see if it exists
            r = cur.fetchall()
            if(r): # if it exists
                cur.execute("delete from carts where sessionId = %d and itemId = %d" %(int(id), int(item))) # delete item from cart
                return True
            else:
                return False
        
        else:
            return False
    else:
        return False
    return False


class SessionResource(object):
    def on_get(self, req, resp):
        try:
            r = create_destroy_session(req.params['id'], req.path)
            # if login/logout request is sucessful:
            resp.status = falcon.HTTP_200
            resp.body = ('{"status": "Ok", "sucess": "'+ str(r) +'"}')
            print('sucessful session action', flush=True)

        except Exception as e:
            # if login/logout request is unsucessful: 
            resp.status = falcon.HTTP_500
            resp.body = (str(e))
            print('failed session action', flush=True)

class ItemResource(object):
    def on_get(self, req, resp):
        try:
            r = add_remove_view_item(req.params['id'], req.params['item'], req.path)
            # if add/view/remove request is sucessful
            resp.status = falcon.HTTP_200
            resp.body = ('{"status": "Ok", "sucess": "'+ str(r) +'"}')
            print('sucessful action', flush=True)

        except Exception as e:
            # if add/view/remove request is unsucessful
            r = False
            resp.status = falcon.HTTP_500
            resp.body = (str(e))
            print('failed action', flush=True)

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
            resp.body = ('{"status": "Ok"}')
        else:
            resp.status = falcon.HTTP_500
            resp.body = ('{"status": "Error"}')

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

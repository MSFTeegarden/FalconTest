#import libraries--falcon is a python web framework and pyodbc is used to connect to the database
import falcon
import sys
import time
import pyodbc
import redis
from datetime import datetime

# connection parameters--replace with your own info
server = 'benchmarkingserver.database.windows.net'
database = 'MyDatabase'
username = 'kyle'
password = 'password1234!'
driver = '{ODBC Driver 17 for SQL Server}'

# connect to the database
conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password, autocommit=True)
cur = conn.cursor()
cur.execute('SELECT @@version')
db_version = cur.fetchone()[0]
print(db_version, flush=True)
print('logged in', flush=True)  # Note: adding 'flush=True' after the print statement causes falcon to print the line to console.

# connect to the Redis instance
r = redis.Redis(host='redisbenchmark.redis.cache.windows.net', port=6380, db=0, password='qKP1nKP58PtVkGHhqdIE0a0hbcrWELrVV4SkcWUae8o=', ssl=True, charset="utf-8", decode_responses=True)
print('Redis v.' + r.execute_command('INFO')['redis_version'], flush=True)


def create_destroy_session(id, action): # This method handles the "login" and "logout" API calls
    store_dt = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
    if (action == '/login'):
        r.hmset("session:" + id, { "isActive": 1, "activeDate": store_dt })
        return True
    
    elif (action == '/logout'):
        r.hmset("session:" + id, { "isActive": 0, "inactiveDate": store_dt })
        return True
    else:
        return False
    return True

def add_remove_view_item(id, item, action): # this method handles the "view", "add", and "remove" API calls
    global r

    if (r.hget("session:" + id, "isActive") == '1'): # check if session exists and is active

        if (action == '/view'):
            price = r.get("item:" + item)  # check cache for price
            if not price:
                cur.execute("select price from items where itemID = %d" % int(item))  # if price is not in cache, check DB
                price = cur.fetchall()[0][0]
                r.set("item:" + item, str(price))  # add price to cache
            
            return str(price) # return the price
        
        elif (action == '/add'):
            store_dt = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
            price = r.get("item:" + item)
            r.hmset("cart:" + id + ":item:" + item, { "price": price,"addedDate": store_dt })
            return True

        elif (action == '/remove'):
            if (r.exists("cart:" + id + ":item:" + item)):
                r.delete("cart:" + id + ":item:" + item)
                return True
            else:
                return False
        
        else:
            return False
    else:
        return False
    return True


class SessionResource(object):
    def on_get(self, req, resp):
        try:
            start = time.process_time() # get start time for process
            r = create_destroy_session(req.params['id'], req.path)
            print(time.process_time() - start, flush=True) # print out elapsed time
            # if login/logout request is sucessful:
            resp.status = falcon.HTTP_200
            resp.body = ('{"status": "Ok"}')

        except Exception as e:
            # if login/logout request is unsucessful: 
            resp.status = falcon.HTTP_500
            resp.body = ('{"status": "Error"}')

class ItemResource(object):
    def on_get(self, req, resp):
        try:
            start = time.process_time()
            r = add_remove_view_item(req.params['id'], req.params['item'], req.path)
            print(time.process_time() - start, flush=True) #print out elapsed time
            # if add/view/remove request is sucessful
            resp.status = falcon.HTTP_200
            resp.body = ('{"status": "Ok"}')

        except Exception as e:
            # if add/view/remove request is unsucessful
            r = False
            resp.status = falcon.HTTP_500
            resp.body = ('{"status": "Error"}')

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

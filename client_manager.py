from google.appengine.ext import db
from google.appengine.api import channel
from google.appengine.ext import webapp
from datetime import timedelta, datetime
from django.utils import simplejson as json

class TicketClient(db.Model):
    ''' all active clients list '''
    def __init__(self, *args, **kwargs):
        kwargs['key_name'] = kwargs['client_id']
        db.Model.__init__(self, *args, **kwargs)
    
    client_id = db.StringProperty()
    update_time = db.DateTimeProperty(auto_now = True)
    access_token = db.StringProperty()
 
def seconds_ago(time_s):
    td = timedelta(seconds = time_s)
    return datetime.now() - td   

class TicketClientObserver():
    '''delete inactive client from client list, 
    the define of inactive client is the one that is more
    than 1 minute not updated .  Run this observer in 
    a cron every 5 second '''
    MAX_FETCH = 500
    def clearOldClients(self, time_s):    
        #query and get ticket older than time_s
        my_query = TicketClient.all(keys_only=True).filter("update_time < ", seconds_ago(time_s))
        clients = my_query.fetch(TicketClientObserver.MAX_FETCH)
        msg = json.dumps({"error":{"code":1, "msg":"connection timeout"}})
        map(lambda c: channel.send_message(c, end_msg), clients)
        db.delete(clients)

    def notifyAllClients(self, msg):
        my_query = TicketClient.all()
        clients = my_query.fetch(TicketClientObserver.MAX_FETCH)
        for client in clients:
            channel.send_message(client.client_id, msg)

        #no api to recycle the channel, so it maybe is limit to the max number of channels
        #is this right?
    def notifyClient(self, client_id, msg):
        channel.send_message(client_id, msg)

class ClearOldClientsHandler(webapp.RequestHandler):
    def get(self):
        clientObserver = TicketClientObserver()
        clientObserver.clearOldClients(70)
    
    
    
    
    

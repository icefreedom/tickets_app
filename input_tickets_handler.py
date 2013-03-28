import cgi
from google.appengine.ext import webapp
from google.appengine.ext import db
from client_manager import TicketClientObserver
from datetime import datetime
import time
from django.utils import simplejson as json
import urllib

class Ticket(db.Model):
    '''model ticket '''
    created_time = db.DateTimeProperty(auto_now_add=True)
    buyin = db.IntegerProperty()
    sellout = db.IntegerProperty()
    price = db.IntegerProperty()
    high_price_buyin = db.IntegerProperty()
    high_price_sellout = db.IntegerProperty()
    
    def toJson(self):
        #in order
        seconds = long(time.mktime(self.created_time.timetuple()))
        list_e = [seconds, self.buyin, self.sellout, self.price, self.high_price_buyin,
                    self.high_price_sellout]
        return json.dumps({"0-1":list_e})



class InputTicketsHandler(webapp.RequestHandler):
    '''store tickets into db, and send message to 
       all active client'''


    def post(self):
        #get all inputs
        ticket = Ticket()
        ticket.buyin = long(cgi.escape(self.request.get('buyin')))
        ticket.sellout = long(cgi.escape(self.request.get('sellout')))
        ticket.price = long(cgi.escape(self.request.get('price')))
        ticket.high_price_buyin = long(cgi.escape(self.request.get('high_price_buyin')))
        ticket.high_price_sellout = long(cgi.escape(self.request.get('high_price_sellout')))
        #valid
        #store into db
        ticket.put()
        #notify all active clients
        clientObserver = TicketClientObserver()
        clientObserver.notifyAllClients(ticket.toJson())        
        #redirect 
        self.redirect('/?' + urllib.urlencode({'count': Ticket.all(keys_only=True).count()}))
    

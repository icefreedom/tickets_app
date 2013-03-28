from google.appengine.ext import webapp
from google.appengine.api import channel
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.api import taskqueue
from client_manager import TicketClient, TicketClientObserver
import os
from django.utils import simplejson as json

class KeepAlive(webapp.RequestHandler):
    '''receive client beat heart message'''
    def post(self):
        #authenticate user
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        taskqueue.add(url='/beatheart_handler', params={'client_id': user.user_id()})

class BeatHeartHandler(webapp.RequestHandler):
    '''task worker'''
    def post(self):
        client_id = self.request.get('client_id')
        client = TicketClient.get_by_key_name(client_id)
        if client:
            client.put()


class ServerPage(webapp.RequestHandler):
    '''create channel to client'''
    def get(self):
        #authenticate user
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        #is it exist
        client = TicketClient.get_by_key_name(user.user_id())
        if client:
            clientObserver = TicketClientObserver()
            clientObserver.notifyClient(client.client_id, json.dumps({"close":1}))
            client.delete()
        #create channel
        access_token = channel.create_channel(user.user_id(), duration_minutes = 30)
        #store into client list
        client = TicketClient(client_id = user.user_id(), access_token = access_token)
        client.put()
        #show page
        temp_values = {"access_token": client.access_token}
        page_path = os.path.join(os.path.dirname(__file__), 'ticket_client.html')
        self.response.out.write(template.render(page_path, temp_values))

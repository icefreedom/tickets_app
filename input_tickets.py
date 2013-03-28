import os
import cgi
from google.appengine.ext import webapp
from google.appengine.api import channel
from google.appengine.api import users
from google.appengine.ext.webapp import template


class InputTicket(webapp.RequestHandler):
    '''provide an entrance for users to 
        input tickets information'''
    def get(self):
        #authenticate user
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        #already exist tickets
        tickets_count = cgi.escape(self.request.get('count'))  \
                        if self.request.get('count') else ''
        temp_values = {'tickets_count': tickets_count}
        #show input page
        page_path = os.path.join(os.path.dirname(__file__), 'input_tickets_page.html')
        self.response.out.write(template.render(page_path, temp_values))
        

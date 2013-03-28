from google.appengine.ext import webapp
from input_tickets import InputTicket
from ticket_server import ServerPage, KeepAlive, BeatHeartHandler
from input_tickets_handler import InputTicketsHandler
from client_manager import ClearOldClientsHandler
from google.appengine.ext.webapp.util import run_wsgi_app


application = webapp.WSGIApplication( [('/', InputTicket),
                                    ('/subscrible', ServerPage),
                                    ('/beatheart', KeepAlive),
                                    ('/beatheart_handler', BeatHeartHandler),
                                    ('/input_tickets_handler', InputTicketsHandler),
                                    ('/clearOldClient', ClearOldClientsHandler)],
                                    debug = True)

def main():
    run_wsgi_app(application)
    

if __name__ == '__main__':
    main()


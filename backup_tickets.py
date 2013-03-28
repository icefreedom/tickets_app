import sys
APPENGINE_PATH = '/path/to/google_appengine/'
sys.path.append(APPENGINE_PATH)
sys.path.append(APPENGINE_PATH + 'lib/yaml/lib/')
sys.path.append(APPENGINE_PATH + 'lib/fancy_urllib/')
sys.path.append(APPENGINE_PATH + 'lib/webob-1.2.3/')
sys.path.append(APPENGINE_PATH +'lib/django-1.2/')

from google.appengine.ext.remote_api import remote_api_stub
from input_tickets_handler import Ticket
import getpass
import time
from datetime import datetime
from multiprocessing import Process, Queue
from subprocess import call

from pygit2 import Repository, Signature
import os
import time
from datetime import datetime, date, timedelta


def auth_func():
  return (raw_input('Username:'), getpass.getpass('Password:'))



remote_api_stub.ConfigureRemoteApi(None, '/_ah/remote_api', auth_func,
                                   'localhost:8080')

last_fetch_ts = datetime.utcnow()
def fetch_new_tickets(queue):
    global last_fetch_ts
    while True:
        next_fetch_ts = last_fetch_ts + timedelta(seconds = 5)
        if next_fetch_ts > datetime.utcnow():
            time.sleep((next_fetch_ts - datetime.utcnow()).total_seconds())
        fetch_ts = last_fetch_ts
        last_fetch_ts = datetime.utcnow()
        tickets = Ticket.all().filter('created_time > ', fetch_ts).fetch(500)
        map(lambda ticket: queue.put(ticket, block=True), tickets)

def push_to_github(repo_path):
    username = 'yourname'
    passwd = 'yourpasswd'
    remote_repo = 'https://%s:%s@github.com/icefreedom/tickets_history.git' % (username, passwd)
    call(['cd "' + repo_path + '" && git push ' + remote_repo] , shell=True)

last_push_ts = None
def commit_new_tickets_to_git(queue, repo_path):
    global last_push_ts
    #repo
    repo = Repository(os.path.join(repo_path, '.git'))
    index = repo.index
    author = Signature('yourname', 'youremail')
    while True:
        #write tickets into file
        ticket = queue.get(block=True)
        #filename format is yyyy-mm-dd
        d = datetime.utcnow().date()
        filename = '%s.txt' % d.strftime('%Y-%m-%d')
        f = open(os.path.join(repo_path, filename), 'ab')
        f.write('%s\n' % ticket.toJson())
        f.close()
        #commit
        index.add(filename)
        index.write()
        oid = index.write_tree()
        repo.create_commit('HEAD', author, author, ticket.toJson(), oid, [repo.head.oid])
        #push
        d_ts = datetime.utcnow()
        if last_push_ts is None or d_ts > (last_push_ts + timedelta(seconds = 60)):
            push_to_github(repo_path)
            last_push_ts = datetime.utcnow()


def main():
    queue = Queue()
    tickets_fetcher = Process(target=fetch_new_tickets, args=(queue,))
    tickets_fetcher.start()
    repo_path = '/path/to/tickets_history/'
    tickets_committer = Process(target=commit_new_tickets_to_git, args=(queue, repo_path, ))
    tickets_committer.start()
    tickets_fetcher.join();
    tickets_committer.join();

if __name__ == '__main__':
    main()
        



    
    

            
    
    
    
    


    


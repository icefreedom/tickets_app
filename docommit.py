from pygit2 import Repository, Signature
import os
from datetime import datetime, date
from subprocess import call

d = datetime.utcnow().date()
path = '/home/xubin/workspace/tickets_history/'
name = '%s.txt' % d.strftime('%Y-%m-%d')
abspath = os.path.join(path, name)
f = open(abspath, 'ab')
f.write('test\n');
f.close()

repo = Repository(os.path.join(path, '.git'))
index = repo.index
index.add(name)
index.write()
oid = index.write_tree()

author = Signature('icefreedom', 'myxu_bin@163.com')

cm  = repo.create_commit('HEAD', author, author, 'test', oid, [repo.head.oid])

username = 'icefreedom'
passwd = '87650872ice'
remote_repo = 'https://%s:%s@github.com/icefreedom/tickets_history.git' % (username, passwd)
call(['cd "' + path + '" && git push ' + remote_repo] , shell=True)


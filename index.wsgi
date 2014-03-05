import sae
from test4weixin import wsgi

application = sae.create_wsgi_app(wsgi.application)

from wsgiproxy.app import WSGIProxyApp
from cgi import parse_qs

import urlparse
import logging
import functools

logger = logging.getLogger('jstools.proxy')

def param_forwarding(sfe):
    @functools.wraps(sfe)
    def wrapper(proxy, environ):
        url = parse_qs(environ['QUERY_STRING']).get('url', None)
        if url is not None:
            if isinstance(url, list):
                assert len(url) == 1, ValueError('Multiple urls submitted')
                url = urlparse.urlparse(url[0])
            else:
                raise ValueError('We expected a list')

            port = ''
            if url.port:
                port = ":%s" %url.port

            proxy.href = "%s://%s%s%s" %(url.scheme, url.hostname, port, url.path)
            environ['QUERY_STRING'] = url.query
        if not proxy.href:
            raise ValueError('No default url, no parameterized url? what do you want me to do?')
        sfe(proxy, environ)
    return wrapper

class ParamQueryProxy(WSGIProxyApp):
    
    def __init__(self, href, secret_file=None,
                 string_keys=None, unicode_keys=None,
                 json_keys=None, pickle_keys=None):
        if href:
            self.href = href
        self.secret_file = secret_file
        self.string_keys = string_keys or ()
        self.unicode_keys = unicode_keys or ()
        self.json_keys = json_keys or ()
        self.pickle_keys = pickle_keys or ()

    setup_forwarded_environ = param_forwarding(WSGIProxyApp.setup_forwarded_environ)

        
def make_proxy(global_conf, href=None, secret_file=None):
    if secret_file is None and 'secret_file' in global_conf:
        secret_file = global_conf['secret_file']
    return ParamQueryProxy(href=href, secret_file=secret_file)

"""Static local preview. Wildlife refreshes through the monthly GitHub workflow."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial
ROOT=Path(__file__).resolve().parents[1]/'dist'
if __name__=='__main__':
 print('Portfolio: http://127.0.0.1:4174/\nWildlife: http://127.0.0.1:4174/wildlife/')
 ThreadingHTTPServer(('127.0.0.1',4174),partial(SimpleHTTPRequestHandler,directory=str(ROOT))).serve_forever()

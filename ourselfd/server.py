from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .membrane import Membrane
from .models import ActionIntent
class Handler(BaseHTTPRequestHandler):
    membrane=None
    def _json(self,status,payload):
        body=json.dumps(payload,sort_keys=True).encode()
        self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_POST(self):
        if self.path!="/v1/intents": return self._json(404,{"error":"NOT_FOUND"})
        try:
            n=int(self.headers.get("Content-Length","0")); p=json.loads(self.rfile.read(n)); d=self.membrane.admit(ActionIntent.from_dict(p)); self._json(200,d.as_dict())
        except (ValueError,TypeError,json.JSONDecodeError) as e: self._json(400,{"error":str(e)})
        except Exception: self._json(500,{"error":"MEMBRANE_FAILURE"})
    def log_message(self,*args): return
def serve(state_path="ourselfd-state/state.db",host="127.0.0.1",port=8765,instance_id="SELF-LOCAL-DEV"):
    Handler.membrane=Membrane(state_path,instance_id); ThreadingHTTPServer((host,port),Handler).serve_forever()
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser(); p.add_argument("--state",default="ourselfd-state/state.db"); p.add_argument("--host",default="127.0.0.1"); p.add_argument("--port",type=int,default=8765); p.add_argument("--instance-id",default="SELF-LOCAL-DEV")
    a=p.parse_args(); serve(a.state,a.host,a.port,a.instance_id)

from __future__ import annotations
import json, sqlite3, threading
from pathlib import Path
from typing import Any
class Store:
    """Authoritative OURSELFD state. Hermes receives no database connection or path."""
    def __init__(self,path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self._lock=threading.RLock()
        self.db=sqlite3.connect(self.path,check_same_thread=False); self.db.row_factory=sqlite3.Row; self._init()
    def _init(self):
        with self._lock,self.db:
            self.db.executescript("""PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL;
            CREATE TABLE IF NOT EXISTS authority(authority_ref TEXT PRIMARY KEY,instance_id TEXT NOT NULL,
            operation TEXT NOT NULL,target_kind TEXT,active INTEGER NOT NULL,metadata_json TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS ledger(seq INTEGER PRIMARY KEY AUTOINCREMENT,event_type TEXT NOT NULL,
            event_id TEXT NOT NULL UNIQUE,intent_id TEXT,instance_id TEXT,payload_json TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS receipts(receipt_ref TEXT PRIMARY KEY,intent_id TEXT NOT NULL,
            phase TEXT NOT NULL,decision TEXT NOT NULL,payload_json TEXT NOT NULL);""")
    def put_authority(self,authority_ref,instance_id,operation,target_kind=None,metadata=None):
        with self._lock,self.db:
            self.db.execute("INSERT OR REPLACE INTO authority VALUES(?,?,?,?,1,?)",
                            (authority_ref,instance_id,operation,target_kind,json.dumps(metadata or {},sort_keys=True)))
    def resolve_authority(self,authority_ref,instance_id,operation,target_kind):
        with self._lock:
            r=self.db.execute("SELECT instance_id,operation,target_kind,active FROM authority WHERE authority_ref=?",(authority_ref,)).fetchone()
        return bool(r and r["active"] and r["instance_id"]==instance_id and r["operation"]==operation and (r["target_kind"] is None or r["target_kind"]==target_kind))
    def append(self,event_type,event_id,payload,intent_id=None,instance_id=None):
        with self._lock,self.db:
            self.db.execute("INSERT INTO ledger(event_type,event_id,intent_id,instance_id,payload_json) VALUES(?,?,?,?,?)",
                            (event_type,event_id,intent_id,instance_id,json.dumps(payload,sort_keys=True)))
    def receipt(self,receipt_ref,intent_id,phase,decision,payload):
        with self._lock,self.db:
            self.db.execute("INSERT OR REPLACE INTO receipts VALUES(?,?,?,?,?)",
                            (receipt_ref,intent_id,phase,decision,json.dumps(payload,sort_keys=True)))

import tempfile
from pathlib import Path
from ourselfd.membrane import Membrane
from ourselfd.models import ActionIntent
def make(**overrides):
    p={"schema":"OURSELF_ACTION_INTENT_V1","intent_id":"INT-test-001","instance_id":"SELF-test",
       "origin":{"runtime":"hermes","actor":"agent","tool":"terminal"},"operation":"terminal.execute",
       "target":{"kind":"filesystem","reference":"workspace"},"arguments":{"command":"printf hello"},
       "requested_effect":"write test output","side_effect_class":"MUTATION","authority_ref":"AUTH-terminal-test","evidence_required":True}
    p.update(overrides); return ActionIntent.from_dict(p)
def test_declared_authority_is_not_authority():
    with tempfile.TemporaryDirectory() as td:
        m=Membrane(Path(td)/"state.db","SELF-test"); d=m.admit(make())
        assert d.decision=="DENY" and d.reason_code=="AUTHORITY_BOUNDARY"
        m.store.put_authority("AUTH-terminal-test","SELF-test","terminal.execute","filesystem")
        d=m.admit(make()); assert d.decision=="ADMIT" and d.admission_ref and d.superbin_ref
def test_instance_boundary():
    with tempfile.TemporaryDirectory() as td:
        m=Membrane(Path(td)/"state.db","SELF-test"); m.store.put_authority("AUTH-terminal-test","SELF-test","terminal.execute","filesystem")
        d=m.admit(make(instance_id="SELF-other")); assert d.decision=="DENY" and d.reason_code=="INSTANCE_BOUNDARY"
def test_admission_is_not_execution():
    with tempfile.TemporaryDirectory() as td:
        m=Membrane(Path(td)/"state.db","SELF-test"); m.store.put_authority("AUTH-terminal-test","SELF-test","terminal.execute","filesystem")
        assert m.admit(make()).decision=="ADMIT"
        assert not hasattr(m,"execute")

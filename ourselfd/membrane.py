from __future__ import annotations
import time
from .models import ActionIntent, Decision, Receipt, stable_id
from .store import Store
class Membrane:
    """Admission only. This object never executes the proposed effect."""
    def __init__(self,state_path,instance_id="SELF-LOCAL-DEV"):
        self.instance_id=instance_id; self.store=Store(state_path)
    def admit(self,intent: ActionIntent) -> Decision:
        if intent.instance_id != self.instance_id: return self._deny(intent,"INSTANCE_BOUNDARY")
        if not intent.authority_ref: return self._deny(intent,"AUTHORITY_REQUIRED")
        if not self.store.resolve_authority(intent.authority_ref,intent.instance_id,intent.operation,intent.target.get("kind")):
            return self._deny(intent,"AUTHORITY_BOUNDARY")
        superbin={"origin":intent.origin,"instance":intent.instance_id,"target":intent.target,"operation":intent.operation,
                  "arguments":intent.arguments,"invariant_set":["DECLARED_NE_AUTHORITY","INTENT_NE_ADMISSION",
                  "ADMISSION_NE_ACTUATION","ACTUATION_NE_OBSERVATION","OBSERVATION_NE_RECEIPT"],
                  "membrane_ref":"ourselfd:v1","authority_ref":intent.authority_ref,"evidence_contract":"RECEIPT_V1"}
        sb=stable_id("SB",superbin); adm=stable_id("ADM",{"normalized_id":intent.normalized_id,"authority_ref":intent.authority_ref,"superbin_ref":sb})
        d=Decision(intent.intent_id,intent.normalized_id,"ADMIT",authority_ref=intent.authority_ref,admission_ref=adm,superbin_ref=sb,receipt_contract="RCPT_V1")
        self._record(intent,d,superbin); return d
    def _deny(self,intent,reason):
        rr=stable_id("RCPT",{"intent_id":intent.intent_id,"normalized_id":intent.normalized_id,"phase":"ADMISSION","decision":"DENY","reason":reason})
        rec=Receipt(rr,intent.intent_id,"ADMISSION","DENY",{"reason_code":reason,"ts":time.time()})
        self.store.receipt(rr,intent.intent_id,"ADMISSION","DENY",rec.as_dict()); self.store.append("INTENT_DENIED",rr,rec.as_dict(),intent.intent_id,intent.instance_id)
        return Decision(intent.intent_id,intent.normalized_id,"DENY",reason_code=reason,receipt_ref=rr)
    def _record(self,intent,d,superbin):
        rr=stable_id("RCPT",{"intent_id":intent.intent_id,"normalized_id":intent.normalized_id,"phase":"ADMISSION","decision":"ADMIT","admission_ref":d.admission_ref})
        rec=Receipt(rr,intent.intent_id,"ADMISSION","ADMIT",{"ts":time.time(),"admission_ref":d.admission_ref,"superbin_ref":d.superbin_ref,"receipt_contract":d.receipt_contract})
        self.store.receipt(rr,intent.intent_id,"ADMISSION","ADMIT",rec.as_dict())
        self.store.append("INTENT_ADMITTED",d.admission_ref,{"intent":intent.normalized(),"superbin":superbin,"receipt":rec.as_dict()},intent.intent_id,intent.instance_id)

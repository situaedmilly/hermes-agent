from __future__ import annotations
import hashlib, json
from dataclasses import dataclass, field
from typing import Any, Literal
SCHEMA = "OURSELF_ACTION_INTENT_V1"
DecisionType = Literal["ADMIT", "DENY"]
def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
def stable_id(prefix: str, value: Any) -> str:
    return f"{prefix}-{hashlib.sha256(canonical_json(value).encode()).hexdigest()[:24]}"
@dataclass(frozen=True)
class ActionIntent:
    intent_id: str; instance_id: str; origin: dict[str, Any]; operation: str
    target: dict[str, Any]; arguments: dict[str, Any]; requested_effect: str
    side_effect_class: str; authority_ref: str | None; evidence_required: bool = True
    schema: str = SCHEMA
    @classmethod
    def from_dict(cls, p: dict[str, Any]) -> "ActionIntent":
        if p.get("schema") != SCHEMA: raise ValueError("UNSUPPORTED_SCHEMA")
        req=("intent_id","instance_id","origin","operation","target","arguments","requested_effect","side_effect_class")
        missing=[k for k in req if k not in p]
        if missing: raise ValueError("MISSING_FIELDS:"+",".join(missing))
        if not isinstance(p["origin"],dict) or not isinstance(p["target"],dict): raise ValueError("INVALID_OBJECT_FIELDS")
        if not isinstance(p["arguments"],dict): raise ValueError("INVALID_ARGUMENTS")
        return cls(str(p["intent_id"]),str(p["instance_id"]),p["origin"],str(p["operation"]),p["target"],p["arguments"],
                   str(p["requested_effect"]),str(p["side_effect_class"]),p.get("authority_ref"),bool(p.get("evidence_required",True)))
    def normalized(self) -> dict[str, Any]:
        return {"schema":self.schema,"intent_id":self.intent_id,"instance_id":self.instance_id,"origin":self.origin,
                "operation":self.operation,"target":self.target,"arguments":self.arguments,"requested_effect":self.requested_effect,
                "side_effect_class":self.side_effect_class,"authority_ref":self.authority_ref,"evidence_required":self.evidence_required}
    @property
    def normalized_id(self): return stable_id("NINT", self.normalized())
@dataclass(frozen=True)
class Decision:
    intent_id: str; normalized_id: str; decision: DecisionType
    reason_code: str | None = None; authority_ref: str | None = None
    admission_ref: str | None = None; superbin_ref: str | None = None
    receipt_contract: str | None = None; receipt_ref: str | None = None
    def as_dict(self):
        return {k:v for k,v in self.__dict__.items() if v is not None}
@dataclass(frozen=True)
class Receipt:
    receipt_ref: str; intent_id: str; phase: str; decision: DecisionType
    evidence: dict[str, Any] = field(default_factory=dict); observed_effect: dict[str, Any] | None = None
    def as_dict(self): return self.__dict__.copy()

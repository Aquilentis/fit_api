from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

FinalMode = Literal["auto_allow","user_confirm","admin_flow","blocked"]
ConfirmationLevel = Literal["none","low","medium","high","admin"]
RiskDecision = Literal["allow","user_confirm","admin_only","block"]
ActionCategory = Literal["schedule_change","workout_plan","supplement_add","override"]

class RiskFlag(BaseModel):
    id: str
    domain: str
    code: str
    level: ConfirmationLevel
    source: str
    context: dict = Field(default_factory=dict)
    createdAt: Optional[str] = None

class EvaluateRequest(BaseModel):
    actionCategory: ActionCategory
    actorUserId: str
    householdId: str
    flags: List[RiskFlag] = Field(default_factory=list)

class Decision(BaseModel):
    decisionId: str
    finalMode: FinalMode
    confirmationLevel: ConfirmationLevel
    riskDecision: RiskDecision
    actionCategory: ActionCategory
    actorRole: str = "adult"
    flags: List[dict] = Field(default_factory=list)
    issuedAt: str
    reason: str = "computed"

class OverrideCreate(BaseModel):
    decisionId: str
    requestedBy: str

class Override(BaseModel):
    overrideId: str
    decisionId: str
    requestedBy: str
    state: Literal["user_confirmed","applied","rejected"] = "user_confirmed"
    createdAt: str
    updatedAt: str

class Alert(BaseModel):
    alertId: str
    userId: str
    audience: Literal["user","household_admin","coach","system"] = "user"
    date: str
    severity: Literal["info","warning","critical"] = "warning"
    title: str
    message: str = "mock"
    domain: str
    actionCategory: ActionCategory
    status: Literal["open","resolved"] = "open"
    createdAt: str
    updatedAt: str

class ApprovalRequest(BaseModel):
    approvalId: str
    userId: str
    decisionId: str
    actionCategory: ActionCategory
    state: Literal["pending","approved","rejected"] = "pending"
    createdAt: str
    updatedAt: str

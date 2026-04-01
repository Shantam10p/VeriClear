
from typing import Literal

from pydantic import BaseModel, Field


IntentLabel = Literal["billing", "tech_support", "account_management"]
EmotionLabel = Literal["neutral", "happy", "frustrated", "confused", "threatening"]


class QueryRequest(BaseModel):
    customer_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    channel: Literal["app", "sms", "chat", "ivr"] = "app"


class IntentResult(BaseModel):
    intent: IntentLabel
    emotion: EmotionLabel
    confidence: float
    auto_resolve: bool
    transfer_reason: str | None = None


class BillingData(BaseModel):
    customer_id: str
    plan_name: str
    monthly_plan_cost: float
    previous_total: float
    current_total: float
    activation_fee: float
    prorated_charge: float
    overage_charge: float
    taxes_and_fees: float


class QueryResponse(BaseModel):
    customer_id: str
    channel: str
    intent: IntentLabel
    emotion: EmotionLabel
    confidence: float
    auto_resolve: bool
    response_type: Literal["summary", "transfer"]
    summary: list[str] = []
    transfer_message: str | None = None
    billing_data: BillingData | None = None

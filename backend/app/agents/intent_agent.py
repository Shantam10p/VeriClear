from app.models.schemas import QueryRequest, RouterResult


class IntentAgent:
    def route(self, request: QueryRequest) -> RouterResult:
        message = request.message.lower()

        emotion = "neutral"
        if any(token in message for token in ["thank", "great", "awesome", "glad"]):
            emotion = "happy"
        elif any(token in message for token in ["confused", "don't understand", "dont understand", "what does this mean"]):
            emotion = "confused"
        elif any(token in message for token in ["angry", "ridiculous", "overcharged", "frustrated", "third time"]):
            emotion = "frustrated"
        elif any(token in message for token in ["cancel", "lawsuit", "manager", "complaint", "switching"]):
            emotion = "threatening"

        if any(token in message for token in ["bill", "charge", "charged", "payment", "invoice", "fee", "overage"]):
            intent = "billing"
            confidence = 0.92
        elif any(token in message for token in ["network", "signal", "internet", "phone not working", "technical", "service down"]):
            intent = "tech_support"
            confidence = 0.9
        else:
            intent = "account_management"
            confidence = 0.88

        auto_resolve = intent == "billing" and emotion != "threatening" and confidence >= 0.85
        transfer_reason = None
        if not auto_resolve:
            transfer_reason = "Escalated to human agent for specialized support."

        return RouterResult(
            intent=intent,
            emotion=emotion,
            confidence=confidence,
            auto_resolve=auto_resolve,
            transfer_reason=transfer_reason,
        )

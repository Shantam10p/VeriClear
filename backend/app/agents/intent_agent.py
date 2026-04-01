import json
import os

from app.config import settings
from app.models.schemas import IntentResult, QueryRequest
from app.utils.model_loader import get_intent_model


class IntentAgent:
    def __init__(self) -> None:
        print(
            "[IntentAgent:init]",
            {
                "pid": os.getpid(),
                "use_real_intent_model": settings.use_real_intent_model,
                "use_real_summarizer_model": settings.use_real_summarizer_model,
                "openai_api_key_present": bool(settings.openai_api_key),
                "shared_model_name": settings.shared_model_name,
            },
        )
        self.model = get_intent_model()
        if self.model is None:
            print("[IntentAgent] Real intent model unavailable; heuristic fallback is active.")
        else:
            print(f"[IntentAgent] Real intent model loaded: {settings.shared_model_name}")

    def route(self, request: QueryRequest) -> IntentResult:
        if self.model is not None:
            model_result = self._route_with_model(request)
            if model_result is not None:
                print("[IntentAgent] Using real model result.")
                return model_result

            print("[IntentAgent] Model path returned no usable result; falling back to heuristics.")

        else:
            print("[IntentAgent] Model path skipped because no real model is loaded.")

        print("[IntentAgent] Using heuristic fallback.")
        return self._route_with_heuristics(request)

    def _route_with_model(self, request: QueryRequest) -> IntentResult | None:
        system_prompt = (
            "You are an intent classification service for Verizon-style support queries. "
            "Return only valid JSON with keys intent, emotion, confidence. "
            "intent must be one of billing, tech_support, account_management. "
            "emotion must be one of neutral, happy, frustrated, confused, threatening. "
            "confidence must be a number between 0 and 1. "
            "Do not include any keys other than intent, emotion, confidence. "
            "Billing questions should still be classified as billing even when the customer sounds confused or frustrated. "
            "Tech support and account management should be classified separately from billing."
        )
        user_prompt = (
            f"Channel: {request.channel}\n"
            f"Customer ID: {request.customer_id}\n"
            f"Customer message: {request.message}"
        )

        try:
            response = self.model.chat.completions.create(
                model=settings.shared_model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
                max_tokens=settings.max_new_tokens,
            )
        except Exception as exc:
            print(f"[IntentAgent] Model inference failed: {exc}")
            return None

        content = response.choices[0].message.content if response.choices else ""
        print(f"[IntentAgent] Raw model output: {content}")

        if not content:
            print("[IntentAgent] Model returned empty content.")
            return None

        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            print("[IntentAgent] Model output was not valid JSON.")
            return None

        intent = payload.get("intent")
        emotion = payload.get("emotion")
        confidence = payload.get("confidence")

        if intent not in {"billing", "tech_support", "account_management"}:
            print("[IntentAgent] Model output did not contain a supported intent label.")
            return None

        if emotion not in {"neutral", "happy", "frustrated", "confused", "threatening"}:
            print("[IntentAgent] Model output did not contain a supported emotion label.")
            return None

        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            print("[IntentAgent] Model output confidence was invalid.")
            return None

        auto_resolve = intent == "billing"
        transfer_reason = None if auto_resolve else "Escalated to human agent for specialized support."


        return IntentResult(
            intent=intent,
            emotion=emotion,
            confidence=confidence,
            auto_resolve=auto_resolve,
            transfer_reason=transfer_reason,
        )

    def _route_with_heuristics(self, request: QueryRequest) -> IntentResult:
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

        auto_resolve = intent == "billing"
        transfer_reason = None
        if not auto_resolve:
            transfer_reason = "Escalated to human agent for specialized support."

        return IntentResult(
            intent=intent,
            emotion=emotion,
            confidence=confidence,
            auto_resolve=auto_resolve,
            transfer_reason=transfer_reason,
        )


from app.agents.intent_agent import IntentAgent
from app.agents.summarizer_agent import SummarizerAgent
from app.models.schemas import QueryRequest, QueryResponse
from app.services.billing import get_billing_data


class QueryPipeline:
    def __init__(self) -> None:
        self.intent_agent = IntentAgent()
        self.summarizer_agent = SummarizerAgent()

    def run(self, request: QueryRequest) -> QueryResponse:
        router_result = self.intent_agent.route(request)
        print(
            "[IntentAgent]",
            {
                "customer_id": request.customer_id,
                "intent": router_result.intent,
                "emotion": router_result.emotion,
                "confidence": router_result.confidence,
                "auto_resolve": router_result.auto_resolve,
                "transfer_reason": router_result.transfer_reason,
            },
        )

        if router_result.intent == "billing":
            billing_data = get_billing_data(request.customer_id)
            summary = self.summarizer_agent.summarize(
                billing_data=billing_data,
                emotion=router_result.emotion,
                include_transition=not router_result.auto_resolve,
            )
            return QueryResponse(
                customer_id=request.customer_id,
                intent=router_result.intent,
                emotion=router_result.emotion,
                confidence=router_result.confidence,
                auto_resolve=router_result.auto_resolve,
                response_type="summary" if router_result.auto_resolve else "transfer",
                summary=summary,
                transfer_message=None if router_result.auto_resolve else (router_result.transfer_reason or "I’ve shared the bill breakdown above and will now connect you with a billing specialist for any remaining account-specific help."),
                billing_data=billing_data,
            )

        return QueryResponse(
            customer_id=request.customer_id,
            intent=router_result.intent,
            emotion=router_result.emotion,
            confidence=router_result.confidence,
            auto_resolve=False,
            response_type="transfer",
            transfer_message=router_result.transfer_reason,
        )


pipeline = QueryPipeline()

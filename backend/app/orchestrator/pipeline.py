
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

        if router_result.auto_resolve:
            billing_data = get_billing_data(request.customer_id)
            summary = self.summarizer_agent.summarize(
                billing_data=billing_data,
                emotion=router_result.emotion,
            )
            return QueryResponse(
                customer_id=request.customer_id,
                channel=request.channel,
                intent=router_result.intent,
                emotion=router_result.emotion,
                confidence=router_result.confidence,
                auto_resolve=True,
                response_type="summary",
                summary=summary,
                billing_data=billing_data,
            )

        return QueryResponse(
            customer_id=request.customer_id,
            channel=request.channel,
            intent=router_result.intent,
            emotion=router_result.emotion,
            confidence=router_result.confidence,
            auto_resolve=False,
            response_type="transfer",
            transfer_message=router_result.transfer_reason,
        )


pipeline = QueryPipeline()

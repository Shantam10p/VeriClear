
from app.agents.intent_agent import IntentAgent
from app.agents.summarizer_agent import SummarizerAgent
from app.models.schemas import QueryRequest, QueryResponse
from app.services.billing import get_billing_data


TECH_SUPPORT_CONTEXT = {
    "neutral": [
        "I can see you're reaching out about a technical issue. Let me gather some details so the right specialist can help.",
        "I've noted the issue you described and flagged it for our technical support team. This helps them understand what's happening before they connect with you.",
        "I'm connecting you with a technical specialist now. They'll have the context from this conversation so you won't need to repeat yourself.",
    ],
    "happy": [
        "Thanks for reaching out! I can see this is a technical issue, so let me get you to the right person.",
        "I've captured the details you shared so the tech team has full context when they pick up.",
        "Connecting you with a technical specialist now. They'll be able to jump right in with what you've described.",
    ],
    "confused": [
        "I understand this can be confusing when things aren't working as expected. Let me help get this sorted out.",
        "I've noted what you're experiencing. Technical issues like this are best handled by a specialist who can walk through it with you step by step.",
        "I'm connecting you now with a technical support specialist. They'll have the details from our conversation and can guide you through the next steps clearly.",
    ],
    "frustrated": [
        "I completely understand how frustrating it is when your service isn't working properly, and I'm sorry you're dealing with this.",
        "I've flagged the issue you described and marked it as a priority. Our technical team will have full context from this conversation.",
        "I'm connecting you with a technical specialist right now so this can be resolved as quickly as possible. You won't have to repeat anything.",
    ],
    "threatening": [
        "I hear you, and I understand this has been a serious issue. I want to make sure you get the right support immediately.",
        "I've documented everything you've shared and escalated this with full priority to our technical support team.",
        "I'm connecting you with a senior technical specialist now. They will have all the details and can address your concerns directly.",
    ],
}

ACCOUNT_MGMT_CONTEXT = {
    "neutral": [
        "I can see you need help with an account-related change. Let me connect you with someone who can handle that securely.",
        "Account changes like this require identity verification and specialized access, so I'm routing you to the right team.",
        "I'm connecting you with an account specialist now. They'll have the context from this conversation and can assist you directly.",
    ],
    "happy": [
        "Happy to help! Account changes need to be handled by a specialist with secure access, so let me get you connected.",
        "I've noted what you need, and the account team will have this context ready when they pick up.",
        "Connecting you with an account specialist now. They'll be able to take care of this quickly.",
    ],
    "confused": [
        "I understand account changes can feel confusing, so let me make this easier for you.",
        "What you're asking about requires secure account access, which a specialist can walk you through step by step.",
        "I'm connecting you with an account specialist now. They'll have the details from our conversation and can guide you through the process clearly.",
    ],
    "frustrated": [
        "I'm sorry this has been a frustrating experience. I want to make sure your account issue gets resolved properly.",
        "I've captured everything you've described and flagged it so the account team has full context before they connect with you.",
        "I'm connecting you with an account specialist right now. You won't need to repeat yourself, and they'll be ready to help.",
    ],
    "threatening": [
        "I understand this is a serious concern, and I want to make sure it's handled properly and promptly.",
        "I've documented your request with full detail and escalated it to our account management team as a priority.",
        "I'm connecting you with a senior account specialist now. They will have everything from this conversation and can address your needs directly.",
    ],
}

TRANSFER_MESSAGES = {
    "tech_support": {
        "neutral": "I've shared the details of your issue above and I'm now connecting you with a technical specialist who can help resolve it.",
        "happy": "I've shared your issue details above and I'm connecting you with a technical specialist who can take it from here.",
        "confused": "I've outlined what's happening above to give you some clarity, and I'm now connecting you with a technical specialist who can walk you through the resolution step by step.",
        "frustrated": "I've documented everything above so you don't have to repeat yourself. I'm connecting you with a technical specialist right now to get this resolved.",
        "threatening": "I've escalated your issue with full details above. A senior technical specialist is being connected now to address your concerns directly.",
    },
    "account_management": {
        "neutral": "I've noted your request above and I'm now connecting you with an account specialist who has secure access to make the changes you need.",
        "happy": "I've captured your request above and I'm connecting you with an account specialist who can take care of it.",
        "confused": "I've outlined the situation above to give you some context, and I'm now connecting you with an account specialist who can guide you through the rest.",
        "frustrated": "I've documented everything above so you won't need to repeat yourself. I'm connecting you with an account specialist right now.",
        "threatening": "I've escalated your request with full details above. A senior account specialist is being connected now to handle your concerns directly.",
    },
}


class QueryPipeline:
    def __init__(self) -> None:
        self.intent_agent = IntentAgent()
        self.summarizer_agent = SummarizerAgent()

    def run(self, request: QueryRequest) -> QueryResponse:
        router_result = self.intent_agent.route(request)
        print(
            "[Pipeline]",
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
                transfer_message=None if router_result.auto_resolve else (router_result.transfer_reason or "I've shared the bill breakdown above and will now connect you with a billing specialist for any remaining account-specific help."),
                billing_data=billing_data,
            )

        emotion = router_result.emotion
        if router_result.intent == "tech_support":
            context_map = TECH_SUPPORT_CONTEXT
            transfer_map = TRANSFER_MESSAGES["tech_support"]
        else:
            context_map = ACCOUNT_MGMT_CONTEXT
            transfer_map = TRANSFER_MESSAGES["account_management"]

        summary = context_map.get(emotion, context_map["neutral"])
        transfer_message = transfer_map.get(emotion, transfer_map["neutral"])

        return QueryResponse(
            customer_id=request.customer_id,
            intent=router_result.intent,
            emotion=router_result.emotion,
            confidence=router_result.confidence,
            auto_resolve=False,
            response_type="transfer",
            summary=summary,
            transfer_message=transfer_message,
        )


pipeline = QueryPipeline()

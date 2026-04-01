
import json

from app.config import settings
from app.models.schemas import BillingData
from app.utils.model_loader import get_summarizer_model


class SummarizerAgent:
    def __init__(self) -> None:
        self.model = get_summarizer_model()

    def summarize(self, billing_data: BillingData, emotion: str, include_transition: bool = False) -> list[str]:
        if self.model is not None:
            model_summary = self._summarize_with_model(
                billing_data=billing_data,
                emotion=emotion,
                include_transition=include_transition,
            )
            if model_summary is not None:
                return model_summary

        delta = round(billing_data.current_total - billing_data.previous_total, 2)
        opening = {
            "frustrated": "I understand why this increase feels frustrating, and I’ll keep this as clear and direct as possible.",
            "confused": "I know billing details can be confusing, so I’ll break this down in a simple way.",
            "happy": "I’m glad to help. Here’s a quick and clear breakdown of your latest bill.",
            "neutral": "Here’s a clear breakdown of your latest bill.",
            "threatening": "I want to help de-escalate this and explain the bill clearly while we get you the right support.",
        }.get(emotion, "Here is a quick breakdown of your latest bill.")

        summary = [
            f"{opening} Your current total is ${billing_data.current_total:.2f}, which is ${delta:.2f} higher than last month.",
            f"The main reason for the increase is: {billing_data.primary_increase_reason}",
            f"Your plan is {billing_data.plan_name} at ${billing_data.monthly_plan_cost:.2f} per month. Key details: {' '.join(billing_data.detailed_reasons)} Next best step: {billing_data.recommended_next_step}",
        ]

        if include_transition:
            transition = {
                "frustrated": "I’ve explained the main bill changes here, and I’m also connecting you with a billing specialist so you do not have to repeat everything from scratch.",
                "confused": "I’ve clarified the main bill changes here, and I’ll also connect you with a billing specialist who can walk through any remaining account-specific questions.",
                "happy": "I’ve covered the main bill details here, and if you want deeper account-specific help, I’ll connect you with a billing specialist next.",
                "neutral": "I’ve covered the main bill details here, and I’ll connect you with a billing specialist for any remaining account-specific help.",
                "threatening": "I’ve outlined the key bill details here, and I’m connecting you with a billing specialist now so your remaining concerns can be handled directly and appropriately.",
            }.get(
                emotion,
                "I’ve covered the main bill details here, and I’ll connect you with a billing specialist for any remaining account-specific help.",
            )
            summary[-1] = (
                f"Your bill details show: {' '.join(billing_data.detailed_reasons)} "
                f"{transition}"
            )

        return summary

    def _summarize_with_model(self, billing_data: BillingData, emotion: str, include_transition: bool) -> list[str] | None:
        system_prompt = (
            "You are an empathetic billing support representative. Return only valid JSON with a key named summary that contains exactly 3 short bullet-style strings. "
            "Your job is to explain the bill clearly in plain English, sound calm and human, and adjust tone based on the customer's emotional state. "
            "For frustrated customers, acknowledge frustration without sounding scripted, stay calm, and focus on reassurance plus clarity. "
            "For confused customers, simplify the explanation, avoid jargon, and break down the charges in a very easy-to-follow way. "
            "For happy or neutral customers, be warm, concise, and helpful. "
            "For threatening or escalated customers, stay respectful, de-escalate, do not argue, and clearly state that a specialist will help with the rest if needed. "
            "Do not blame the customer, do not sound robotic, and do not say you cannot help without first explaining what you can clarify from the bill data. "
            "The first bullet should acknowledge the situation in an empathetic tone and explain the total clearly. "
            "The second bullet should directly answer why the bill changed using the provided primary increase reason. "
            "The third bullet should use the detailed reasons and recommended next step to explain what happened and what the customer should expect next, and if a transition is requested, it must also include a polite handoff that says what has been clarified already and that a billing specialist will help with any remaining account-specific issues."
        )
        user_prompt = (
            f"Customer emotion: {emotion}\n"
            f"Include polite transition to CSR: {include_transition}\n"
            f"Billing data: {billing_data.model_dump_json()}"
        )

        try:
            response = self.model.chat.completions.create(
                model=settings.shared_model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=settings.max_new_tokens,
            )
        except Exception as exc:
            print(f"[SummarizerAgent] Model summarization failed: {exc}")
            return None

        content = response.choices[0].message.content if response.choices else ""
        print(f"[SummarizerAgent] Raw model output: {content}")

        if not content:
            return None

        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            return None

        summary = payload.get("summary")
        if not isinstance(summary, list) or len(summary) != 3 or not all(isinstance(item, str) for item in summary):
            return None

        return summary

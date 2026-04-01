
from app.models.schemas import BillingData


class SummarizerAgent:
    def summarize(self, billing_data: BillingData, emotion: str) -> list[str]:
        delta = round(billing_data.current_total - billing_data.previous_total, 2)
        opening = {
            "frustrated": "We understand this bill increase may be frustrating.",
            "confused": "Here is a simpler explanation of your latest bill.",
            "happy": "Here is a quick breakdown of your latest bill.",
            "neutral": "Here is a quick breakdown of your latest bill.",
            "threatening": "Here is a quick breakdown of your latest bill.",
        }.get(emotion, "Here is a quick breakdown of your latest bill.")

        return [
            f"{opening} Your current total is ${billing_data.current_total:.2f}, which is ${delta:.2f} higher than last month.",
            f"Your base plan is {billing_data.plan_name} at ${billing_data.monthly_plan_cost:.2f} per month.",
            f"This month includes ${billing_data.activation_fee:.2f} in activation fees, ${billing_data.prorated_charge:.2f} in prorated charges, and ${billing_data.overage_charge:.2f} in overage charges.",
        ]


from app.models.schemas import BillingData


MOCK_BILLING_DATA: dict[str, BillingData] = {
    "cust_001": BillingData(
        customer_id="cust_001",
        plan_name="Unlimited Plus",
        monthly_plan_cost=65.0,
        previous_total=71.2,
        current_total=126.7,
        activation_fee=35.0,
        prorated_charge=12.0,
        overage_charge=8.5,
        taxes_and_fees=6.2,
    ),
    "cust_002": BillingData(
        customer_id="cust_002",
        plan_name="5G Start",
        monthly_plan_cost=55.0,
        previous_total=58.4,
        current_total=64.1,
        activation_fee=0.0,
        prorated_charge=0.0,
        overage_charge=0.0,
        taxes_and_fees=9.1,
    ),
    "cust_003": BillingData(
        customer_id="cust_003",
        plan_name="Unlimited Welcome",
        monthly_plan_cost=50.0,
        previous_total=52.6,
        current_total=88.6,
        activation_fee=0.0,
        prorated_charge=18.0,
        overage_charge=12.0,
        taxes_and_fees=8.6,
    ),
}


def get_billing_data(customer_id: str) -> BillingData:
    return MOCK_BILLING_DATA.get(
        customer_id,
        BillingData(
            customer_id=customer_id,
            plan_name="Unlimited Plus",
            monthly_plan_cost=65.0,
            previous_total=72.1,
            current_total=84.3,
            activation_fee=0.0,
            prorated_charge=0.0,
            overage_charge=6.0,
            taxes_and_fees=13.3,
        ),
    )

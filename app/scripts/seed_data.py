import asyncio
import random
import sys
import selectors
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from app.db.database import AsyncSessionLocal

from app.modules.customers.models import Customer
from app.modules.interactions.models import Interaction


CUSTOMERS = [
    {
        "name": "Arun Kumar",
        "email": "arun@example.com",
        "phone": "9876543210",
        "company": "AK Technologies",
        "status": "active",
        "profile": "happy",
    },
    {
        "name": "Priya Sharma",
        "email": "priya@example.com",
        "phone": "9876543211",
        "company": "Nova Systems",
        "status": "active",
        "profile": "churn_risk",
    },
    {
        "name": "Rahul Mehta",
        "email": "rahul@example.com",
        "phone": "9876543212",
        "company": "RM Solutions",
        "status": "active",
        "profile": "price_sensitive",
    },
    {
        "name": "Sneha Iyer",
        "email": "sneha@example.com",
        "phone": "9876543213",
        "company": "Pixel Works",
        "status": "active",
        "profile": "purchase_ready",
    },
    {
        "name": "Vikram Rao",
        "email": "vikram@example.com",
        "phone": "9876543214",
        "company": "VR Industries",
        "status": "active",
        "profile": "support_heavy",
    },
    {
        "name": "Neha Kapoor",
        "email": "neha@example.com",
        "phone": "9876543215",
        "company": "NK Digital",
        "status": "active",
        "profile": "happy",
    },
    {
        "name": "Karthik Nair",
        "email": "karthik@example.com",
        "phone": "9876543216",
        "company": "KN Retail",
        "status": "active",
        "profile": "repeated_complaint",
    },
    {
        "name": "Divya Menon",
        "email": "divya@example.com",
        "phone": "9876543217",
        "company": "DM Consulting",
        "status": "active",
        "profile": "new_lead",
    },
    {
        "name": "Sanjay Patel",
        "email": "sanjay@example.com",
        "phone": "9876543218",
        "company": "SP Enterprises",
        "status": "active",
        "profile": "high_value",
    },
    {
        "name": "Anjali Singh",
        "email": "anjali@example.com",
        "phone": "9876543219",
        "company": "AS Services",
        "status": "inactive",
        "profile": "inactive",
    },
    {
        "name": "Rohit Verma",
        "email": "rohit@example.com",
        "phone": "9876543220",
        "company": "RV Labs",
        "status": "active",
        "profile": "purchase_ready",
    },
    {
        "name": "Meera Krishnan",
        "email": "meera@example.com",
        "phone": "9876543221",
        "company": "MK Solutions",
        "status": "active",
        "profile": "positive_feedback",
    },
    {
        "name": "Aditya Jain",
        "email": "aditya@example.com",
        "phone": "9876543222",
        "company": "AJ Commerce",
        "status": "active",
        "profile": "price_sensitive",
    },
    {
        "name": "Pooja Reddy",
        "email": "pooja@example.com",
        "phone": "9876543223",
        "company": "PR Technologies",
        "status": "active",
        "profile": "new_lead",
    },
    {
        "name": "Naveen Raj",
        "email": "naveen@example.com",
        "phone": "9876543224",
        "company": "NR Systems",
        "status": "active",
        "profile": "churn_risk",
    },
]


PROFILE_MESSAGES = {

    "happy": [
        (
            "enquiry",
            "inbound",
            "whatsapp",
            "Can you explain the difference between the standard and premium plans?",
        ),
        (
            "follow_up",
            "outbound",
            "email",
            "Sharing the plan comparison and pricing details you requested.",
        ),
        (
            "purchase",
            "inbound",
            "whatsapp",
            "Premium looks good. Please send me the payment link.",
        ),
        (
            "follow_up",
            "outbound",
            "email",
            "Your premium subscription has been activated successfully.",
        ),
        (
            "feedback",
            "inbound",
            "email",
            "Everything is working well. The onboarding was very smooth.",
        ),
    ],

    "churn_risk": [
        (
            "support",
            "inbound",
            "whatsapp",
            "My account is not working properly since yesterday.",
        ),
        (
            "follow_up",
            "outbound",
            "email",
            "Our support team is checking the issue.",
        ),
        (
            "complaint",
            "inbound",
            "whatsapp",
            "It is still not fixed. I already contacted support yesterday.",
        ),
        (
            "complaint",
            "inbound",
            "call",
            "This is the third time I am contacting you about the same issue.",
        ),
        (
            "complaint",
            "inbound",
            "email",
            "If this isn't resolved soon I will cancel my subscription.",
        ),
    ],

    "price_sensitive": [
        (
            "enquiry",
            "inbound",
            "whatsapp",
            "What is the monthly price?",
        ),
        (
            "enquiry",
            "inbound",
            "email",
            "Do you provide any discount for annual payment?",
        ),
        (
            "follow_up",
            "outbound",
            "email",
            "We currently provide a discount on annual subscriptions.",
        ),
        (
            "enquiry",
            "inbound",
            "whatsapp",
            "The price is still slightly high. Is there a cheaper plan?",
        ),
        (
            "follow_up",
            "outbound",
            "whatsapp",
            "We can help you compare the available plans.",
        ),
    ],

    "purchase_ready": [
        (
            "enquiry",
            "inbound",
            "web",
            "Does the premium plan include all features?",
        ),
        (
            "enquiry",
            "inbound",
            "whatsapp",
            "Can I start immediately after payment?",
        ),
        (
            "follow_up",
            "outbound",
            "whatsapp",
            "Yes, your account can be activated immediately.",
        ),
        (
            "purchase",
            "inbound",
            "whatsapp",
            "Great. Send me the payment link. I want to purchase today.",
        ),
    ],

    "support_heavy": [
        (
            "support",
            "inbound",
            "email",
            "I cannot log into my account.",
        ),
        (
            "follow_up",
            "outbound",
            "email",
            "We have sent a password reset link.",
        ),
        (
            "support",
            "inbound",
            "whatsapp",
            "I reset the password but now the dashboard isn't loading.",
        ),
        (
            "support",
            "inbound",
            "call",
            "Can someone help me configure the dashboard?",
        ),
        (
            "follow_up",
            "outbound",
            "email",
            "Our technical team has shared the setup instructions.",
        ),
    ],

    "repeated_complaint": [
        (
            "complaint",
            "inbound",
            "email",
            "My invoice amount is incorrect.",
        ),
        (
            "follow_up",
            "outbound",
            "email",
            "We are reviewing your invoice.",
        ),
        (
            "complaint",
            "inbound",
            "whatsapp",
            "The invoice is still incorrect.",
        ),
        (
            "complaint",
            "inbound",
            "call",
            "Why do I have to contact you repeatedly for the same billing issue?",
        ),
        (
            "complaint",
            "inbound",
            "email",
            "Please escalate this. I need the corrected invoice today.",
        ),
    ],

    "new_lead": [
        (
            "enquiry",
            "inbound",
            "web",
            "I would like to know more about your product.",
        ),
        (
            "follow_up",
            "outbound",
            "email",
            "Thanks for your interest. Here is an overview of our plans.",
        ),
        (
            "enquiry",
            "inbound",
            "email",
            "Can we arrange a demo next week?",
        ),
    ],

    "high_value": [
        (
            "enquiry",
            "inbound",
            "email",
            "We need accounts for approximately 100 employees.",
        ),
        (
            "follow_up",
            "outbound",
            "email",
            "We can prepare an enterprise proposal for your team.",
        ),
        (
            "enquiry",
            "inbound",
            "call",
            "We need SSO, priority support and consolidated billing.",
        ),
        (
            "purchase",
            "inbound",
            "email",
            "The proposal looks good. Please send the agreement.",
        ),
        (
            "follow_up",
            "outbound",
            "email",
            "The enterprise agreement has been sent for review.",
        ),
    ],

    "inactive": [
        (
            "purchase",
            "inbound",
            "web",
            "I have completed the purchase.",
        ),
        (
            "follow_up",
            "outbound",
            "email",
            "Welcome. Your account has been activated.",
        ),
        (
            "follow_up",
            "outbound",
            "email",
            "We noticed you haven't used your account recently. Do you need help?",
        ),
    ],

    "positive_feedback": [
        (
            "purchase",
            "inbound",
            "web",
            "I purchased the annual plan.",
        ),
        (
            "support",
            "inbound",
            "whatsapp",
            "I need help importing my existing data.",
        ),
        (
            "follow_up",
            "outbound",
            "whatsapp",
            "Our team has completed the data import.",
        ),
        (
            "feedback",
            "inbound",
            "email",
            "Excellent support. The migration was much easier than expected.",
        ),
    ],
}


async def seed_database():

    async with AsyncSessionLocal() as db:

        # Development only:
        # clear interactions before customers because of FK.
        await db.execute(
            delete(Interaction)
        )

        await db.execute(
            delete(Customer)
        )

        await db.commit()

        now = datetime.now(timezone.utc)

        interaction_count = 0

        for index, customer_data in enumerate(
            CUSTOMERS
        ):
            profile = customer_data.pop(
                "profile"
            )

            customer = Customer(
                **customer_data
            )

            db.add(customer)

            await db.flush()

            messages = PROFILE_MESSAGES[
                profile
            ]

            # Repeat the profile with small variations
            # so each customer has more history.
            repeated_messages = (
                messages
                + random.sample(
                    messages,
                    min(
                        len(messages),
                        3,
                    ),
                )
            )

            for message_index, (
                interaction_type,
                direction,
                channel,
                content,
            ) in enumerate(
                repeated_messages
            ):

                days_ago = (
                    45
                    - index
                    - message_index * 3
                )

                interaction = Interaction(
                    customer_id=customer.id,
                    channel=channel,
                    direction=direction,
                    interaction_type=interaction_type,
                    content=content,
                    occurred_at=(
                        now
                        - timedelta(
                            days=max(
                                days_ago,
                                0,
                            )
                        )
                    ),
                )

                db.add(interaction)

                interaction_count += 1

        await db.commit()

        print(
            f"Seed complete: "
            f"{len(CUSTOMERS)} customers, "
            f"{interaction_count} interactions"
        )


if __name__ == "__main__":

    if sys.platform == "win32":
        asyncio.run(
            seed_database(),
            loop_factory=lambda: asyncio.SelectorEventLoop(
                selectors.SelectSelector()
            ),
        )
    else:
        asyncio.run(
            seed_database()
        )
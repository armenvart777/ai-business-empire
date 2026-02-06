"""
Sales Email Sequences - sales-focused email automation.

Trial conversion, demo follow-up, re-engagement.
"""

import logging
from typing import Dict, Any, List
import json
import re


logger = logging.getLogger(__name__)


class SalesEmailSequences:
    """
    Генератор sales email sequences.

    Отличается от marketing emails:
    - Более direct sales focus
    - Короче и to-the-point
    - Clear CTAs (trial, demo, buy)
    - Objection handling
    - Urgency/FOMO
    """

    def __init__(self, llm):
        """
        Args:
            llm: LLM instance
        """
        self.llm = llm

    async def create_trial_to_paid_sequence(
        self,
        business_idea: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Создать sequence для конверсии trial → paid.

        Returns:
            Dict with email sequence
        """
        prompt = f"""
Create a 7-email sequence to convert free trial users to paid customers.

Business: {business_idea['name']}
Description: {business_idea['description']}
Pricing: {business_idea.get('pricing', 'Freemium')}

Trial duration: 14 days

Emails should:
1. Day 0: Welcome, quick start
2. Day 2: Highlight key feature #1
3. Day 5: Highlight key feature #2, show value
4. Day 8: Share customer success story
5. Day 11: Urgency - trial ending soon, upgrade now
6. Day 13: LAST CHANCE - trial ends tomorrow
7. Day 15: Trial expired - special offer to comeback

Each email should:
- Be short (under 150 words)
- Have ONE clear CTA
- Focus on value, not features
- Handle potential objections

Return as JSON:
{{
    "sequence_name": "Trial to Paid Conversion",
    "sequence_type": "conversion",
    "trigger": "User starts free trial",
    "emails": [
        {{
            "email_number": 1,
            "send_day": 0,
            "subject_line": "...",
            "preview_text": "...",
            "email_body": "...",
            "cta_text": "...",
            "cta_url": "/upgrade"
        }}
    ]
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.7,
            max_tokens=3000
        )

        sequence = self._parse_json_response(response)

        logger.info(f"Created trial→paid sequence with {len(sequence.get('emails', []))} emails")

        return sequence

    async def create_demo_followup_sequence(
        self,
        business_idea: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Создать sequence после demo call.

        Returns:
            Dict with email sequence
        """
        prompt = f"""
Create a 5-email follow-up sequence after a demo call.

Business: {business_idea['name']}
Description: {business_idea['description']}

Emails should:
1. Day 0 (1 hour after demo): Thank you, recap key points
2. Day 1: Answer common questions, share resources
3. Day 3: Check-in, offer to answer questions
4. Day 5: Case study similar to their use case
5. Day 7: Time-limited offer to close the deal

Return as JSON:
{{
    "sequence_name": "Demo Follow-Up",
    "sequence_type": "sales",
    "trigger": "Demo call completed",
    "emails": [
        {{
            "email_number": 1,
            "send_day": 0,
            "subject_line": "...",
            "preview_text": "...",
            "email_body": "...",
            "cta_text": "...",
            "cta_url": "..."
        }}
    ]
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.7,
            max_tokens=2500
        )

        return self._parse_json_response(response)

    async def create_reengagement_sequence(
        self,
        business_idea: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Создать re-engagement sequence для churned users.

        Returns:
            Dict with email sequence
        """
        prompt = f"""
Create a 4-email re-engagement sequence for churned customers.

Business: {business_idea['name']}
Description: {business_idea['description']}

Goal: Win back churned customers

Emails should:
1. Day 0 (30 days after churn): We miss you, what went wrong?
2. Day 7: Show what's new/improved since they left
3. Day 14: Special comeback offer (discount)
4. Day 30: Last chance, then we'll stop bothering you

Tone: Humble, understanding, show you've improved

Return as JSON:
{{
    "sequence_name": "Win-Back Sequence",
    "sequence_type": "reengagement",
    "trigger": "Subscription cancelled 30+ days ago",
    "emails": [
        {{
            "email_number": 1,
            "send_day": 0,
            "subject_line": "...",
            "preview_text": "...",
            "email_body": "...",
            "cta_text": "...",
            "cta_url": "...",
            "special_offer": "20% off for 3 months"
        }}
    ]
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.7,
            max_tokens=2500
        )

        return self._parse_json_response(response)

    async def create_cold_outreach_sequence(
        self,
        business_idea: Dict[str, Any],
        target_segment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Создать cold outreach sequence (опционально).

        Args:
            business_idea: Информация о бизнесе
            target_segment: Целевой сегмент

        Returns:
            Dict with email sequence
        """
        prompt = f"""
Create a 3-email cold outreach sequence.

Business: {business_idea['name']}
Description: {business_idea['description']}
Target: {target_segment.get('name', 'Decision makers')}

IMPORTANT: Cold outreach rules:
- Highly personalized (mention their company/role)
- Lead with value, not features
- NO SPAM - provide opt-out
- Short (under 100 words)

Emails:
1. Day 0: Initial outreach - quick value prop
2. Day 3: Follow-up - share relevant resource
3. Day 7: Final follow-up - ask if not interested

Return as JSON:
{{
    "sequence_name": "Cold Outreach",
    "sequence_type": "outbound",
    "trigger": "Manual trigger for cold prospects",
    "emails": [
        {{
            "email_number": 1,
            "send_day": 0,
            "subject_line": "...",
            "preview_text": "...",
            "email_body": "...",
            "personalization_fields": ["company_name", "role"],
            "cta_text": "...",
            "cta_url": "..."
        }}
    ],
    "compliance_notes": "Include opt-out link, CAN-SPAM compliant"
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.7,
            max_tokens=2000
        )

        return self._parse_json_response(response)

    async def create_upgrade_sequence(
        self,
        business_idea: Dict[str, Any],
        current_plan: str = "basic",
        target_plan: str = "pro"
    ) -> Dict[str, Any]:
        """
        Создать sequence для upgrade (basic → pro).

        Returns:
            Dict with email sequence
        """
        prompt = f"""
Create a 3-email sequence to upgrade users from {current_plan} to {target_plan}.

Business: {business_idea['name']}
Current Plan: {current_plan}
Target Plan: {target_plan}

Emails should:
1. Day 0: Highlight pro features they're missing
2. Day 3: Show ROI calculation (how pro pays for itself)
3. Day 7: Limited-time upgrade discount

Return as JSON:
{{
    "sequence_name": "Upgrade {current_plan} → {target_plan}",
    "sequence_type": "upgrade",
    "trigger": "User on {current_plan} for 30+ days",
    "emails": [
        {{
            "email_number": 1,
            "send_day": 0,
            "subject_line": "...",
            "preview_text": "...",
            "email_body": "...",
            "cta_text": "Upgrade Now",
            "cta_url": "/upgrade"
        }}
    ]
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.7,
            max_tokens=2000
        )

        return self._parse_json_response(response)

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        json_str = re.sub(r'^```(?:json)?\n', '', response.strip())
        json_str = re.sub(r'\n```$', '', json_str)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {
                "sequence_name": "Default Sequence",
                "emails": []
            }


# Пример использования
if __name__ == "__main__":
    import asyncio
    from agents.base.mock_llm import MockLLM

    async def main():
        llm = MockLLM()
        sequences = SalesEmailSequences(llm=llm)

        business_idea = {
            "name": "TaskFlow AI",
            "description": "AI-powered PM tool for small teams",
            "pricing": "Free + $19/month Pro"
        }

        # Trial → Paid sequence
        trial_sequence = await sequences.create_trial_to_paid_sequence(business_idea)

        print(f"Trial→Paid Sequence:")
        print(f"  - Emails: {len(trial_sequence.get('emails', []))}")

        # Demo follow-up
        demo_sequence = await sequences.create_demo_followup_sequence(business_idea)

        print(f"\nDemo Follow-up Sequence:")
        print(f"  - Emails: {len(demo_sequence.get('emails', []))}")

        # Re-engagement
        reengagement = await sequences.create_reengagement_sequence(business_idea)

        print(f"\nWin-Back Sequence:")
        print(f"  - Emails: {len(reengagement.get('emails', []))}")

    asyncio.run(main())

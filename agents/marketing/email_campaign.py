"""
Email Campaign Manager - управление email маркетингом.

Email sequences, automation, personalization.
"""

import logging
from typing import Dict, Any, List
import json
import re


logger = logging.getLogger(__name__)


class EmailCampaignManager:
    """
    Менеджер email кампаний.

    Поддерживает:
    - Welcome email sequence
    - Nurture campaigns
    - Promotional emails
    - Abandoned cart recovery
    - Re-engagement campaigns
    """

    def __init__(self, llm):
        """
        Args:
            llm: LLM instance
        """
        self.llm = llm

    async def create_campaigns(
        self,
        business_idea: Dict[str, Any],
        audience_segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Создать email кампании для всех сегментов.

        Args:
            business_idea: Информация о бизнесе
            audience_segments: Сегменты аудитории

        Returns:
            List of email campaign objects
        """
        campaigns = []

        # 1. Welcome sequence (для всех)
        welcome_campaign = await self._create_welcome_sequence(business_idea)
        campaigns.append(welcome_campaign)

        # 2. Nurture campaign (для каждого сегмента)
        for segment in audience_segments[:2]:  # Top 2 segments
            nurture_campaign = await self._create_nurture_campaign(
                business_idea,
                segment
            )
            campaigns.append(nurture_campaign)

        # 3. Conversion campaign
        conversion_campaign = await self._create_conversion_campaign(business_idea)
        campaigns.append(conversion_campaign)

        logger.info(f"Created {len(campaigns)} email campaigns")

        return campaigns

    async def _create_welcome_sequence(
        self,
        business_idea: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Создать welcome email sequence.

        Returns:
            Dict with welcome campaign
        """
        prompt = f"""
Create a 5-email welcome sequence for new signups.

Business: {business_idea['name']}
Description: {business_idea['description']}
Key Features: {', '.join(business_idea.get('key_features', []))}

Emails should:
1. Email 1 (Day 0): Welcome, confirm signup, quick start guide
2. Email 2 (Day 1): Introduce core features, tips for success
3. Email 3 (Day 3): Share use case/success story
4. Email 4 (Day 5): Highlight key feature, encourage action
5. Email 5 (Day 7): Upgrade to paid plan (if freemium)

For each email provide:
- Subject line (45 chars max)
- Preview text
- Content summary
- CTA
- Delay (days after signup)

Return as JSON:
{{
    "campaign_name": "Welcome Sequence",
    "campaign_type": "welcome",
    "emails": [
        {{
            "sequence_number": 1,
            "delay_days": 0,
            "subject_line": "...",
            "preview_text": "...",
            "content_summary": "...",
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

        campaign = self._parse_json_response(response)

        logger.info(f"Created welcome sequence with {len(campaign.get('emails', []))} emails")

        return campaign

    async def _create_nurture_campaign(
        self,
        business_idea: Dict[str, Any],
        audience_segment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Создать nurture campaign для сегмента.

        Args:
            business_idea: Информация о бизнесе
            audience_segment: Сегмент аудитории

        Returns:
            Dict with nurture campaign
        """
        segment_name = audience_segment.get("name", "General")
        segment_pain_points = audience_segment.get("pain_points", [])

        prompt = f"""
Create a 4-email nurture campaign for this audience segment.

Business: {business_idea['name']}
Segment: {segment_name}
Pain Points: {', '.join(segment_pain_points) if segment_pain_points else 'General'}

Emails should:
1. Email 1: Educational content addressing pain point
2. Email 2: Tips & tricks for getting more value
3. Email 3: Case study or testimonial
4. Email 4: Gentle push towards conversion

Return as JSON:
{{
    "campaign_name": "Nurture - {segment_name}",
    "campaign_type": "nurture",
    "target_segment": "{segment_name}",
    "emails": [
        {{
            "sequence_number": 1,
            "delay_days": 2,
            "subject_line": "...",
            "preview_text": "...",
            "content_summary": "...",
            "cta_text": "...",
            "cta_url": "..."
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

    async def _create_conversion_campaign(
        self,
        business_idea: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Создать conversion campaign (free → paid).

        Returns:
            Dict with conversion campaign
        """
        prompt = f"""
Create a 3-email conversion campaign to upgrade free users.

Business: {business_idea['name']}
Pricing: {business_idea.get('pricing', 'Freemium')}

Emails should:
1. Email 1: Highlight pro features, show value
2. Email 2: Limited-time offer (20% discount)
3. Email 3: Last chance, FOMO

Return as JSON:
{{
    "campaign_name": "Free to Paid Conversion",
    "campaign_type": "conversion",
    "trigger": "User active for 14+ days on free plan",
    "emails": [
        {{
            "sequence_number": 1,
            "delay_days": 0,
            "subject_line": "...",
            "preview_text": "...",
            "content_summary": "...",
            "cta_text": "...",
            "cta_url": "...",
            "offer": "20% off first month"
        }}
    ]
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.7,
            max_tokens=1500
        )

        return self._parse_json_response(response)

    async def create_one_off_email(
        self,
        business_idea: Dict[str, Any],
        email_type: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Создать разовый email (announcement, promotion, etc).

        Args:
            business_idea: Информация о бизнесе
            email_type: Тип (announcement/promotion/update/survey)
            context: Дополнительный контекст

        Returns:
            Dict with email
        """
        context = context or {}

        prompt = f"""
Create a {email_type} email.

Business: {business_idea['name']}
Context: {context.get('message', 'New feature launch')}

Return as JSON:
{{
    "subject_line": "...",
    "preview_text": "...",
    "content_summary": "...",
    "cta_text": "...",
    "cta_url": "...",
    "send_time": "suggested send time"
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.7,
            max_tokens=1000
        )

        email = self._parse_json_response(response)
        email["email_type"] = email_type

        return email

    def calculate_campaign_metrics(
        self,
        campaign: Dict[str, Any],
        performance_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Рассчитать метрики кампании.

        Args:
            campaign: Campaign object
            performance_data: Actual performance data (optional)

        Returns:
            Dict with campaign metrics
        """
        # Mock implementation
        # В реальности: данные из email provider API (SendGrid, Mailchimp, etc)

        num_emails = len(campaign.get("emails", []))

        # Estimated metrics (industry averages для SaaS)
        estimated = {
            "total_emails": num_emails,
            "estimated_open_rate": 0.22,  # 22%
            "estimated_click_rate": 0.035,  # 3.5%
            "estimated_conversion_rate": 0.02,  # 2%
            "estimated_unsubscribe_rate": 0.001  # 0.1%
        }

        if performance_data:
            # Actual data overrides estimates
            estimated.update(performance_data)

        return estimated

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        json_str = re.sub(r'^```(?:json)?\n', '', response.strip())
        json_str = re.sub(r'\n```$', '', json_str)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {
                "campaign_name": "Default Campaign",
                "emails": []
            }


# Пример использования
if __name__ == "__main__":
    import asyncio
    from agents.base.mock_llm import MockLLM

    async def main():
        llm = MockLLM()
        email_manager = EmailCampaignManager(llm=llm)

        business_idea = {
            "name": "TaskFlow AI",
            "description": "AI-powered PM tool for small teams",
            "key_features": [
                "AI task prioritization",
                "Automatic deadline prediction"
            ],
            "pricing": "Free + $19/month Pro"
        }

        # Create campaigns
        campaigns = await email_manager.create_campaigns(
            business_idea=business_idea,
            audience_segments=[
                {
                    "name": "Freelancers",
                    "pain_points": ["Time management", "Client communication"]
                }
            ]
        )

        print(f"Created {len(campaigns)} campaigns:")
        for campaign in campaigns:
            name = campaign.get("campaign_name", "Unknown")
            emails = len(campaign.get("emails", []))
            print(f"  - {name}: {emails} emails")

    asyncio.run(main())

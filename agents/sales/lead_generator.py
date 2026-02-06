"""
Lead Generator - генерация и квалификация лидов.

Lead magnets, lead scoring, qualification criteria.
"""

import logging
from typing import Dict, Any, List
import json
import re


logger = logging.getLogger(__name__)


class LeadGenerator:
    """
    Генератор и квалификатор лидов.

    Функции:
    - Lead magnet creation
    - Lead capture forms
    - Lead scoring models
    - Lead qualification criteria
    - Lead nurture strategies
    """

    def __init__(self, llm):
        """
        Args:
            llm: LLM instance
        """
        self.llm = llm

    async def create_lead_strategy(
        self,
        business_idea: Dict[str, Any],
        funnel: Dict[str, Any],
        target_mrr: int
    ) -> Dict[str, Any]:
        """
        Создать lead generation стратегию.

        Args:
            business_idea: Информация о бизнесе
            funnel: Sales funnel
            target_mrr: Target MRR

        Returns:
            Dict с lead generation стратегией
        """
        # 1. Lead magnets
        lead_magnets = await self._create_lead_magnets(business_idea)

        # 2. Lead capture forms
        capture_forms = await self._design_capture_forms(business_idea)

        # 3. Lead scoring model
        scoring_model = await self._create_lead_scoring_model(business_idea)

        # 4. Qualification criteria
        qualification_criteria = await self._define_qualification_criteria(
            business_idea
        )

        # 5. Рассчитываем target leads
        conversion_rate = funnel.get("estimated_overall_conversion", 0.02)
        avg_price = self._extract_price(business_idea.get("pricing", "$19"))
        customers_needed = int(target_mrr / avg_price)
        leads_needed = int(customers_needed / conversion_rate) if conversion_rate > 0 else 1000

        return {
            "lead_magnets": lead_magnets,
            "capture_forms": capture_forms,
            "scoring_model": scoring_model,
            "qualification_criteria": qualification_criteria,
            "targets": {
                "monthly_leads_needed": leads_needed,
                "conversion_rate": conversion_rate,
                "customers_needed": customers_needed,
                "target_mrr": target_mrr
            }
        }

    async def _create_lead_magnets(
        self,
        business_idea: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Создать lead magnets.

        Returns:
            List of lead magnet ideas
        """
        prompt = f"""
Create 5 compelling lead magnets for this SaaS business.

Business: {business_idea['name']}
Description: {business_idea['description']}
Target Audience: {business_idea.get('target_audience', 'Small teams')}

Lead magnets should:
1. Provide immediate value
2. Be relevant to target audience pain points
3. Position the product as solution
4. Be quick to consume (or implement)
5. Build trust and authority

Types to consider:
- Checklists / templates
- Ebooks / guides
- Video tutorials
- Free tools / calculators
- Webinars
- Case studies

Return as JSON:
{{
    "lead_magnets": [
        {{
            "name": "Lead magnet name",
            "type": "checklist/ebook/tool/webinar/etc",
            "description": "What it provides",
            "target_audience": "Who it's for",
            "value_proposition": "Why they should download it",
            "effort_to_create": "low/medium/high",
            "expected_conversion_rate": 0.15
        }}
    ]
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.7,
            max_tokens=2000
        )

        result = self._parse_json_response(response)

        logger.info(f"Created {len(result.get('lead_magnets', []))} lead magnets")

        return result.get("lead_magnets", [])

    async def _design_capture_forms(
        self,
        business_idea: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Дизайн lead capture forms.

        Returns:
            List of form configurations
        """
        forms = [
            {
                "form_name": "Homepage Signup",
                "placement": "Homepage hero section",
                "fields": [
                    {
                        "name": "email",
                        "type": "email",
                        "required": True,
                        "placeholder": "your@email.com"
                    }
                ],
                "submit_button": "Start Free Trial",
                "privacy_note": "No credit card required. 14-day free trial.",
                "expected_conversion_rate": 0.03
            },
            {
                "form_name": "Lead Magnet Download",
                "placement": "Lead magnet landing page",
                "fields": [
                    {
                        "name": "email",
                        "type": "email",
                        "required": True
                    },
                    {
                        "name": "company",
                        "type": "text",
                        "required": False
                    }
                ],
                "submit_button": "Download Now",
                "expected_conversion_rate": 0.25
            },
            {
                "form_name": "Demo Request",
                "placement": "/demo page",
                "fields": [
                    {
                        "name": "email",
                        "type": "email",
                        "required": True
                    },
                    {
                        "name": "company",
                        "type": "text",
                        "required": True
                    },
                    {
                        "name": "team_size",
                        "type": "select",
                        "options": ["1-5", "6-20", "21-50", "51+"],
                        "required": True
                    }
                ],
                "submit_button": "Request Demo",
                "expected_conversion_rate": 0.10
            }
        ]

        return forms

    async def _create_lead_scoring_model(
        self,
        business_idea: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Создать lead scoring model.

        Returns:
            Dict с критериями и весами
        """
        return {
            "scoring_criteria": [
                {
                    "criterion": "Company Size",
                    "weight": 20,
                    "scores": {
                        "1-5 employees": 5,
                        "6-20 employees": 15,
                        "21-50 employees": 20,
                        "51+ employees": 10
                    }
                },
                {
                    "criterion": "Industry",
                    "weight": 15,
                    "scores": {
                        "target_industry": 15,
                        "related_industry": 10,
                        "other": 5
                    }
                },
                {
                    "criterion": "Engagement Level",
                    "weight": 30,
                    "scores": {
                        "visited_pricing_page": 10,
                        "watched_demo_video": 8,
                        "downloaded_lead_magnet": 7,
                        "opened_emails": 5
                    }
                },
                {
                    "criterion": "Role/Title",
                    "weight": 20,
                    "scores": {
                        "decision_maker": 20,
                        "influencer": 15,
                        "end_user": 10
                    }
                },
                {
                    "criterion": "Budget Indicator",
                    "weight": 15,
                    "scores": {
                        "asked_about_enterprise": 15,
                        "asked_about_pricing": 10,
                        "mentioned_budget": 12
                    }
                }
            ],
            "score_ranges": {
                "hot": {"min": 70, "max": 100, "action": "Immediate sales contact"},
                "warm": {"min": 40, "max": 69, "action": "Nurture sequence"},
                "cold": {"min": 0, "max": 39, "action": "Educational content"}
            }
        }

    async def _define_qualification_criteria(
        self,
        business_idea: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Определить qualification criteria (BANT/MEDDIC).

        Returns:
            Dict с qualification framework
        """
        return {
            "framework": "BANT",
            "criteria": {
                "Budget": {
                    "question": "What's your budget for this type of solution?",
                    "qualifying_answer": f"At least {business_idea.get('pricing', '$19/month')}",
                    "disqualifying_answer": "No budget allocated"
                },
                "Authority": {
                    "question": "Are you the decision-maker for this purchase?",
                    "qualifying_answer": "Yes / Part of decision team",
                    "disqualifying_answer": "Just researching, no decision power"
                },
                "Need": {
                    "question": "What problem are you trying to solve?",
                    "qualifying_answer": f"Matches {business_idea['description']}",
                    "disqualifying_answer": "No clear need or pain point"
                },
                "Timeline": {
                    "question": "When are you looking to implement a solution?",
                    "qualifying_answer": "Within 3 months",
                    "disqualifying_answer": "Just exploring, no timeline"
                }
            },
            "minimum_criteria_to_qualify": 3
        }

    def calculate_lead_score(
        self,
        lead_data: Dict[str, Any],
        scoring_model: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Рассчитать score для лида.

        Args:
            lead_data: Данные о лиде
            scoring_model: Scoring model

        Returns:
            Dict с score и classification
        """
        total_score = 0
        max_score = 100

        criteria = scoring_model.get("scoring_criteria", [])

        for criterion in criteria:
            weight = criterion.get("weight", 0)
            scores = criterion.get("scores", {})

            # Найти matching score
            criterion_value = lead_data.get(criterion["criterion"].lower().replace(" ", "_"), "")

            if criterion_value in scores:
                total_score += scores[criterion_value]
            else:
                # Default score (половина от веса)
                total_score += weight // 2

        # Classification
        score_ranges = scoring_model.get("score_ranges", {})
        classification = "cold"

        for category, range_data in score_ranges.items():
            if range_data["min"] <= total_score <= range_data["max"]:
                classification = category
                break

        return {
            "lead_score": total_score,
            "max_score": max_score,
            "classification": classification,
            "recommended_action": score_ranges.get(classification, {}).get("action", "")
        }

    def _extract_price(self, pricing_str: str) -> int:
        """
        Извлечь числовую цену из строки.

        Args:
            pricing_str: Pricing string (e.g. "Free + $19/month Pro")

        Returns:
            int: Price в долларах
        """
        # Найти первое число после $
        match = re.search(r'\$(\d+)', pricing_str)

        if match:
            return int(match.group(1))

        return 19  # Default

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        json_str = re.sub(r'^```(?:json)?\n', '', response.strip())
        json_str = re.sub(r'\n```$', '', json_str)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {}


# Пример использования
if __name__ == "__main__":
    import asyncio
    from agents.base.mock_llm import MockLLM

    async def main():
        llm = MockLLM()
        generator = LeadGenerator(llm=llm)

        business_idea = {
            "name": "TaskFlow AI",
            "description": "AI-powered PM tool for small teams",
            "target_audience": "Freelancers and teams of 2-10",
            "pricing": "Free + $19/month Pro"
        }

        funnel = {
            "estimated_overall_conversion": 0.025
        }

        # Create lead strategy
        strategy = await generator.create_lead_strategy(
            business_idea=business_idea,
            funnel=funnel,
            target_mrr=5000
        )

        print(f"Lead Strategy:")
        print(f"  - Lead magnets: {len(strategy['lead_magnets'])}")
        print(f"  - Capture forms: {len(strategy['capture_forms'])}")
        print(f"  - Monthly leads needed: {strategy['targets']['monthly_leads_needed']}")

        # Calculate lead score (example)
        lead_data = {
            "company_size": "6-20 employees",
            "engagement_level": "visited_pricing_page"
        }

        score_result = generator.calculate_lead_score(
            lead_data,
            strategy["scoring_model"]
        )

        print(f"\nLead Score: {score_result['lead_score']}/100 ({score_result['classification']})")

    asyncio.run(main())

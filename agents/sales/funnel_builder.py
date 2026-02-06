"""
Funnel Builder - проектирование sales funnels.

Создание и оптимизация воронок продаж.
"""

import logging
from typing import Dict, Any, List
import json
import re


logger = logging.getLogger(__name__)


class FunnelBuilder:
    """
    Builder для sales funnels.

    Поддерживает:
    - SaaS free trial funnel
    - Demo-based sales funnel
    - Self-serve funnel
    - Enterprise sales funnel
    """

    def __init__(self, llm):
        """
        Args:
            llm: LLM instance
        """
        self.llm = llm

    async def design_funnel(
        self,
        business_idea: Dict[str, Any],
        deployment_url: str,
        channels: List[str]
    ) -> Dict[str, Any]:
        """
        Проектирование sales funnel.

        Args:
            business_idea: Информация о бизнесе
            deployment_url: URL сайта
            channels: Sales каналы

        Returns:
            Dict с описанием funnel
        """
        pricing_model = business_idea.get("revenue_model", "freemium")

        # Определяем тип funnel на основе pricing model
        funnel_type = self._determine_funnel_type(pricing_model, channels)

        logger.info(f"Designing {funnel_type} funnel")

        # Генерация funnel с помощью LLM
        funnel = await self._generate_funnel(
            business_idea,
            deployment_url,
            funnel_type,
            channels
        )

        # Добавляем метаданные
        funnel["funnel_type"] = funnel_type
        funnel["deployment_url"] = deployment_url
        funnel["channels"] = channels

        return funnel

    def _determine_funnel_type(
        self,
        pricing_model: str,
        channels: List[str]
    ) -> str:
        """
        Определить тип funnel.

        Returns:
            str: Тип funnel
        """
        if pricing_model == "freemium" or pricing_model == "free_trial":
            if "demo" in channels:
                return "trial_with_demo"
            return "self_serve_trial"
        elif pricing_model == "demo_only":
            return "demo_required"
        elif pricing_model == "enterprise":
            return "enterprise_sales"
        else:
            return "self_serve_trial"  # Default

    async def _generate_funnel(
        self,
        business_idea: Dict[str, Any],
        deployment_url: str,
        funnel_type: str,
        channels: List[str]
    ) -> Dict[str, Any]:
        """
        Генерация funnel с помощью LLM.

        Returns:
            Dict с funnel stages и conversion rates
        """
        prompt = f"""
Design a {funnel_type} sales funnel for this SaaS business.

Business: {business_idea['name']}
Description: {business_idea['description']}
Target Audience: {business_idea.get('target_audience', 'Small teams')}
Pricing: {business_idea.get('pricing', 'Freemium')}
Channels: {', '.join(channels)}

Funnel should include:
1. All stages from visitor to paid customer
2. Estimated conversion rate for each stage (realistic SaaS benchmarks)
3. Average time in each stage
4. Key actions/triggers for progression
5. Drop-off reasons and solutions

Return as JSON:
{{
    "funnel_name": "{funnel_type} funnel for {business_idea['name']}",
    "stages": [
        {{
            "stage_number": 1,
            "name": "Visitor",
            "description": "User lands on website",
            "conversion_rate_to_next": 0.30,
            "avg_time_in_stage_hours": 0.1,
            "key_actions": ["View homepage", "Read about features"],
            "progression_triggers": ["Click signup button"],
            "drop_off_reasons": ["Not clear value prop", "Too expensive"],
            "optimization_tips": ["Clearer headline", "Add social proof"]
        }}
    ],
    "estimated_overall_conversion": 0.025,
    "avg_sales_cycle_days": 14
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.6,
            max_tokens=2500
        )

        funnel = self._parse_json_response(response)

        logger.info(f"Generated funnel with {len(funnel.get('stages', []))} stages")

        return funnel

    def calculate_funnel_metrics(
        self,
        funnel: Dict[str, Any],
        traffic: int = 1000
    ) -> Dict[str, Any]:
        """
        Рассчитать метрики funnel.

        Args:
            funnel: Funnel object
            traffic: Monthly traffic (visitors)

        Returns:
            Dict с метриками на каждом stage
        """
        stages = funnel.get("stages", [])

        metrics = {
            "monthly_traffic": traffic,
            "stage_metrics": [],
            "total_conversions": 0,
            "overall_conversion_rate": 0.0
        }

        current_volume = traffic

        for stage in stages:
            conversion_rate = stage.get("conversion_rate_to_next", 0.5)

            stage_metric = {
                "stage_name": stage.get("name", ""),
                "users_at_stage": int(current_volume),
                "conversion_rate": conversion_rate,
                "users_to_next_stage": int(current_volume * conversion_rate)
            }

            metrics["stage_metrics"].append(stage_metric)

            # Move to next stage
            current_volume = current_volume * conversion_rate

        # Final conversions
        metrics["total_conversions"] = int(current_volume)
        metrics["overall_conversion_rate"] = current_volume / traffic if traffic > 0 else 0

        return metrics

    def identify_bottlenecks(
        self,
        funnel: Dict[str, Any],
        actual_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Идентифицировать bottlenecks в funnel.

        Args:
            funnel: Funnel object
            actual_data: Actual performance data

        Returns:
            List of bottlenecks с рекомендациями
        """
        bottlenecks = []

        stages = funnel.get("stages", [])

        for i, stage in enumerate(stages):
            expected_conversion = stage.get("conversion_rate_to_next", 0.5)
            actual_conversion = actual_data.get(f"stage_{i}_conversion", expected_conversion)

            # Если actual на 30%+ хуже expected
            if actual_conversion < expected_conversion * 0.7:
                bottleneck = {
                    "stage_name": stage.get("name", ""),
                    "stage_number": i + 1,
                    "severity": "high" if actual_conversion < expected_conversion * 0.5 else "medium",
                    "expected_conversion": expected_conversion,
                    "actual_conversion": actual_conversion,
                    "gap": expected_conversion - actual_conversion,
                    "drop_off_reasons": stage.get("drop_off_reasons", []),
                    "optimization_tips": stage.get("optimization_tips", [])
                }

                bottlenecks.append(bottleneck)

        logger.info(f"Identified {len(bottlenecks)} bottlenecks")

        return bottlenecks

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        json_str = re.sub(r'^```(?:json)?\n', '', response.strip())
        json_str = re.sub(r'\n```$', '', json_str)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {
                "funnel_name": "Default Funnel",
                "stages": [],
                "estimated_overall_conversion": 0.02
            }


# Пример использования
if __name__ == "__main__":
    import asyncio
    from agents.base.mock_llm import MockLLM

    async def main():
        llm = MockLLM()
        builder = FunnelBuilder(llm=llm)

        business_idea = {
            "name": "TaskFlow AI",
            "description": "AI-powered PM tool for small teams",
            "target_audience": "Freelancers and teams of 2-10",
            "revenue_model": "freemium",
            "pricing": "Free + $19/month Pro"
        }

        # Design funnel
        funnel = await builder.design_funnel(
            business_idea=business_idea,
            deployment_url="https://taskflow-ai.vercel.app",
            channels=["email", "demo"]
        )

        print(f"Funnel: {funnel.get('funnel_name')}")
        print(f"Stages: {len(funnel.get('stages', []))}")
        print(f"Overall conversion: {funnel.get('estimated_overall_conversion', 0) * 100:.1f}%")

        # Calculate metrics
        metrics = builder.calculate_funnel_metrics(funnel, traffic=1000)

        print(f"\nWith 1000 monthly visitors:")
        print(f"Expected conversions: {metrics['total_conversions']}")

    asyncio.run(main())

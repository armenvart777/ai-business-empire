"""
Conversion Optimizer - оптимизация conversion rate.

A/B testing, pricing optimization, funnel analysis.
"""

import logging
from typing import Dict, Any, List
import json
import re


logger = logging.getLogger(__name__)


class ConversionOptimizer:
    """
    Оптимизатор конверсий.

    Функции:
    - Funnel analysis
    - Pricing optimization
    - A/B test recommendations
    - Objection handling
    - Conversion rate improvements
    """

    def __init__(self, llm):
        """
        Args:
            llm: LLM instance
        """
        self.llm = llm

    async def optimize_pricing(
        self,
        business_idea: Dict[str, Any],
        target_mrr: int
    ) -> Dict[str, Any]:
        """
        Оптимизация pricing strategy.

        Args:
            business_idea: Информация о бизнесе
            target_mrr: Target MRR

        Returns:
            Dict с pricing recommendations
        """
        current_pricing = business_idea.get("pricing", "$19/month")

        prompt = f"""
Optimize pricing strategy for this SaaS business.

Business: {business_idea['name']}
Description: {business_idea['description']}
Target Audience: {business_idea.get('target_audience', 'Small teams')}
Current Pricing: {current_pricing}
Target MRR: ${target_mrr}

Analyze and recommend:
1. Optimal price points for different tiers
2. Pricing model (per user, per feature, flat rate)
3. Free tier limitations
4. Trial duration
5. Annual discount
6. Pricing psychology (anchoring, decoy pricing)

Return as JSON:
{{
    "recommended_pricing_model": "per_user / flat_rate / usage_based",
    "tiers": [
        {{
            "tier_name": "Free",
            "price_monthly": 0,
            "price_annual": 0,
            "features": ["Feature 1", "Feature 2"],
            "limitations": ["Max 5 projects", "Basic support"],
            "target_audience": "Individuals, trying the product"
        }},
        {{
            "tier_name": "Pro",
            "price_monthly": 19,
            "price_annual": 190,
            "annual_discount_percent": 17,
            "features": ["All Free features", "Feature 3", "Feature 4"],
            "target_audience": "Small teams, power users"
        }}
    ],
    "trial_duration_days": 14,
    "recommended_price": 19,
    "pricing_psychology_tips": [
        "Anchor with higher enterprise price",
        "Make Pro tier most attractive (pricing highlight)"
    ]
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.6,
            max_tokens=2000
        )

        pricing_strategy = self._parse_json_response(response)

        logger.info(f"Generated pricing strategy with {len(pricing_strategy.get('tiers', []))} tiers")

        return pricing_strategy

    async def analyze_funnel(
        self,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Анализ funnel performance.

        Args:
            performance_data: Данные о performance

        Returns:
            Dict с insights
        """
        analysis = {
            "overall_health": "good",  # good/warning/critical
            "stage_analysis": [],
            "bottlenecks": [],
            "quick_wins": []
        }

        # Анализ каждой стадии
        for stage_key, stage_data in performance_data.items():
            if not stage_key.startswith("stage_"):
                continue

            visitors = stage_data.get("visitors", 0)
            converted = stage_data.get("converted", 0)
            conversion_rate = converted / visitors if visitors > 0 else 0

            # Benchmark conversion rates для SaaS
            benchmarks = {
                "stage_0": 0.30,  # Visitor → Signup
                "stage_1": 0.40,  # Signup → Trial
                "stage_2": 0.25,  # Trial → Paid
            }

            expected = benchmarks.get(stage_key, 0.3)

            stage_analysis = {
                "stage": stage_key,
                "visitors": visitors,
                "converted": converted,
                "conversion_rate": conversion_rate,
                "expected_conversion": expected,
                "performance": "good" if conversion_rate >= expected * 0.8 else "poor"
            }

            analysis["stage_analysis"].append(stage_analysis)

            # Identify bottlenecks
            if conversion_rate < expected * 0.7:
                analysis["bottlenecks"].append({
                    "stage": stage_key,
                    "severity": "high" if conversion_rate < expected * 0.5 else "medium",
                    "impact": visitors * (expected - conversion_rate)
                })

        # Overall health
        poor_stages = sum(1 for s in analysis["stage_analysis"] if s["performance"] == "poor")

        if poor_stages >= 2:
            analysis["overall_health"] = "critical"
        elif poor_stages == 1:
            analysis["overall_health"] = "warning"

        return analysis

    async def generate_recommendations(
        self,
        funnel_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Генерация рекомендаций по оптимизации.

        Args:
            funnel_analysis: Результаты анализа funnel

        Returns:
            List of actionable recommendations
        """
        recommendations = []

        bottlenecks = funnel_analysis.get("bottlenecks", [])

        # Рекомендации для каждого bottleneck
        for bottleneck in bottlenecks:
            stage = bottleneck.get("stage", "")

            if stage == "stage_0":  # Visitor → Signup
                recommendations.append({
                    "priority": "high",
                    "category": "Landing Page",
                    "issue": "Low visitor-to-signup conversion",
                    "recommendation": "Optimize landing page: clearer value prop, stronger CTA, add social proof",
                    "expected_impact": "+50-100% signups",
                    "effort": "medium",
                    "tactics": [
                        "A/B test headline variations",
                        "Add customer testimonials above the fold",
                        "Simplify signup form (email only)",
                        "Add urgency (limited spots, countdown)",
                        "Show trust badges (security, reviews)"
                    ]
                })
            elif stage == "stage_1":  # Signup → Trial
                recommendations.append({
                    "priority": "high",
                    "category": "Onboarding",
                    "issue": "Users not starting trial after signup",
                    "recommendation": "Improve onboarding: reduce friction, show quick wins",
                    "expected_impact": "+30-50% trial starts",
                    "effort": "high",
                    "tactics": [
                        "Interactive product tour",
                        "Pre-populate sample data",
                        "Gamify onboarding (progress bar)",
                        "Send reminder email if not started",
                        "Offer onboarding call for high-value leads"
                    ]
                })
            elif stage == "stage_2":  # Trial → Paid
                recommendations.append({
                    "priority": "high",
                    "category": "Trial Conversion",
                    "issue": "Low trial-to-paid conversion",
                    "recommendation": "Increase trial engagement and urgency",
                    "expected_impact": "+20-40% paid conversions",
                    "effort": "medium",
                    "tactics": [
                        "Email sequence during trial",
                        "In-app upgrade prompts at key moments",
                        "Show value metrics (time saved, tasks completed)",
                        "Trial expiration countdown",
                        "Limited-time discount (20% off first month)",
                        "Exit survey for churned trials"
                    ]
                })

        # General best practices
        if not recommendations:
            recommendations.append({
                "priority": "low",
                "category": "Continuous Optimization",
                "issue": "Performance is healthy",
                "recommendation": "Continue A/B testing for incremental gains",
                "expected_impact": "5-10% improvement",
                "effort": "ongoing",
                "tactics": [
                    "A/B test pricing page",
                    "Test different trial durations (7 vs 14 vs 30 days)",
                    "Experiment with pricing tiers",
                    "Test different email subject lines",
                    "Optimize for mobile conversion"
                ]
            })

        logger.info(f"Generated {len(recommendations)} recommendations")

        return recommendations

    async def create_ab_test_plan(
        self,
        test_hypothesis: str,
        metric: str = "conversion_rate"
    ) -> Dict[str, Any]:
        """
        Создать plan для A/B теста.

        Args:
            test_hypothesis: Гипотеза для тестирования
            metric: Метрика для измерения

        Returns:
            Dict с A/B test plan
        """
        return {
            "test_name": test_hypothesis,
            "hypothesis": test_hypothesis,
            "primary_metric": metric,
            "variants": {
                "A": {
                    "name": "Control",
                    "description": "Current version",
                    "traffic_split": 0.5
                },
                "B": {
                    "name": "Variation",
                    "description": "New version with change",
                    "traffic_split": 0.5
                }
            },
            "sample_size_needed": 1000,  # Минимум visitors per variant
            "confidence_level": 0.95,
            "expected_duration_days": 14,
            "success_criteria": f"{metric} improvement > 10%"
        }

    def calculate_statistical_significance(
        self,
        control_conversions: int,
        control_visitors: int,
        variant_conversions: int,
        variant_visitors: int
    ) -> Dict[str, Any]:
        """
        Рассчитать statistical significance (упрощенная версия).

        Args:
            control_conversions: Conversions в контрольной группе
            control_visitors: Visitors в контрольной группе
            variant_conversions: Conversions в варианте
            variant_visitors: Visitors в варианте

        Returns:
            Dict с результатами
        """
        control_rate = control_conversions / control_visitors if control_visitors > 0 else 0
        variant_rate = variant_conversions / variant_visitors if variant_visitors > 0 else 0

        improvement = ((variant_rate - control_rate) / control_rate * 100) if control_rate > 0 else 0

        # Упрощенная версия - в реальности нужен z-test или chi-square test
        # Для простоты: если выборка > 100 и improvement > 10%, считаем значимым

        is_significant = (
            control_visitors >= 100 and
            variant_visitors >= 100 and
            abs(improvement) >= 10
        )

        return {
            "control_rate": control_rate,
            "variant_rate": variant_rate,
            "improvement_percent": improvement,
            "is_significant": is_significant,
            "winner": "variant" if variant_rate > control_rate else "control",
            "recommendation": "Deploy variant" if is_significant and variant_rate > control_rate else "Keep testing or revert to control"
        }

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
        optimizer = ConversionOptimizer(llm=llm)

        business_idea = {
            "name": "TaskFlow AI",
            "description": "AI-powered PM tool for small teams",
            "target_audience": "Freelancers and teams of 2-10",
            "pricing": "Free + $19/month Pro"
        }

        # Optimize pricing
        pricing = await optimizer.optimize_pricing(
            business_idea=business_idea,
            target_mrr=5000
        )

        print(f"Pricing Strategy:")
        print(f"  - Tiers: {len(pricing.get('tiers', []))}")
        print(f"  - Recommended price: ${pricing.get('recommended_price', 0)}")

        # Analyze funnel (mock data)
        performance_data = {
            "stage_0": {"visitors": 1000, "converted": 200},  # 20% (below 30% benchmark)
            "stage_1": {"visitors": 200, "converted": 100},   # 50% (good)
            "stage_2": {"visitors": 100, "converted": 15}     # 15% (below 25% benchmark)
        }

        analysis = await optimizer.analyze_funnel(performance_data)

        print(f"\nFunnel Analysis:")
        print(f"  - Health: {analysis['overall_health']}")
        print(f"  - Bottlenecks: {len(analysis['bottlenecks'])}")

        # Get recommendations
        recommendations = await optimizer.generate_recommendations(analysis)

        print(f"\nRecommendations:")
        for rec in recommendations:
            print(f"  - [{rec['priority']}] {rec['recommendation']}")

    asyncio.run(main())

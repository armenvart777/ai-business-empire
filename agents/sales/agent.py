"""
Sales Agent - автоматизация продаж для SaaS.

Sales funnels, lead generation, CRM, email sequences.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from agents.base.template_agent import TemplateAgent
from agents.sales.funnel_builder import FunnelBuilder
from agents.sales.lead_generator import LeadGenerator
from agents.sales.crm_manager import CRMManager
from agents.sales.email_sequences import SalesEmailSequences
from agents.sales.conversion_optimizer import ConversionOptimizer


logger = logging.getLogger(__name__)


class SalesAgent(TemplateAgent):
    """
    Sales Agent - автоматизация продаж.

    Workflow:
    1. Design sales funnel
    2. Setup lead generation
    3. Create email sequences
    4. CRM integration
    5. Track conversions
    6. Optimize funnel
    7. A/B testing
    8. Revenue reporting
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4",
        data_dir: str = "data/sales"
    ):
        """
        Инициализация Sales Agent.

        Args:
            api_key: API ключ для LLM
            model: Модель для генерации
            data_dir: Директория для сохранения данных
        """
        super().__init__(
            agent_name="sales",
            api_key=api_key,
            model=model,
            data_dir=data_dir
        )

        self.funnel_builder = FunnelBuilder(llm=self.llm)
        self.lead_generator = LeadGenerator(llm=self.llm)
        self.crm_manager = CRMManager()
        self.email_sequences = SalesEmailSequences(llm=self.llm)
        self.optimizer = ConversionOptimizer(llm=self.llm)

    async def create_sales_system(
        self,
        business_idea: Dict[str, Any],
        deployment_url: str,
        target_mrr: int = 5000,
        channels: List[str] = ["email", "demo", "chat"],
        automation_level: str = "high"
    ) -> Dict[str, Any]:
        """
        Создать полную sales систему.

        Args:
            business_idea: Информация о бизнесе
            deployment_url: URL deployed MVP
            target_mrr: Target MRR в долларах
            channels: Sales каналы (email, demo, chat, phone)
            automation_level: Уровень автоматизации (low/medium/high)

        Returns:
            Dict с настроенной sales системой
        """
        logger.info(f"Creating sales system for {business_idea['name']}")

        system_id = f"sales-{business_idea['id']}-{datetime.now().strftime('%Y%m%d')}"

        # 1. Проектирование sales funnel
        logger.info("Step 1/8: Designing sales funnel")
        funnel = await self._design_sales_funnel(
            business_idea,
            deployment_url,
            channels
        )

        # 2. Setup lead generation
        logger.info("Step 2/8: Setting up lead generation")
        lead_gen_strategy = await self._setup_lead_generation(
            business_idea,
            funnel,
            target_mrr
        )

        # 3. Создание email sequences
        logger.info("Step 3/8: Creating sales email sequences")
        email_sequences = await self._create_email_sequences(
            business_idea,
            funnel
        )

        # 4. CRM setup
        logger.info("Step 4/8: Setting up CRM")
        crm_setup = await self._setup_crm(
            business_idea,
            funnel
        )

        # 5. Demo/onboarding flow
        demo_flow = None
        if "demo" in channels:
            logger.info("Step 5/8: Creating demo flow")
            demo_flow = await self._create_demo_flow(business_idea)

        # 6. Chat sales flow
        chat_flow = None
        if "chat" in channels:
            logger.info("Step 6/8: Creating chat sales flow")
            chat_flow = await self._create_chat_flow(business_idea)

        # 7. Pricing & packaging
        logger.info("Step 7/8: Optimizing pricing & packaging")
        pricing_strategy = await self._optimize_pricing(
            business_idea,
            target_mrr
        )

        # 8. Analytics & tracking
        logger.info("Step 8/8: Setting up sales analytics")
        analytics_setup = await self._setup_sales_analytics(
            deployment_url,
            funnel
        )

        # Собираем результаты
        sales_system = {
            "system_id": system_id,
            "business_id": business_idea["id"],
            "business_name": business_idea["name"],
            "deployment_url": deployment_url,
            "status": "active",
            "target_mrr": target_mrr,
            "channels": channels,
            "automation_level": automation_level,
            "funnel": funnel,
            "lead_generation": lead_gen_strategy,
            "email_sequences": email_sequences,
            "crm_setup": crm_setup,
            "demo_flow": demo_flow,
            "chat_flow": chat_flow,
            "pricing_strategy": pricing_strategy,
            "analytics_setup": analytics_setup,
            "created_at": datetime.now().isoformat(),
            "estimated_conversion_rate": self._calculate_estimated_conversion_rate(
                funnel,
                automation_level
            ),
            "estimated_customers_needed": self._calculate_customers_needed(
                target_mrr,
                pricing_strategy
            )
        }

        # Сохраняем систему
        await self.save_data(sales_system, f"systems/{system_id}")

        logger.info(f"✅ Sales system created: {system_id}")

        return sales_system

    async def _design_sales_funnel(
        self,
        business_idea: Dict[str, Any],
        deployment_url: str,
        channels: List[str]
    ) -> Dict[str, Any]:
        """
        Проектирование sales funnel.

        Returns:
            Dict с описанием sales funnel
        """
        return await self.funnel_builder.design_funnel(
            business_idea=business_idea,
            deployment_url=deployment_url,
            channels=channels
        )

    async def _setup_lead_generation(
        self,
        business_idea: Dict[str, Any],
        funnel: Dict[str, Any],
        target_mrr: int
    ) -> Dict[str, Any]:
        """
        Setup lead generation стратегии.

        Returns:
            Dict с lead generation стратегией
        """
        return await self.lead_generator.create_lead_strategy(
            business_idea=business_idea,
            funnel=funnel,
            target_mrr=target_mrr
        )

    async def _create_email_sequences(
        self,
        business_idea: Dict[str, Any],
        funnel: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Создать sales email sequences.

        Returns:
            List of email sequence objects
        """
        sequences = []

        # 1. Trial → Paid conversion sequence
        trial_to_paid = await self.email_sequences.create_trial_to_paid_sequence(
            business_idea
        )
        sequences.append(trial_to_paid)

        # 2. Demo follow-up sequence
        if "demo" in funnel.get("channels", []):
            demo_followup = await self.email_sequences.create_demo_followup_sequence(
                business_idea
            )
            sequences.append(demo_followup)

        # 3. Re-engagement sequence (для churned users)
        reengagement = await self.email_sequences.create_reengagement_sequence(
            business_idea
        )
        sequences.append(reengagement)

        return sequences

    async def _setup_crm(
        self,
        business_idea: Dict[str, Any],
        funnel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Setup CRM интеграции.

        Returns:
            Dict с CRM настройками
        """
        return await self.crm_manager.setup_crm(
            business_idea=business_idea,
            funnel_stages=funnel.get("stages", [])
        )

    async def _create_demo_flow(
        self,
        business_idea: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Создать demo/onboarding flow.

        Returns:
            Dict с demo flow
        """
        prompt = f"""
Create a product demo/onboarding flow for this SaaS business.

Business: {business_idea['name']}
Description: {business_idea['description']}
Key Features: {', '.join(business_idea.get('key_features', []))}

Demo should:
1. Highlight key features (2-3 most impactful)
2. Show quick wins (value in first 5 minutes)
3. Interactive walkthrough
4. End with clear next step (start trial / upgrade)

Return as JSON:
{{
    "demo_type": "interactive_tour",
    "duration_minutes": 10,
    "steps": [
        {{
            "step_number": 1,
            "title": "...",
            "description": "...",
            "action": "...",
            "expected_outcome": "..."
        }}
    ],
    "quick_wins": ["Win 1", "Win 2"],
    "cta": "Start your free trial"
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.7,
            max_tokens=2000
        )

        return self._parse_json_response(response)

    async def _create_chat_flow(
        self,
        business_idea: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Создать chat sales flow (live chat / chatbot).

        Returns:
            Dict с chat flow
        """
        prompt = f"""
Create a sales chat flow for this SaaS business.

Business: {business_idea['name']}
Description: {business_idea['description']}
Pricing: {business_idea.get('pricing', 'Freemium')}

Chat flow should:
1. Qualify leads (ask qualifying questions)
2. Understand use case
3. Recommend appropriate plan
4. Handle objections
5. Close the sale or book demo

Return as JSON:
{{
    "flow_type": "sales_chat",
    "greeting": "...",
    "qualifying_questions": ["Q1", "Q2", "Q3"],
    "objection_handling": {{
        "price_objection": "...",
        "feature_objection": "...",
        "competitor_objection": "..."
    }},
    "closing_messages": ["...", "..."],
    "fallback_to_human": "Conditions when to escalate to human agent"
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.7,
            max_tokens=2000
        )

        return self._parse_json_response(response)

    async def _optimize_pricing(
        self,
        business_idea: Dict[str, Any],
        target_mrr: int
    ) -> Dict[str, Any]:
        """
        Оптимизация pricing & packaging.

        Returns:
            Dict с pricing стратегией
        """
        return await self.optimizer.optimize_pricing(
            business_idea=business_idea,
            target_mrr=target_mrr
        )

    async def _setup_sales_analytics(
        self,
        deployment_url: str,
        funnel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Setup sales analytics tracking.

        Returns:
            Dict с analytics настройками
        """
        stages = funnel.get("stages", [])

        return {
            "url": deployment_url,
            "tracked_events": [
                {
                    "event_name": "trial_started",
                    "category": "Sales",
                    "action": "Start Trial",
                    "value": 0
                },
                {
                    "event_name": "demo_requested",
                    "category": "Sales",
                    "action": "Request Demo",
                    "value": 0
                },
                {
                    "event_name": "subscription_created",
                    "category": "Sales",
                    "action": "Subscribe",
                    "value": 19  # Monthly price
                },
                {
                    "event_name": "trial_converted",
                    "category": "Sales",
                    "action": "Convert",
                    "value": 19
                },
                {
                    "event_name": "subscription_upgraded",
                    "category": "Sales",
                    "action": "Upgrade",
                    "value": 49
                },
                {
                    "event_name": "subscription_churned",
                    "category": "Sales",
                    "action": "Churn",
                    "value": -19
                }
            ],
            "funnel_tracking": [
                {
                    "stage": stage.get("name", ""),
                    "event": f"funnel_stage_{i}",
                    "conversion_goal": i == len(stages) - 1
                }
                for i, stage in enumerate(stages)
            ],
            "revenue_tracking": {
                "mrr": "Monthly Recurring Revenue",
                "arr": "Annual Recurring Revenue",
                "ltv": "Lifetime Value",
                "cac": "Customer Acquisition Cost",
                "payback_period": "CAC Payback Period"
            }
        }

    def _calculate_estimated_conversion_rate(
        self,
        funnel: Dict[str, Any],
        automation_level: str
    ) -> float:
        """
        Оценить conversion rate на основе funnel и automation.

        Returns:
            float: Estimated conversion rate (visitor → paid customer)
        """
        # Базовые conversion rates для SaaS
        base_rates = {
            "low": 0.01,  # 1% (много manual work)
            "medium": 0.02,  # 2% (полу-автоматизировано)
            "high": 0.03  # 3% (полная автоматизация)
        }

        return base_rates.get(automation_level, 0.02)

    def _calculate_customers_needed(
        self,
        target_mrr: int,
        pricing_strategy: Dict[str, Any]
    ) -> int:
        """
        Рассчитать количество customers для достижения target MRR.

        Returns:
            int: Number of customers needed
        """
        avg_price = pricing_strategy.get("recommended_price", 19)

        return int(target_mrr / avg_price)

    async def optimize_conversion_rate(
        self,
        system_id: str,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Оптимизация conversion rate на основе данных.

        Args:
            system_id: ID sales системы
            performance_data: Данные о performance

        Returns:
            Dict с рекомендациями по оптимизации
        """
        logger.info(f"Optimizing conversion rate for: {system_id}")

        # Анализ funnel performance
        funnel_analysis = await self.optimizer.analyze_funnel(performance_data)

        # Рекомендации по оптимизации
        recommendations = await self.optimizer.generate_recommendations(
            funnel_analysis
        )

        return {
            "system_id": system_id,
            "funnel_analysis": funnel_analysis,
            "recommendations": recommendations,
            "optimized_at": datetime.now().isoformat()
        }


# Пример использования
if __name__ == "__main__":
    import asyncio

    async def main():
        agent = SalesAgent()

        # Бизнес-идея (из Business Generator)
        business_idea = {
            "id": "test-123",
            "name": "TaskFlow AI",
            "tagline": "Project management that thinks for you",
            "description": "AI-powered PM tool for small teams",
            "target_audience": "Freelancers and teams of 2-10",
            "key_features": [
                "AI task prioritization",
                "Automatic deadline prediction",
                "Smart workflow suggestions"
            ],
            "revenue_model": "freemium",
            "pricing": "Free + $19/month Pro"
        }

        # Deployment URL (из Developer Agent)
        deployment_url = "https://business-123-taskflow-ai.vercel.app"

        # Создаем sales систему
        sales_system = await agent.create_sales_system(
            business_idea=business_idea,
            deployment_url=deployment_url,
            target_mrr=5000,
            channels=["email", "demo", "chat"],
            automation_level="high"
        )

        print(f"\n✅ Sales System Created!")
        print(f"System ID: {sales_system['system_id']}")
        print(f"Funnel stages: {len(sales_system['funnel']['stages'])}")
        print(f"Email sequences: {len(sales_system['email_sequences'])}")
        print(f"Estimated conversion rate: {sales_system['estimated_conversion_rate'] * 100:.1f}%")
        print(f"Customers needed for ${sales_system['target_mrr']} MRR: {sales_system['estimated_customers_needed']}")

    asyncio.run(main())

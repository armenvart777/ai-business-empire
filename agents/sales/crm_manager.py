"""
CRM Manager - интеграция с CRM системами.

HubSpot, Pipedrive, или custom CRM setup.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class CRMManager:
    """
    Менеджер CRM интеграций.

    Поддерживает:
    - HubSpot (most popular for SaaS)
    - Pipedrive
    - Custom CRM setup
    """

    def __init__(self):
        """Инициализация CRM manager."""
        pass

    async def setup_crm(
        self,
        business_idea: Dict[str, Any],
        funnel_stages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Setup CRM интеграции.

        Args:
            business_idea: Информация о бизнесе
            funnel_stages: Stages из sales funnel

        Returns:
            Dict с CRM настройками
        """
        # Для SaaS лучше всего HubSpot (free tier)
        crm_provider = "HubSpot"

        setup = {
            "provider": crm_provider,
            "pipeline_setup": self._create_pipeline_from_funnel(funnel_stages),
            "contact_properties": self._define_contact_properties(business_idea),
            "deal_properties": self._define_deal_properties(),
            "automation_workflows": self._create_automation_workflows(),
            "reporting_dashboards": self._create_dashboards()
        }

        logger.info(f"Setup CRM: {crm_provider}")

        return setup

    def _create_pipeline_from_funnel(
        self,
        funnel_stages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Создать CRM pipeline из funnel stages.

        Returns:
            Dict с pipeline configuration
        """
        pipeline_stages = []

        for i, stage in enumerate(funnel_stages):
            pipeline_stage = {
                "stage_name": stage.get("name", f"Stage {i+1}"),
                "stage_order": i + 1,
                "probability": int(stage.get("conversion_rate_to_next", 0.5) * 100),
                "actions": stage.get("key_actions", []),
                "expected_duration_days": int(stage.get("avg_time_in_stage_hours", 24) / 24)
            }

            pipeline_stages.append(pipeline_stage)

        return {
            "pipeline_name": "Sales Pipeline",
            "stages": pipeline_stages
        }

    def _define_contact_properties(
        self,
        business_idea: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Определить custom properties для contacts.

        Returns:
            List of contact property definitions
        """
        return [
            {
                "name": "company_size",
                "label": "Company Size",
                "type": "select",
                "options": ["1-5", "6-20", "21-50", "51+"]
            },
            {
                "name": "industry",
                "label": "Industry",
                "type": "text"
            },
            {
                "name": "role",
                "label": "Role/Title",
                "type": "select",
                "options": ["Decision Maker", "Influencer", "End User"]
            },
            {
                "name": "lead_source",
                "label": "Lead Source",
                "type": "select",
                "options": ["Website", "Lead Magnet", "Referral", "Ads", "Cold Outreach"]
            },
            {
                "name": "lead_score",
                "label": "Lead Score",
                "type": "number"
            },
            {
                "name": "engagement_level",
                "label": "Engagement Level",
                "type": "select",
                "options": ["Hot", "Warm", "Cold"]
            },
            {
                "name": "pain_points",
                "label": "Primary Pain Points",
                "type": "text"
            },
            {
                "name": "budget",
                "label": "Budget Range",
                "type": "select",
                "options": ["<$50/mo", "$50-$100/mo", "$100-$500/mo", "$500+/mo"]
            },
            {
                "name": "timeline",
                "label": "Purchase Timeline",
                "type": "select",
                "options": ["Immediate", "This month", "This quarter", "Just researching"]
            }
        ]

    def _define_deal_properties(self) -> List[Dict[str, Any]]:
        """
        Определить custom properties для deals.

        Returns:
            List of deal property definitions
        """
        return [
            {
                "name": "plan_type",
                "label": "Plan Type",
                "type": "select",
                "options": ["Free", "Basic", "Pro", "Enterprise"]
            },
            {
                "name": "mrr",
                "label": "Monthly Recurring Revenue",
                "type": "number"
            },
            {
                "name": "arr",
                "label": "Annual Recurring Revenue",
                "type": "number"
            },
            {
                "name": "contract_length",
                "label": "Contract Length (months)",
                "type": "number"
            },
            {
                "name": "deal_source",
                "label": "Deal Source",
                "type": "select",
                "options": ["Self-Serve", "Demo", "Sales Call", "Partner"]
            },
            {
                "name": "competitors_considered",
                "label": "Competitors Considered",
                "type": "text"
            },
            {
                "name": "close_reason",
                "label": "Close Reason (Won/Lost)",
                "type": "text"
            }
        ]

    def _create_automation_workflows(self) -> List[Dict[str, Any]]:
        """
        Создать automation workflows в CRM.

        Returns:
            List of workflow definitions
        """
        return [
            {
                "workflow_name": "New Lead Nurture",
                "trigger": "Contact property 'Lead Score' is less than 40",
                "actions": [
                    {
                        "action_type": "send_email",
                        "template": "Educational Email Sequence",
                        "delay_days": 0
                    },
                    {
                        "action_type": "assign_to_rep",
                        "rep": "Auto-assign based on territory",
                        "delay_days": 0
                    }
                ]
            },
            {
                "workflow_name": "Hot Lead Alert",
                "trigger": "Contact property 'Lead Score' is greater than 70",
                "actions": [
                    {
                        "action_type": "notify_sales_rep",
                        "message": "New hot lead needs immediate attention",
                        "delay_days": 0
                    },
                    {
                        "action_type": "create_task",
                        "task": "Reach out to hot lead within 24 hours",
                        "delay_days": 0
                    }
                ]
            },
            {
                "workflow_name": "Trial Started",
                "trigger": "Deal stage moves to 'Trial'",
                "actions": [
                    {
                        "action_type": "send_email",
                        "template": "Welcome to Trial",
                        "delay_days": 0
                    },
                    {
                        "action_type": "send_email",
                        "template": "Trial Day 3 Tips",
                        "delay_days": 3
                    },
                    {
                        "action_type": "send_email",
                        "template": "Trial Day 7 Check-in",
                        "delay_days": 7
                    },
                    {
                        "action_type": "create_task",
                        "task": "Call to check trial progress",
                        "delay_days": 5
                    }
                ]
            },
            {
                "workflow_name": "Deal Won",
                "trigger": "Deal stage moves to 'Won'",
                "actions": [
                    {
                        "action_type": "send_internal_notification",
                        "message": "New customer! 🎉",
                        "delay_days": 0
                    },
                    {
                        "action_type": "send_email",
                        "template": "Welcome New Customer",
                        "delay_days": 0
                    },
                    {
                        "action_type": "create_onboarding_tasks",
                        "delay_days": 0
                    }
                ]
            },
            {
                "workflow_name": "Deal Lost",
                "trigger": "Deal stage moves to 'Lost'",
                "actions": [
                    {
                        "action_type": "send_email",
                        "template": "Sorry to see you go",
                        "delay_days": 0
                    },
                    {
                        "action_type": "add_to_list",
                        "list": "Lost Deals - Future Re-engagement",
                        "delay_days": 0
                    },
                    {
                        "action_type": "send_email",
                        "template": "Re-engagement (6 months later)",
                        "delay_days": 180
                    }
                ]
            }
        ]

    def _create_dashboards(self) -> List[Dict[str, Any]]:
        """
        Создать reporting dashboards.

        Returns:
            List of dashboard definitions
        """
        return [
            {
                "dashboard_name": "Sales Performance",
                "reports": [
                    {
                        "report_name": "Pipeline Value",
                        "type": "sum",
                        "metric": "Deal MRR",
                        "group_by": "Deal Stage"
                    },
                    {
                        "report_name": "Conversion Rates",
                        "type": "funnel",
                        "stages": "All pipeline stages"
                    },
                    {
                        "report_name": "Monthly Closed Won",
                        "type": "line_chart",
                        "metric": "Deals Won",
                        "time_period": "Last 12 months"
                    },
                    {
                        "report_name": "Average Deal Size",
                        "type": "average",
                        "metric": "Deal MRR"
                    },
                    {
                        "report_name": "Sales Cycle Length",
                        "type": "average",
                        "metric": "Days to Close"
                    }
                ]
            },
            {
                "dashboard_name": "Lead Quality",
                "reports": [
                    {
                        "report_name": "Lead Score Distribution",
                        "type": "bar_chart",
                        "metric": "Lead Score",
                        "group_by": "Engagement Level"
                    },
                    {
                        "report_name": "Lead Source Performance",
                        "type": "table",
                        "columns": ["Lead Source", "Count", "Conversion Rate", "Avg Deal Size"]
                    },
                    {
                        "report_name": "Top Performing Industries",
                        "type": "pie_chart",
                        "metric": "Closed Won Deals",
                        "group_by": "Industry"
                    }
                ]
            },
            {
                "dashboard_name": "Revenue Metrics",
                "reports": [
                    {
                        "report_name": "MRR Growth",
                        "type": "line_chart",
                        "metric": "Total MRR",
                        "time_period": "Last 12 months"
                    },
                    {
                        "report_name": "ARR",
                        "type": "single_value",
                        "metric": "Total ARR"
                    },
                    {
                        "report_name": "Churn Rate",
                        "type": "percentage",
                        "metric": "Churned MRR / Total MRR"
                    },
                    {
                        "report_name": "Customer Lifetime Value",
                        "type": "average",
                        "metric": "LTV"
                    }
                ]
            }
        ]

    def sync_lead_to_crm(
        self,
        lead_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Синхронизация лида в CRM.

        Args:
            lead_data: Данные о лиде

        Returns:
            Dict с результатом синхронизации
        """
        # Mock implementation
        # В реальности: HubSpot API, Pipedrive API, etc.

        contact_id = f"contact_{datetime.now().timestamp()}"

        logger.info(f"Synced lead to CRM: {contact_id}")

        return {
            "contact_id": contact_id,
            "synced_at": datetime.now().isoformat(),
            "crm_url": f"https://app.hubspot.com/contacts/contact/{contact_id}"
        }


# Пример использования
if __name__ == "__main__":
    import asyncio

    async def main():
        crm = CRMManager()

        funnel_stages = [
            {"name": "Visitor", "conversion_rate_to_next": 0.3, "avg_time_in_stage_hours": 1},
            {"name": "Trial", "conversion_rate_to_next": 0.4, "avg_time_in_stage_hours": 168},
            {"name": "Paid", "conversion_rate_to_next": 1.0, "avg_time_in_stage_hours": 0}
        ]

        setup = await crm.setup_crm(
            business_idea={"name": "TaskFlow AI"},
            funnel_stages=funnel_stages
        )

        print(f"CRM Setup:")
        print(f"  - Provider: {setup['provider']}")
        print(f"  - Pipeline stages: {len(setup['pipeline_setup']['stages'])}")
        print(f"  - Contact properties: {len(setup['contact_properties'])}")
        print(f"  - Automation workflows: {len(setup['automation_workflows'])}")
        print(f"  - Dashboards: {len(setup['reporting_dashboards'])}")

    asyncio.run(main())

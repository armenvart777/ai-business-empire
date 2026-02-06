"""
Sales Agent - автоматизация продаж для SaaS.

Экспорты:
- SalesAgent: Основной класс агента
- FunnelBuilder: Проектирование sales funnels
- LeadGenerator: Lead generation & qualification
- CRMManager: CRM интеграция
- SalesEmailSequences: Sales email sequences
- ConversionOptimizer: Conversion optimization
"""

from agents.sales.agent import SalesAgent
from agents.sales.funnel_builder import FunnelBuilder
from agents.sales.lead_generator import LeadGenerator
from agents.sales.crm_manager import CRMManager
from agents.sales.email_sequences import SalesEmailSequences
from agents.sales.conversion_optimizer import ConversionOptimizer

__all__ = [
    "SalesAgent",
    "FunnelBuilder",
    "LeadGenerator",
    "CRMManager",
    "SalesEmailSequences",
    "ConversionOptimizer"
]

__version__ = "0.1.0"

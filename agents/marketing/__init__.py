"""
Marketing Agent - автоматический маркетинг для MVP.

Экспорты:
- MarketingAgent: Основной класс агента
- ContentGenerator: Генерация контента
- SEOOptimizer: SEO оптимизация
- EmailCampaignManager: Email маркетинг
- SocialMediaManager: Social media management
- MarketingAnalytics: Analytics tracking
"""

from agents.marketing.agent import MarketingAgent
from agents.marketing.content_generator import ContentGenerator
from agents.marketing.seo_optimizer import SEOOptimizer
from agents.marketing.email_campaign import EmailCampaignManager
from agents.marketing.social_media import SocialMediaManager
from agents.marketing.analytics import MarketingAnalytics

__all__ = [
    "MarketingAgent",
    "ContentGenerator",
    "SEOOptimizer",
    "EmailCampaignManager",
    "SocialMediaManager",
    "MarketingAnalytics"
]

__version__ = "0.1.0"

"""
Trend Scanner Agent - обнаружение трендов и бизнес-возможностей.

Экспорты:
- TrendScannerAgent: Основной класс агента
- GoogleTrendsSource, RedditSource, ProductHuntSource: Источники данных
- TrendAnalyzer: Анализатор трендов
- TrendScorer: Оценка трендов
"""

from agents.trend-scanner.agent import TrendScannerAgent
from agents.trend-scanner.sources import (
    GoogleTrendsSource,
    RedditSource,
    ProductHuntSource
)
from agents.trend-scanner.analyzer import TrendAnalyzer
from agents.trend-scanner.scorer import TrendScorer

__all__ = [
    "TrendScannerAgent",
    "GoogleTrendsSource",
    "RedditSource",
    "ProductHuntSource",
    "TrendAnalyzer",
    "TrendScorer"
]

__version__ = "0.1.0"

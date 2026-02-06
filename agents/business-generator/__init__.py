"""
Business Generator Agent - генерация бизнес-идей из трендов.

Экспорты:
- BusinessGeneratorAgent: Основной класс агента
- IdeaGenerator: Генератор идей с помощью LLM
- IdeaValidator: Валидация через поиск конкурентов
- IdeaPrioritizer: Приоритизация идей
"""

from agents.business_generator.agent import BusinessGeneratorAgent
from agents.business_generator.idea_generator import IdeaGenerator
from agents.business_generator.validator import IdeaValidator
from agents.business_generator.prioritizer import IdeaPrioritizer

__all__ = [
    "BusinessGeneratorAgent",
    "IdeaGenerator",
    "IdeaValidator",
    "IdeaPrioritizer"
]

__version__ = "0.1.0"

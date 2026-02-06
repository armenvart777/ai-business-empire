"""
Idea Validator - валидация бизнес-идей через поиск конкурентов.

Проверяет существующие решения и оценивает уровень конкуренции.
"""

import logging
from typing import Dict, Any, List
import asyncio


logger = logging.getLogger(__name__)


class IdeaValidator:
    """
    Валидатор бизнес-идей.

    Функции:
    - Поиск существующих конкурентов
    - Оценка уровня конкуренции
    - Анализ дифференциации
    """

    def __init__(self):
        """Инициализация валидатора."""
        pass

    async def validate(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валидация идеи через поиск конкурентов.

        Args:
            idea: Бизнес-идея

        Returns:
            Dict: Данные валидации
        """
        try:
            # Ищем конкурентов
            competitors = await self._find_competitors(idea)

            # Анализируем конкуренцию
            competition_analysis = self._analyze_competition(competitors, idea)

            # Возвращаем данные валидации
            return {
                "competitors_found": len(competitors),
                "competitors": competitors[:5],  # Топ-5
                "competition_level": competition_analysis["level"],
                "competition_score": competition_analysis["score"],
                "differentiation_strength": competition_analysis["differentiation"],
                "market_gap": competition_analysis["gap"],
                "validation_status": "validated"
            }

        except Exception as e:
            logger.error(f"Error validating idea: {e}")
            return {
                "competitors_found": 0,
                "competitors": [],
                "competition_level": "unknown",
                "competition_score": 50,
                "differentiation_strength": "unknown",
                "market_gap": "unknown",
                "validation_status": "failed"
            }

    async def _find_competitors(self, idea: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Найти существующих конкурентов.

        Использует поиск по ключевым словам.

        Args:
            idea: Бизнес-идея

        Returns:
            List[Dict]: Список конкурентов
        """
        # Для реальной реализации нужно использовать:
        # - Google Search API
        # - Product Hunt API
        # - AlternativeTo API
        # - Manual scraping

        # Сейчас возвращаем mock data для тестирования
        logger.info(f"Searching competitors for: {idea['name']}")

        # Mock competitors
        mock_competitors = [
            {
                "name": "Competitor 1",
                "url": "https://example.com/competitor1",
                "description": "Similar product in the space",
                "pricing": "$29/mo",
                "users": "~10k",
                "founded": "2023"
            },
            {
                "name": "Competitor 2",
                "url": "https://example.com/competitor2",
                "description": "Another alternative",
                "pricing": "Free + $49/mo Pro",
                "users": "~5k",
                "founded": "2024"
            }
        ]

        # Simulate API delay
        await asyncio.sleep(0.5)

        # В реальности здесь должен быть поиск
        # Для демо возвращаем 0-3 конкурента рандомно
        import random
        num_competitors = random.randint(0, 3)

        return mock_competitors[:num_competitors]

    def _analyze_competition(
        self,
        competitors: List[Dict[str, Any]],
        idea: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Анализ уровня конкуренции.

        Args:
            competitors: Список конкурентов
            idea: Наша идея

        Returns:
            Dict: Анализ конкуренции
        """
        num_competitors = len(competitors)

        # Определяем уровень конкуренции
        if num_competitors == 0:
            level = "low"
            score = 90  # Хорошо - нет конкурентов
            gap = "wide"
        elif num_competitors <= 2:
            level = "medium"
            score = 70
            gap = "moderate"
        elif num_competitors <= 5:
            level = "high"
            score = 40
            gap = "narrow"
        else:
            level = "very_high"
            score = 20
            gap = "crowded"

        # Оцениваем силу дифференциации
        unique_angle = idea.get("unique_angle", "")
        if unique_angle and len(unique_angle) > 50:
            differentiation = "strong"
        elif unique_angle:
            differentiation = "moderate"
        else:
            differentiation = "weak"

        return {
            "level": level,
            "score": score,
            "differentiation": differentiation,
            "gap": gap
        }

    async def check_domain_available(self, domain: str) -> bool:
        """
        Проверить доступность домена.

        Args:
            domain: Доменное имя (без .com)

        Returns:
            bool: True если доступен
        """
        # Для реальной реализации использовать:
        # - whois lookup
        # - Domain availability APIs (Namecheap, GoDaddy)

        # Mock implementation
        import random
        await asyncio.sleep(0.3)
        return random.choice([True, False])

    def suggest_domain_names(self, idea: Dict[str, Any], num: int = 5) -> List[str]:
        """
        Предложить доменные имена для идеи.

        Args:
            idea: Бизнес-идея
            num: Количество вариантов

        Returns:
            List[str]: Список доменов
        """
        name = idea["name"].lower().replace(" ", "")
        tagline_words = idea["tagline"].lower().split()

        suggestions = [
            f"{name}.com",
            f"get{name}.com",
            f"try{name}.com",
            f"{name}app.com",
            f"{name}hq.com"
        ]

        # Добавляем варианты из tagline
        for word in tagline_words[:3]:
            if len(word) > 4:
                suggestions.append(f"{word}{name}.com")

        return suggestions[:num]


# Пример использования
if __name__ == "__main__":
    import asyncio

    async def main():
        validator = IdeaValidator()

        idea = {
            "name": "TaskFlow AI",
            "tagline": "Project management that thinks for you",
            "unique_angle": "Uses ML to learn from team behavior"
        }

        # Валидируем
        validation = await validator.validate(idea)

        print("Validation Results:")
        print(f"Competitors found: {validation['competitors_found']}")
        print(f"Competition level: {validation['competition_level']}")
        print(f"Competition score: {validation['competition_score']}/100")
        print(f"Market gap: {validation['market_gap']}")

        # Предлагаем домены
        domains = validator.suggest_domain_names(idea)
        print(f"\nSuggested domains: {', '.join(domains[:3])}")

    asyncio.run(main())

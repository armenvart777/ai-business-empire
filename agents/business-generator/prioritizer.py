"""
Idea Prioritizer - приоритизация бизнес-идей.

Рассчитывает priority score на основе множества факторов.
"""

import logging
from typing import Dict, Any


logger = logging.getLogger(__name__)


class IdeaPrioritizer:
    """
    Приоритизатор бизнес-идей.

    Рассчитывает priority score (0-100) на основе:
    - Revenue potential
    - Technical complexity
    - Time to MVP
    - Competition level
    - Market size
    - Trend score
    """

    def __init__(self):
        """Инициализация приоритизатора."""
        # Веса для факторов (сумма = 100)
        self.weights = {
            "revenue_potential": 30,    # Потенциальный доход
            "feasibility": 25,           # Простота реализации
            "competition": 20,           # Уровень конкуренции
            "market_size": 15,           # Размер рынка
            "trend_strength": 10         # Сила тренда
        }

    def calculate_priority(self, idea: Dict[str, Any]) -> int:
        """
        Рассчитать priority score идеи.

        Args:
            idea: Бизнес-идея с метриками

        Returns:
            int: Priority score (0-100)
        """
        # Рассчитываем компоненты
        revenue_score = self._calculate_revenue_score(idea)
        feasibility_score = self._calculate_feasibility_score(idea)
        competition_score = self._calculate_competition_score(idea)
        market_score = self._calculate_market_score(idea)
        trend_score = self._calculate_trend_score(idea)

        # Взвешенная сумма
        total = (
            revenue_score * self.weights["revenue_potential"] / 100 +
            feasibility_score * self.weights["feasibility"] / 100 +
            competition_score * self.weights["competition"] / 100 +
            market_score * self.weights["market_size"] / 100 +
            trend_score * self.weights["trend_strength"] / 100
        )

        priority = int(round(total))

        logger.debug(
            f"Priority for '{idea.get('name', 'Unknown')}': {priority}/100 "
            f"(rev={revenue_score}, feas={feasibility_score}, comp={competition_score})"
        )

        return priority

    def _calculate_revenue_score(self, idea: Dict[str, Any]) -> int:
        """Оценка потенциального дохода (0-100)."""
        revenue_potential = idea.get("revenue_potential", "$0-0/mo")

        # Парсим диапазон (например "$10k-50k/mo")
        try:
            # Извлекаем максимальное значение
            import re
            numbers = re.findall(r'(\d+)k', revenue_potential.lower())
            if numbers:
                max_revenue = int(numbers[-1])  # Берем последнее (максимальное)

                # Нормализуем:
                # $100k+/mo = 100 points
                # $50k/mo = 80 points
                # $10k/mo = 50 points
                # $5k/mo = 30 points
                if max_revenue >= 100:
                    return 100
                elif max_revenue >= 50:
                    return 80
                elif max_revenue >= 20:
                    return 65
                elif max_revenue >= 10:
                    return 50
                elif max_revenue >= 5:
                    return 30
                else:
                    return 20

        except:
            pass

        # Default
        return 50

    def _calculate_feasibility_score(self, idea: Dict[str, Any]) -> int:
        """Оценка простоты реализации (0-100)."""
        complexity = idea.get("technical_complexity", "medium").lower()
        time_to_mvp = idea.get("time_to_mvp_weeks", 8)

        # Оценка сложности
        complexity_scores = {
            "low": 90,
            "medium": 70,
            "high": 40
        }
        complexity_score = complexity_scores.get(complexity, 60)

        # Оценка времени
        # 2 недели = 100 points
        # 4 недели = 80 points
        # 8 недель = 50 points
        # 12+ недель = 30 points
        if time_to_mvp <= 2:
            time_score = 100
        elif time_to_mvp <= 4:
            time_score = 80
        elif time_to_mvp <= 6:
            time_score 65
        elif time_to_mvp <= 8:
            time_score = 50
        else:
            time_score = 30

        # Средневзвешенное
        feasibility = (complexity_score * 0.6 + time_score * 0.4)

        return int(feasibility)

    def _calculate_competition_score(self, idea: Dict[str, Any]) -> int:
        """Оценка уровня конкуренции (0-100)."""
        # Используем competition_score из validator
        comp_score = idea.get("competition_score", 50)

        # Или рассчитываем из competition_level
        if comp_score == 50:  # Default, нужно рассчитать
            competition_level = idea.get("competition_level", "medium").lower()

            level_scores = {
                "low": 90,
                "medium": 70,
                "high": 40,
                "very_high": 20,
                "unknown": 50
            }

            comp_score = level_scores.get(competition_level, 50)

        return comp_score

    def _calculate_market_score(self, idea: Dict[str, Any]) -> int:
        """Оценка размера рынка (0-100)."""
        market_size = idea.get("market_size", "unknown").lower()

        market_scores = {
            "large": 100,
            "medium": 70,
            "small": 40,
            "niche": 30,
            "unknown": 50
        }

        return market_scores.get(market_size, 50)

    def _calculate_trend_score(self, idea: Dict[str, Any]) -> int:
        """Оценка силы тренда (0-100)."""
        trend_score = idea.get("trend_score", 50)

        # Нормализуем если нужно (уже должен быть 0-100)
        if trend_score > 100:
            trend_score = 100
        elif trend_score < 0:
            trend_score = 0

        return int(trend_score)

    def get_priority_explanation(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """
        Получить детальное объяснение priority score.

        Args:
            idea: Бизнес-идея

        Returns:
            Dict: Breakdown по компонентам
        """
        components = {
            "revenue_potential": self._calculate_revenue_score(idea),
            "feasibility": self._calculate_feasibility_score(idea),
            "competition": self._calculate_competition_score(idea),
            "market_size": self._calculate_market_score(idea),
            "trend_strength": self._calculate_trend_score(idea)
        }

        weighted_components = {
            key: {
                "raw_score": score,
                "weight": self.weights[key],
                "weighted_score": round(score * self.weights[key] / 100, 2)
            }
            for key, score in components.items()
        }

        total = sum(c["weighted_score"] for c in weighted_components.values())

        return {
            "components": weighted_components,
            "total_score": int(round(total)),
            "weights": self.weights
        }

    def compare_ideas(
        self,
        idea1: Dict[str, Any],
        idea2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Сравнить две идеи.

        Args:
            idea1: Первая идея
            idea2: Вторая идея

        Returns:
            Dict: Сравнение
        """
        score1 = self.calculate_priority(idea1)
        score2 = self.calculate_priority(idea2)

        explanation1 = self.get_priority_explanation(idea1)
        explanation2 = self.get_priority_explanation(idea2)

        return {
            "idea1": {
                "name": idea1.get("name", "Idea 1"),
                "score": score1,
                "breakdown": explanation1
            },
            "idea2": {
                "name": idea2.get("name", "Idea 2"),
                "score": score2,
                "breakdown": explanation2
            },
            "winner": idea1.get("name") if score1 > score2 else idea2.get("name"),
            "score_difference": abs(score1 - score2)
        }


# Пример использования
if __name__ == "__main__":
    prioritizer = IdeaPrioritizer()

    # Пример идеи
    idea = {
        "name": "TaskFlow AI",
        "revenue_potential": "$20k-100k/mo",
        "technical_complexity": "medium",
        "time_to_mvp_weeks": 6,
        "competition_level": "medium",
        "competition_score": 70,
        "market_size": "large",
        "trend_score": 85
    }

    # Рассчитываем priority
    priority = prioritizer.calculate_priority(idea)
    print(f"Priority Score: {priority}/100")

    # Детальное объяснение
    explanation = prioritizer.get_priority_explanation(idea)
    print("\nPriority Breakdown:")
    for component, data in explanation["components"].items():
        print(f"  {component}: {data['raw_score']} × {data['weight']}% = {data['weighted_score']}")
    print(f"\nTotal: {explanation['total_score']}/100")

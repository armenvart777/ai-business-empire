"""
Trend Scorer - оценка потенциала трендов.

Рассчитывает score от 0 до 100 на основе различных факторов.
"""

from typing import Dict, Any
import logging


logger = logging.getLogger(__name__)


class TrendScorer:
    """
    Оценка потенциала трендов.

    Факторы оценки:
    - Популярность (interest, votes, upvotes)
    - Размер рынка
    - Engagement (комментарии, шеры)
    - Категория (некоторые категории более перспективны)
    - Новизна
    """

    def __init__(self):
        """Инициализация scorer."""
        # Веса для разных факторов (сумма = 100)
        self.weights = {
            "popularity": 30,      # Популярность
            "engagement": 25,      # Вовлеченность
            "market_size": 20,     # Размер рынка
            "category": 15,        # Категория
            "novelty": 10          # Новизна
        }

        # Категории с высоким потенциалом
        self.high_potential_categories = [
            "technology",
            "health",
            "finance",
            "education",
            "productivity"
        ]

    def calculate_score(self, trend: Dict[str, Any]) -> int:
        """
        Рассчитать общий score тренда.

        Args:
            trend: Данные о тренде

        Returns:
            int: Score от 0 до 100
        """
        source = trend.get("source", "unknown")

        # Рассчитываем компоненты score
        popularity_score = self._calculate_popularity_score(trend, source)
        engagement_score = self._calculate_engagement_score(trend, source)
        market_size_score = self._calculate_market_size_score(trend)
        category_score = self._calculate_category_score(trend)
        novelty_score = self._calculate_novelty_score(trend)

        # Взвешенная сумма
        total_score = (
            popularity_score * self.weights["popularity"] / 100 +
            engagement_score * self.weights["engagement"] / 100 +
            market_size_score * self.weights["market_size"] / 100 +
            category_score * self.weights["category"] / 100 +
            novelty_score * self.weights["novelty"] / 100
        )

        # Округляем до целого
        final_score = int(round(total_score))

        logger.debug(
            f"Score breakdown: pop={popularity_score}, eng={engagement_score}, "
            f"market={market_size_score}, cat={category_score}, nov={novelty_score} "
            f"=> TOTAL={final_score}"
        )

        return final_score

    def _calculate_popularity_score(
        self,
        trend: Dict[str, Any],
        source: str
    ) -> int:
        """Оценка популярности (0-100)."""
        if source == "google_trends":
            # Interest от Google Trends (0-100)
            interest = trend.get("interest", 0)
            return min(interest, 100)

        elif source == "reddit":
            # Reddit score (upvotes)
            score = trend.get("score", 0)
            # Нормализуем: 1000+ upvotes = 100 points
            normalized = min((score / 1000) * 100, 100)
            return int(normalized)

        elif source == "product_hunt":
            # Product Hunt votes
            votes = trend.get("votes", 0)
            # Нормализуем: 500+ votes = 100 points
            normalized = min((votes / 500) * 100, 100)
            return int(normalized)

        return 50  # Default для неизвестных источников

    def _calculate_engagement_score(
        self,
        trend: Dict[str, Any],
        source: str
    ) -> int:
        """Оценка вовлеченности (0-100)."""
        if source == "reddit":
            # Количество комментариев
            comments = trend.get("num_comments", 0)
            # Нормализуем: 100+ comments = 100 points
            normalized = min((comments / 100) * 100, 100)
            return int(normalized)

        elif source == "product_hunt":
            # Votes относительно популярности
            votes = trend.get("votes", 0)
            # Высокая вовлеченность если много голосов
            normalized = min((votes / 300) * 100, 100)
            return int(normalized)

        elif source == "google_trends":
            # Количество related queries как proxy
            related = trend.get("related_queries", [])
            # 10+ related queries = высокая вовлеченность
            normalized = min((len(related) / 10) * 100, 100)
            return int(normalized)

        return 50  # Default

    def _calculate_market_size_score(self, trend: Dict[str, Any]) -> int:
        """Оценка размера рынка (0-100)."""
        market_size = trend.get("market_size", "unknown")

        market_size_map = {
            "large": 100,
            "medium": 70,
            "small": 40,
            "unknown": 50
        }

        return market_size_map.get(market_size, 50)

    def _calculate_category_score(self, trend: Dict[str, Any]) -> int:
        """Оценка категории (0-100)."""
        category = trend.get("category", "unknown")

        if category in self.high_potential_categories:
            return 90
        elif category == "unknown":
            return 50
        else:
            return 70  # Другие категории

    def _calculate_novelty_score(self, trend: Dict[str, Any]) -> int:
        """
        Оценка новизны (0-100).

        Более новые тренды получают более высокий score.
        """
        # Проверяем возраст тренда
        # Для простоты: все текущие тренды считаем новыми
        # В будущем можно добавить анализ временных рядов

        from datetime import datetime

        timestamp = trend.get("timestamp")
        if not timestamp:
            return 80  # Default для новых трендов

        try:
            trend_time = datetime.fromisoformat(timestamp)
            now = datetime.now()
            age_hours = (now - trend_time).total_seconds() / 3600

            # Тренды до 24 часов = 100 points
            # Старше 7 дней = 40 points
            if age_hours < 24:
                return 100
            elif age_hours < 48:
                return 90
            elif age_hours < 168:  # 7 days
                return 70
            else:
                return 40

        except:
            return 80

    def get_score_explanation(
        self,
        trend: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Получить детальное объяснение score.

        Args:
            trend: Данные о тренде

        Returns:
            Dict: Breakdown по компонентам score
        """
        source = trend.get("source", "unknown")

        components = {
            "popularity": self._calculate_popularity_score(trend, source),
            "engagement": self._calculate_engagement_score(trend, source),
            "market_size": self._calculate_market_size_score(trend),
            "category": self._calculate_category_score(trend),
            "novelty": self._calculate_novelty_score(trend)
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


# Пример использования
if __name__ == "__main__":
    scorer = TrendScorer()

    # Пример тренда
    example_trend = {
        "source": "reddit",
        "title": "Frustrated with project management tools",
        "score": 1200,  # upvotes
        "num_comments": 150,
        "category": "productivity",
        "market_size": "large",
        "timestamp": "2026-02-06T10:00:00"
    }

    # Рассчитываем score
    score = scorer.calculate_score(example_trend)
    print(f"Trend Score: {score}/100")

    # Получаем детальное объяснение
    explanation = scorer.get_score_explanation(example_trend)
    print("\nScore Breakdown:")
    for component, data in explanation["components"].items():
        print(f"  {component}: {data['raw_score']} × {data['weight']}% = {data['weighted_score']}")
    print(f"\nTotal: {explanation['total_score']}/100")

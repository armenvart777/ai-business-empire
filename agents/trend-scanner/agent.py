"""
Trend Scanner Agent - обнаружение новых трендов и бизнес-возможностей.

Функции:
- Мониторинг Google Trends
- Парсинг Reddit для выявления болей пользователей
- Анализ Product Hunt для новых продуктов
- Оценка потенциала каждого тренда
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

from agents.shared.template_agent import TemplateAgent, AgentConfig
from agents.trend-scanner.sources import (
    GoogleTrendsSource,
    RedditSource,
    ProductHuntSource
)
from agents.trend-scanner.analyzer import TrendAnalyzer
from agents.trend-scanner.scorer import TrendScorer


class TrendScannerAgent(TemplateAgent):
    """
    Trend Scanner Agent - находит новые тренды и возможности.

    Workflow:
    1. Сканировать источники (Google Trends, Reddit, Product Hunt)
    2. Собрать сырые данные о трендах
    3. Анализировать каждый тренд с помощью LLM
    4. Оценить потенциал (score 0-100)
    5. Сохранить в БД / JSON файл
    6. Отправить лучшие тренды в Business Generator
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Инициализация Trend Scanner агента.

        Args:
            config: Конфигурация агента (если None - использует дефолтную)
        """
        config = config or AgentConfig(
            name="trend-scanner",
            llm_model="claude-haiku-3-5-20241022",  # Дешевая модель для анализа
            temperature=0.3,  # Меньше креативности, больше точности
            max_tokens=2000
        )
        super().__init__(config)

        # Источники данных
        self.google_trends = GoogleTrendsSource()
        self.reddit = RedditSource()
        self.product_hunt = ProductHuntSource()

        # Анализаторы
        self.analyzer = TrendAnalyzer(llm=self.llm)
        self.scorer = TrendScorer()

        # Путь для сохранения трендов
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "trends"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("Trend Scanner Agent initialized")

    async def scan_trends(
        self,
        sources: List[str] = ["google_trends", "reddit", "product_hunt"],
        min_score: int = 60,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Сканировать тренды из всех источников.

        Args:
            sources: Список источников для сканирования
            min_score: Минимальный score для фильтрации трендов
            limit: Максимальное количество трендов

        Returns:
            List[Dict]: Список найденных трендов с метриками
        """
        self.logger.info(f"Starting trend scan from sources: {sources}")

        # Собираем данные из всех источников параллельно
        tasks = []

        if "google_trends" in sources:
            tasks.append(self._scan_google_trends())
        if "reddit" in sources:
            tasks.append(self._scan_reddit())
        if "product_hunt" in sources:
            tasks.append(self._scan_product_hunt())

        # Ждем все результаты
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Объединяем все тренды
        all_trends = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Error scanning source: {result}")
                continue
            all_trends.extend(result)

        self.logger.info(f"Collected {len(all_trends)} raw trends")

        # Анализируем и оцениваем каждый тренд
        analyzed_trends = await self._analyze_trends(all_trends)

        # Фильтруем по score
        filtered_trends = [
            trend for trend in analyzed_trends
            if trend.get("score", 0) >= min_score
        ]

        # Сортируем по score (лучшие первые)
        sorted_trends = sorted(
            filtered_trends,
            key=lambda x: x.get("score", 0),
            reverse=True
        )[:limit]

        # Сохраняем результаты
        await self._save_trends(sorted_trends)

        self.logger.info(f"Found {len(sorted_trends)} high-quality trends (score >= {min_score})")

        return sorted_trends

    async def _scan_google_trends(self) -> List[Dict[str, Any]]:
        """Сканировать Google Trends."""
        self.logger.info("Scanning Google Trends...")

        try:
            # Получаем trending searches за последние 24 часа
            trends = await self.google_trends.get_trending_searches(
                geo="US",  # США
                timeframe="now 1-d"
            )

            # Получаем related queries для каждого тренда
            enriched_trends = []
            for trend in trends[:10]:  # Берем топ-10
                related = await self.google_trends.get_related_queries(trend["query"])

                enriched_trends.append({
                    "source": "google_trends",
                    "query": trend["query"],
                    "interest": trend.get("interest", 0),
                    "related_queries": related,
                    "timestamp": datetime.now().isoformat()
                })

            return enriched_trends

        except Exception as e:
            self.logger.error(f"Error scanning Google Trends: {e}")
            return []

    async def _scan_reddit(self) -> List[Dict[str, Any]]:
        """Сканировать Reddit для выявления болей пользователей."""
        self.logger.info("Scanning Reddit...")

        try:
            # Subreddits для мониторинга
            subreddits = [
                "SaaS",
                "Entrepreneur",
                "startups",
                "indiehackers",
                "digitalnomad",
                "passive_income"
            ]

            all_posts = []

            for subreddit in subreddits:
                # Получаем топ-посты за последний день
                posts = await self.reddit.get_top_posts(
                    subreddit=subreddit,
                    time_filter="day",
                    limit=10
                )

                # Фильтруем посты с болями/проблемами
                for post in posts:
                    # Ищем ключевые слова
                    keywords = ["problem", "frustrat", "need", "wish", "how to", "help"]
                    if any(keyword in post["title"].lower() for keyword in keywords):
                        all_posts.append({
                            "source": "reddit",
                            "subreddit": subreddit,
                            "title": post["title"],
                            "text": post.get("selftext", ""),
                            "score": post["score"],
                            "num_comments": post["num_comments"],
                            "url": post["url"],
                            "timestamp": datetime.now().isoformat()
                        })

            return all_posts

        except Exception as e:
            self.logger.error(f"Error scanning Reddit: {e}")
            return []

    async def _scan_product_hunt(self) -> List[Dict[str, Any]]:
        """Сканировать Product Hunt для новых продуктов."""
        self.logger.info("Scanning Product Hunt...")

        try:
            # Получаем продукты за последний день
            products = await self.product_hunt.get_recent_products(days=1)

            trends = []
            for product in products[:20]:  # Топ-20
                trends.append({
                    "source": "product_hunt",
                    "name": product["name"],
                    "tagline": product["tagline"],
                    "description": product.get("description", ""),
                    "votes": product.get("votes", 0),
                    "topics": product.get("topics", []),
                    "url": product["url"],
                    "timestamp": datetime.now().isoformat()
                })

            return trends

        except Exception as e:
            self.logger.error(f"Error scanning Product Hunt: {e}")
            return []

    async def _analyze_trends(
        self,
        trends: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Анализировать тренды с помощью LLM.

        Для каждого тренда:
        1. Определить категорию
        2. Выявить боль пользователей
        3. Оценить размер рынка
        4. Предложить бизнес-идеи
        5. Рассчитать score (0-100)
        """
        self.logger.info(f"Analyzing {len(trends)} trends with LLM...")

        analyzed = []

        # Анализируем параллельно (батчами по 5)
        batch_size = 5
        for i in range(0, len(trends), batch_size):
            batch = trends[i:i+batch_size]

            tasks = [
                self._analyze_single_trend(trend)
                for trend in batch
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    self.logger.error(f"Error analyzing trend: {result}")
                    continue
                if result:
                    analyzed.append(result)

        return analyzed

    async def _analyze_single_trend(
        self,
        trend: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Анализ одного тренда."""
        try:
            # Создаем промпт для LLM
            prompt = self._create_analysis_prompt(trend)

            # Вызываем LLM
            response = await self.llm.generate(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.3
            )

            # Парсим ответ (ожидаем JSON)
            analysis = json.loads(response)

            # Добавляем метаданные
            trend["analysis"] = analysis
            trend["category"] = analysis.get("category", "unknown")
            trend["user_pain"] = analysis.get("user_pain", "")
            trend["market_size"] = analysis.get("market_size", "unknown")
            trend["business_ideas"] = analysis.get("business_ideas", [])

            # Рассчитываем score
            trend["score"] = self.scorer.calculate_score(trend)

            return trend

        except Exception as e:
            self.logger.error(f"Error analyzing trend: {e}")
            return None

    def _create_analysis_prompt(self, trend: Dict[str, Any]) -> str:
        """Создать промпт для анализа тренда."""
        source = trend.get("source", "unknown")

        if source == "google_trends":
            context = f"""
Query: {trend.get("query", "")}
Interest Level: {trend.get("interest", 0)}
Related Queries: {", ".join(trend.get("related_queries", [])[:5])}
"""
        elif source == "reddit":
            context = f"""
Subreddit: r/{trend.get("subreddit", "")}
Title: {trend.get("title", "")}
Text: {trend.get("text", "")[:500]}
Upvotes: {trend.get("score", 0)}
Comments: {trend.get("num_comments", 0)}
"""
        elif source == "product_hunt":
            context = f"""
Product: {trend.get("name", "")}
Tagline: {trend.get("tagline", "")}
Description: {trend.get("description", "")[:500]}
Votes: {trend.get("votes", 0)}
Topics: {", ".join(trend.get("topics", []))}
"""
        else:
            context = str(trend)

        prompt = f"""Analyze this trend and identify business opportunities.

Source: {source}
{context}

Provide analysis in JSON format:

{{
  "category": "technology/health/finance/lifestyle/education/other",
  "user_pain": "What problem/pain point does this reveal?",
  "market_size": "small/medium/large",
  "target_audience": "Who would be interested?",
  "business_ideas": [
    "Idea 1: Brief description",
    "Idea 2: Brief description",
    "Idea 3: Brief description"
  ],
  "reasoning": "Why is this a good opportunity?"
}}

Be concise and focus on actionable insights."""

        return prompt

    async def _save_trends(self, trends: List[Dict[str, Any]]) -> None:
        """Сохранить тренды в файл."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / f"trends_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(trends, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Saved {len(trends)} trends to {filename}")

        # Также сохраняем в latest.json для удобства
        latest_file = self.data_dir / "latest.json"
        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(trends, f, indent=2, ensure_ascii=False)

    async def get_top_trends(
        self,
        limit: int = 10,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить топ-тренды из последнего скана.

        Args:
            limit: Количество трендов
            category: Фильтр по категории (опционально)

        Returns:
            List[Dict]: Список топ-трендов
        """
        latest_file = self.data_dir / "latest.json"

        if not latest_file.exists():
            self.logger.warning("No trends found. Run scan_trends() first.")
            return []

        with open(latest_file, "r", encoding="utf-8") as f:
            trends = json.load(f)

        # Фильтр по категории
        if category:
            trends = [t for t in trends if t.get("category") == category]

        return trends[:limit]


# Пример использования
if __name__ == "__main__":
    async def main():
        # Создаем агента
        agent = TrendScannerAgent()

        # Запускаем сканирование
        trends = await agent.scan_trends(
            sources=["google_trends", "reddit", "product_hunt"],
            min_score=60,
            limit=20
        )

        print(f"\n=== Found {len(trends)} High-Quality Trends ===\n")

        for i, trend in enumerate(trends[:5], 1):
            print(f"{i}. [{trend['source']}] Score: {trend['score']}")
            print(f"   Category: {trend.get('category', 'N/A')}")
            print(f"   Pain: {trend.get('user_pain', 'N/A')[:100]}...")
            print(f"   Ideas: {len(trend.get('business_ideas', []))} ideas generated")
            print()

    # Запуск
    asyncio.run(main())

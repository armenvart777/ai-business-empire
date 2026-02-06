"""
Business Generator Agent - генерация бизнес-идей из трендов.

Функции:
- Анализ трендов от Trend Scanner
- Генерация 3-5 SaaS идей на каждый тренд
- Оценка сложности реализации
- Расчет потенциальной прибыльности
- Приоритизация идей
- Валидация через поиск конкурентов
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

from agents.shared.template_agent import TemplateAgent, AgentConfig
from agents.business_generator.idea_generator import IdeaGenerator
from agents.business_generator.validator import IdeaValidator
from agents.business_generator.prioritizer import IdeaPrioritizer


class BusinessGeneratorAgent(TemplateAgent):
    """
    Business Generator Agent - создает бизнес-идеи из трендов.

    Workflow:
    1. Получить тренды от Trend Scanner
    2. Для каждого тренда сгенерировать 3-5 бизнес-идей
    3. Оценить каждую идею (сложность, прибыльность, конкуренция)
    4. Валидировать через поиск конкурентов
    5. Приоритизировать идеи (score 0-100)
    6. Сохранить топ-идеи в БД/JSON
    7. Отправить лучшие идеи в Developer Agent
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Инициализация Business Generator агента.

        Args:
            config: Конфигурация агента
        """
        config = config or AgentConfig(
            name="business-generator",
            llm_model="claude-sonnet-3-5-20241022",  # Более мощная модель для генерации идей
            temperature=0.7,  # Больше креативности
            max_tokens=3000
        )
        super().__init__(config)

        # Компоненты
        self.idea_generator = IdeaGenerator(llm=self.llm)
        self.validator = IdeaValidator()
        self.prioritizer = IdeaPrioritizer()

        # Путь для сохранения идей
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "businesses"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("Business Generator Agent initialized")

    async def generate_business_ideas(
        self,
        trends: List[Dict[str, Any]],
        ideas_per_trend: int = 5,
        min_priority_score: int = 70,
        validate_competition: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Генерация бизнес-идей из трендов.

        Args:
            trends: Список трендов от Trend Scanner
            ideas_per_trend: Сколько идей генерировать на тренд
            min_priority_score: Минимальный priority score для фильтрации
            validate_competition: Проверять конкурентов

        Returns:
            List[Dict]: Список бизнес-идей с метриками
        """
        self.logger.info(f"Generating business ideas from {len(trends)} trends")

        all_ideas = []

        # Генерируем идеи для каждого тренда
        for i, trend in enumerate(trends, 1):
            self.logger.info(f"Processing trend {i}/{len(trends)}: {trend.get('query', trend.get('title', 'N/A'))[:50]}")

            # Генерируем идеи
            ideas = await self._generate_ideas_for_trend(
                trend=trend,
                num_ideas=ideas_per_trend
            )

            # Валидируем через поиск конкурентов
            if validate_competition:
                ideas = await self._validate_ideas(ideas)

            # Добавляем в общий список
            all_ideas.extend(ideas)

        self.logger.info(f"Generated {len(all_ideas)} total business ideas")

        # Приоритизируем все идеи
        prioritized_ideas = await self._prioritize_ideas(all_ideas)

        # Фильтруем по priority score
        filtered_ideas = [
            idea for idea in prioritized_ideas
            if idea.get("priority_score", 0) >= min_priority_score
        ]

        # Сортируем по priority score (лучшие первые)
        sorted_ideas = sorted(
            filtered_ideas,
            key=lambda x: x.get("priority_score", 0),
            reverse=True
        )

        # Сохраняем результаты
        await self._save_ideas(sorted_ideas)

        self.logger.info(
            f"Found {len(sorted_ideas)} high-priority ideas "
            f"(score >= {min_priority_score})"
        )

        return sorted_ideas

    async def _generate_ideas_for_trend(
        self,
        trend: Dict[str, Any],
        num_ideas: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Генерация бизнес-идей для одного тренда.

        Args:
            trend: Данные о тренде
            num_ideas: Количество идей

        Returns:
            List[Dict]: Список идей
        """
        try:
            # Генерируем идеи с помощью LLM
            ideas = await self.idea_generator.generate(
                trend=trend,
                num_ideas=num_ideas
            )

            # Добавляем метаданные
            for idea in ideas:
                idea["trend_source"] = trend.get("source", "unknown")
                idea["trend_query"] = trend.get("query", trend.get("title", ""))
                idea["trend_score"] = trend.get("score", 0)
                idea["generated_at"] = datetime.now().isoformat()

            return ideas

        except Exception as e:
            self.logger.error(f"Error generating ideas for trend: {e}")
            return []

    async def _validate_ideas(
        self,
        ideas: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Валидация идей через поиск конкурентов.

        Args:
            ideas: Список идей

        Returns:
            List[Dict]: Идеи с добавленными данными о конкуренции
        """
        self.logger.info(f"Validating {len(ideas)} ideas...")

        validated = []

        # Валидируем параллельно (батчами по 3)
        batch_size = 3
        for i in range(0, len(ideas), batch_size):
            batch = ideas[i:i+batch_size]

            tasks = [
                self.validator.validate(idea)
                for idea in batch
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for idea, validation in zip(batch, results):
                if isinstance(validation, Exception):
                    self.logger.error(f"Error validating idea: {validation}")
                    validated.append(idea)
                    continue

                # Добавляем данные валидации
                idea.update(validation)
                validated.append(idea)

        return validated

    async def _prioritize_ideas(
        self,
        ideas: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Приоритизация идей на основе метрик.

        Args:
            ideas: Список идей

        Returns:
            List[Dict]: Идеи с priority_score
        """
        self.logger.info(f"Prioritizing {len(ideas)} ideas...")

        prioritized = []

        for idea in ideas:
            # Рассчитываем priority score
            priority_score = self.prioritizer.calculate_priority(idea)
            idea["priority_score"] = priority_score

            # Получаем объяснение score
            explanation = self.prioritizer.get_priority_explanation(idea)
            idea["priority_explanation"] = explanation

            prioritized.append(idea)

        return prioritized

    async def _save_ideas(self, ideas: List[Dict[str, Any]]) -> None:
        """Сохранить бизнес-идеи в файл."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / f"ideas_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(ideas, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Saved {len(ideas)} ideas to {filename}")

        # Также сохраняем в latest.json
        latest_file = self.data_dir / "latest.json"
        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(ideas, f, indent=2, ensure_ascii=False)

    async def get_top_ideas(
        self,
        limit: int = 10,
        category: Optional[str] = None,
        max_complexity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить топ бизнес-идеи из последней генерации.

        Args:
            limit: Количество идей
            category: Фильтр по категории
            max_complexity: Максимальная сложность (low/medium/high)

        Returns:
            List[Dict]: Топ-идеи
        """
        latest_file = self.data_dir / "latest.json"

        if not latest_file.exists():
            self.logger.warning("No ideas found. Run generate_business_ideas() first.")
            return []

        with open(latest_file, "r", encoding="utf-8") as f:
            ideas = json.load(f)

        # Фильтры
        if category:
            ideas = [i for i in ideas if i.get("category") == category]

        if max_complexity:
            complexity_order = {"low": 1, "medium": 2, "high": 3}
            max_level = complexity_order.get(max_complexity, 3)
            ideas = [
                i for i in ideas
                if complexity_order.get(i.get("technical_complexity", "high"), 3) <= max_level
            ]

        return ideas[:limit]

    async def approve_idea(self, idea_id: str) -> Dict[str, Any]:
        """
        Одобрить идею для разработки.

        Args:
            idea_id: ID идеи

        Returns:
            Dict: Данные одобренной идеи
        """
        latest_file = self.data_dir / "latest.json"

        with open(latest_file, "r", encoding="utf-8") as f:
            ideas = json.load(f)

        # Находим идею
        idea = next((i for i in ideas if i.get("id") == idea_id), None)

        if not idea:
            raise ValueError(f"Idea {idea_id} not found")

        # Помечаем как одобренную
        idea["approved"] = True
        idea["approved_at"] = datetime.now().isoformat()
        idea["status"] = "approved"

        # Сохраняем
        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(ideas, f, indent=2, ensure_ascii=False)

        # Также сохраняем в отдельный файл одобренных
        approved_dir = self.data_dir / "approved"
        approved_dir.mkdir(exist_ok=True)

        approved_file = approved_dir / f"{idea_id}.json"
        with open(approved_file, "w", encoding="utf-8") as f:
            json.dump(idea, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Idea {idea_id} approved for development")

        return idea

    async def get_approved_ideas(self) -> List[Dict[str, Any]]:
        """
        Получить все одобренные идеи.

        Returns:
            List[Dict]: Одобренные идеи
        """
        approved_dir = self.data_dir / "approved"

        if not approved_dir.exists():
            return []

        ideas = []
        for file_path in approved_dir.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                idea = json.load(f)
                ideas.append(idea)

        # Сортируем по дате одобрения
        ideas.sort(key=lambda x: x.get("approved_at", ""), reverse=True)

        return ideas


# Пример использования
if __name__ == "__main__":
    async def main():
        # Создаем агента
        agent = BusinessGeneratorAgent()

        # Пример трендов (обычно приходят от Trend Scanner)
        example_trends = [
            {
                "source": "reddit",
                "query": "project management frustration",
                "score": 85,
                "category": "productivity",
                "user_pain": "Complex PM tools are overwhelming for small teams",
                "market_size": "large",
                "target_audience": "Freelancers and small teams"
            },
            {
                "source": "google_trends",
                "query": "ai content writing",
                "score": 78,
                "category": "technology",
                "user_pain": "Writers need help with consistency and speed",
                "market_size": "large",
                "target_audience": "Content creators and marketers"
            }
        ]

        # Генерируем бизнес-идеи
        ideas = await agent.generate_business_ideas(
            trends=example_trends,
            ideas_per_trend=5,
            min_priority_score=70,
            validate_competition=True
        )

        print(f"\n=== Generated {len(ideas)} High-Priority Business Ideas ===\n")

        for i, idea in enumerate(ideas[:5], 1):
            print(f"{i}. {idea['name']}")
            print(f"   Tagline: {idea['tagline']}")
            print(f"   Priority Score: {idea['priority_score']}/100")
            print(f"   Complexity: {idea['technical_complexity']}")
            print(f"   Revenue Potential: ${idea.get('revenue_potential', 'N/A')}/mo")
            print(f"   Competition: {idea.get('competition_level', 'N/A')}")
            print()

    # Запуск
    asyncio.run(main())

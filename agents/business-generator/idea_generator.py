"""
Idea Generator - генерация бизнес-идей с помощью LLM.

Использует продвинутые промпты для генерации качественных SaaS идей.
"""

import json
import logging
from typing import List, Dict, Any
import uuid


logger = logging.getLogger(__name__)


class IdeaGenerator:
    """
    Генератор бизнес-идей с помощью LLM.

    Генерирует детальные бизнес-идеи на основе трендов.
    """

    def __init__(self, llm):
        """
        Инициализация генератора.

        Args:
            llm: LLM клиент
        """
        self.llm = llm

    async def generate(
        self,
        trend: Dict[str, Any],
        num_ideas: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Генерация бизнес-идей для тренда.

        Args:
            trend: Данные о тренде
            num_ideas: Количество идей

        Returns:
            List[Dict]: Список бизнес-идей
        """
        try:
            prompt = self._create_prompt(trend, num_ideas)

            response = await self.llm.generate(
                prompt=prompt,
                max_tokens=3000,
                temperature=0.7  # Больше креативности
            )

            # Парсим ответ
            ideas = self._parse_response(response)

            # Добавляем ID
            for idea in ideas:
                idea["id"] = str(uuid.uuid4())
                idea["status"] = "generated"

            logger.info(f"Generated {len(ideas)} ideas for trend")
            return ideas

        except Exception as e:
            logger.error(f"Error generating ideas: {e}")
            return []

    def _create_prompt(self, trend: Dict[str, Any], num_ideas: int) -> str:
        """Создать промпт для генерации идей."""

        # Контекст о тренде
        trend_context = f"""
**Trend Information:**
- Source: {trend.get('source', 'N/A')}
- Query/Title: {trend.get('query', trend.get('title', 'N/A'))}
- Category: {trend.get('category', 'N/A')}
- User Pain: {trend.get('user_pain', 'N/A')}
- Target Audience: {trend.get('target_audience', 'N/A')}
- Market Size: {trend.get('market_size', 'N/A')}
- Trend Score: {trend.get('score', 0)}/100
"""

        # Основной промпт
        prompt = f"""You are an expert SaaS product strategist. Generate {num_ideas} actionable business ideas based on this trend.

{trend_context}

For each idea, provide:

1. **Name**: Catchy product name (2-3 words)
2. **Tagline**: One-sentence value proposition
3. **Description**: What does it do? (2-3 sentences)
4. **Target Audience**: Specific user persona
5. **Key Features**: 3-5 core features
6. **Revenue Model**: How it makes money (subscription/freemium/one-time/marketplace)
7. **Pricing**: Suggested pricing (e.g., "$29/month", "Free + $99/month Pro")
8. **Technical Complexity**: low/medium/high
9. **Time to MVP**: Estimated weeks
10. **Revenue Potential**: Estimated monthly revenue at scale ($X-Y/mo)
11. **Unique Angle**: What makes this different from competitors?
12. **Go-to-Market**: How to acquire first 100 users?

Return as JSON array:

```json
[
  {{
    "name": "ProductName",
    "tagline": "One sentence value prop",
    "description": "Detailed description...",
    "target_audience": "Specific persona",
    "key_features": [
      "Feature 1",
      "Feature 2",
      "Feature 3"
    ],
    "revenue_model": "subscription",
    "pricing": "$29/month",
    "technical_complexity": "medium",
    "time_to_mvp_weeks": 4,
    "revenue_potential": "$10k-50k/mo",
    "unique_angle": "What makes it special",
    "go_to_market": "How to get first users",
    "category": "{trend.get('category', 'unknown')}"
  }}
]
```

Requirements:
- Focus on digital/SaaS products (not physical)
- Ideas should be MVP-able in 2-8 weeks
- Realistic revenue potential
- Clear differentiation
- Specific, not generic
- Actionable from day 1

Generate {num_ideas} diverse ideas with different approaches to solving the user pain."""

        return prompt

    def _parse_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Парсинг ответа от LLM.

        Args:
            response: Ответ от LLM

        Returns:
            List[Dict]: Список идей
        """
        try:
            # Извлекаем JSON из ответа
            # Ищем JSON array
            start_idx = response.find('[')
            end_idx = response.rfind(']')

            if start_idx == -1 or end_idx == -1:
                raise ValueError("No JSON array found in response")

            json_str = response[start_idx:end_idx+1]
            ideas = json.loads(json_str)

            # Валидация обязательных полей
            required_fields = [
                "name",
                "tagline",
                "description",
                "target_audience",
                "key_features",
                "revenue_model"
            ]

            validated_ideas = []
            for idea in ideas:
                # Проверяем обязательные поля
                if all(field in idea for field in required_fields):
                    # Нормализуем данные
                    idea["technical_complexity"] = idea.get("technical_complexity", "medium").lower()
                    idea["time_to_mvp_weeks"] = int(idea.get("time_to_mvp_weeks", 4))

                    validated_ideas.append(idea)
                else:
                    logger.warning(f"Idea missing required fields: {idea.get('name', 'Unknown')}")

            return validated_ideas

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.debug(f"Response was: {response}")
            return []

    async def refine_idea(
        self,
        idea: Dict[str, Any],
        feedback: str
    ) -> Dict[str, Any]:
        """
        Уточнение идеи на основе feedback.

        Args:
            idea: Существующая идея
            feedback: Feedback от пользователя

        Returns:
            Dict: Уточненная идея
        """
        prompt = f"""Refine this business idea based on feedback.

**Current Idea:**
Name: {idea['name']}
Tagline: {idea['tagline']}
Description: {idea['description']}

**Feedback:**
{feedback}

Provide a refined version with improvements. Return as JSON with the same structure.
Keep what works, improve what doesn't based on the feedback."""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.6
            )

            refined = self._parse_response(response)
            if refined:
                refined[0]["id"] = idea["id"]  # Keep same ID
                refined[0]["refined"] = True
                refined[0]["original_idea"] = idea
                return refined[0]

            return idea

        except Exception as e:
            logger.error(f"Error refining idea: {e}")
            return idea


# Пример использования
if __name__ == "__main__":
    import asyncio

    async def main():
        # Mock LLM для тестирования
        class MockLLM:
            async def generate(self, prompt: str, **kwargs):
                return """
```json
[
  {
    "name": "TaskFlow AI",
    "tagline": "Project management that thinks for you",
    "description": "AI-powered project management tool that automatically organizes tasks, predicts deadlines, and suggests optimal workflows based on your team's patterns.",
    "target_audience": "Freelancers and teams of 2-10 people",
    "key_features": [
      "AI task prioritization",
      "Automatic deadline prediction",
      "Smart workflow suggestions",
      "Slack/Discord integration",
      "Beautiful minimal interface"
    ],
    "revenue_model": "freemium",
    "pricing": "Free for 5 projects, $19/month Pro",
    "technical_complexity": "medium",
    "time_to_mvp_weeks": 6,
    "revenue_potential": "$20k-100k/mo",
    "unique_angle": "Uses ML to learn from your team's actual behavior, not templates",
    "go_to_market": "Launch on Product Hunt, target indie hackers community, offer migration from complex tools",
    "category": "productivity"
  }
]
```
"""

        llm = MockLLM()
        generator = IdeaGenerator(llm)

        trend = {
            "query": "project management frustration",
            "category": "productivity",
            "user_pain": "Complex PM tools overwhelming",
            "target_audience": "Small teams",
            "market_size": "large",
            "score": 85
        }

        ideas = await generator.generate(trend, num_ideas=1)

        if ideas:
            idea = ideas[0]
            print(f"Generated Idea: {idea['name']}")
            print(f"Tagline: {idea['tagline']}")
            print(f"Features: {', '.join(idea['key_features'])}")
            print(f"Pricing: {idea['pricing']}")
            print(f"Revenue Potential: {idea['revenue_potential']}")

    asyncio.run(main())

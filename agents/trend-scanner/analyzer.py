"""
Trend Analyzer - анализ трендов с помощью LLM.

Использует LLM для глубокого анализа каждого тренда.
"""

from typing import Dict, Any, Optional
import json
import logging


logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """
    Анализатор трендов с помощью LLM.

    Функции:
    - Определение категории
    - Выявление проблем пользователей
    - Оценка размера рынка
    - Генерация бизнес-идей
    """

    def __init__(self, llm):
        """
        Инициализация analyzer.

        Args:
            llm: LLM клиент (из template_agent)
        """
        self.llm = llm

    async def analyze(
        self,
        trend: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Анализ тренда с помощью LLM.

        Args:
            trend: Данные о тренде

        Returns:
            Dict: Результаты анализа
        """
        try:
            prompt = self._create_prompt(trend)

            response = await self.llm.generate(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.3
            )

            # Парсим JSON ответ
            analysis = self._parse_response(response)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing trend: {e}")
            return None

    def _create_prompt(self, trend: Dict[str, Any]) -> str:
        """Создать промпт для LLM."""
        source = trend.get("source", "unknown")

        # Формируем контекст в зависимости от источника
        if source == "google_trends":
            context = f"""
**Google Trends Data:**
- Search Query: "{trend.get('query', '')}"
- Interest Level: {trend.get('interest', 0)}/100
- Related Queries: {', '.join(trend.get('related_queries', [])[:5])}
"""

        elif source == "reddit":
            context = f"""
**Reddit Post:**
- Subreddit: r/{trend.get('subreddit', '')}
- Title: "{trend.get('title', '')}"
- Text: {trend.get('text', '')[:500]}
- Engagement: {trend.get('score', 0)} upvotes, {trend.get('num_comments', 0)} comments
"""

        elif source == "product_hunt":
            context = f"""
**Product Hunt:**
- Product Name: {trend.get('name', '')}
- Tagline: {trend.get('tagline', '')}
- Description: {trend.get('description', '')[:500]}
- Votes: {trend.get('votes', 0)}
- Topics: {', '.join(trend.get('topics', []))}
"""

        else:
            context = f"**Data:** {json.dumps(trend, indent=2)}"

        # Основной промпт
        prompt = f"""You are a business analyst identifying opportunities from market trends.

{context}

Analyze this trend and provide insights in JSON format:

{{
  "category": "<choose one: technology/health/finance/lifestyle/education/ecommerce/productivity/entertainment/other>",
  "user_pain": "<what problem or pain point does this reveal? be specific>",
  "market_size": "<choose one: small/medium/large>",
  "target_audience": "<who would be most interested? be specific>",
  "business_ideas": [
    "<actionable SaaS or digital product idea 1>",
    "<actionable SaaS or digital product idea 2>",
    "<actionable SaaS or digital product idea 3>"
  ],
  "reasoning": "<why is this a good opportunity? 2-3 sentences>",
  "monetization": "<how could this be monetized? subscription/one-time/freemium/ads>",
  "competition_level": "<choose one: low/medium/high>",
  "technical_complexity": "<choose one: low/medium/high>"
}}

Requirements:
- Be specific and actionable
- Focus on digital/SaaS opportunities
- Consider competition and feasibility
- Provide realistic business ideas
- Keep it concise

Return ONLY valid JSON, no additional text."""

        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Парсинг ответа от LLM.

        Args:
            response: Ответ от LLM

        Returns:
            Dict: Спарсенные данные
        """
        try:
            # Попытка извлечь JSON из ответа
            # LLM иногда добавляет текст до/после JSON

            # Ищем JSON блок
            start_idx = response.find('{')
            end_idx = response.rfind('}')

            if start_idx == -1 or end_idx == -1:
                raise ValueError("No JSON found in response")

            json_str = response[start_idx:end_idx+1]
            analysis = json.loads(json_str)

            # Валидация обязательных полей
            required_fields = [
                "category",
                "user_pain",
                "market_size",
                "target_audience",
                "business_ideas"
            ]

            for field in required_fields:
                if field not in analysis:
                    logger.warning(f"Missing field in analysis: {field}")
                    analysis[field] = "unknown" if field != "business_ideas" else []

            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.debug(f"Response was: {response}")

            # Возвращаем default структуру
            return {
                "category": "unknown",
                "user_pain": "Could not analyze",
                "market_size": "unknown",
                "target_audience": "unknown",
                "business_ideas": [],
                "reasoning": "Analysis failed",
                "error": str(e)
            }

    async def batch_analyze(
        self,
        trends: list[Dict[str, Any]],
        batch_size: int = 5
    ) -> list[Dict[str, Any]]:
        """
        Анализ нескольких трендов батчами.

        Args:
            trends: Список трендов
            batch_size: Размер батча

        Returns:
            List[Dict]: Результаты анализа
        """
        import asyncio

        results = []

        for i in range(0, len(trends), batch_size):
            batch = trends[i:i+batch_size]

            # Анализируем батч параллельно
            tasks = [self.analyze(trend) for trend in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Добавляем результаты
            for trend, analysis in zip(batch, batch_results):
                if isinstance(analysis, Exception):
                    logger.error(f"Error analyzing trend: {analysis}")
                    continue

                if analysis:
                    # Объединяем данные тренда с анализом
                    trend.update({
                        "analysis": analysis,
                        "category": analysis.get("category", "unknown"),
                        "user_pain": analysis.get("user_pain", ""),
                        "market_size": analysis.get("market_size", "unknown"),
                        "target_audience": analysis.get("target_audience", ""),
                        "business_ideas": analysis.get("business_ideas", [])
                    })
                    results.append(trend)

        logger.info(f"Analyzed {len(results)} trends successfully")
        return results


# Пример использования
if __name__ == "__main__":
    import asyncio
    from agents.shared.template_agent import LLMClient

    async def main():
        # Mock LLM для тестирования
        class MockLLM:
            async def generate(self, prompt: str, **kwargs):
                return json.dumps({
                    "category": "productivity",
                    "user_pain": "Users struggle with managing multiple projects",
                    "market_size": "large",
                    "target_audience": "Freelancers and small teams",
                    "business_ideas": [
                        "AI-powered project tracker",
                        "Smart task automation tool",
                        "Team collaboration platform"
                    ],
                    "reasoning": "Large market with clear pain points",
                    "monetization": "subscription",
                    "competition_level": "medium",
                    "technical_complexity": "medium"
                })

        llm = MockLLM()
        analyzer = TrendAnalyzer(llm)

        # Пример тренда
        trend = {
            "source": "reddit",
            "title": "Frustrated with project management tools",
            "text": "All the tools are too complex...",
            "score": 500,
            "num_comments": 100
        }

        # Анализируем
        result = await analyzer.analyze(trend)
        print(json.dumps(result, indent=2))

    asyncio.run(main())

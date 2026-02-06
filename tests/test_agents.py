"""
Тесты для AI агентов.

Проверяем работу Trend Scanner и Business Generator.
"""

import asyncio
import json
from pathlib import Path
import sys

# Добавляем путь к agents в sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Mock LLM для тестирования без реальных API вызовов
class MockLLM:
    """Mock LLM клиент для тестов."""

    async def generate(self, prompt: str, **kwargs):
        """Генерация mock ответа."""

        # Определяем тип промпта и возвращаем соответствующий ответ
        if "trend" in prompt.lower() and "analyze" in prompt.lower():
            # Trend analysis
            return json.dumps({
                "category": "productivity",
                "user_pain": "Users struggle with complex project management tools",
                "market_size": "large",
                "target_audience": "Freelancers and small teams",
                "business_ideas": [
                    "Simple AI-powered task manager",
                    "No-code workflow automation",
                    "Smart deadline predictor"
                ],
                "reasoning": "Large underserved market with clear pain points"
            })

        elif "business idea" in prompt.lower() or "generate" in prompt.lower():
            # Business idea generation
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
    "go_to_market": "Launch on Product Hunt, target indie hackers community",
    "category": "productivity"
  },
  {
    "name": "FlowState",
    "tagline": "Focus time tracking with AI insights",
    "description": "Automatically tracks your focus time and provides AI-powered insights on when you're most productive. Helps you plan your day around your natural rhythms.",
    "target_audience": "Knowledge workers and creatives",
    "key_features": [
      "Automatic focus tracking",
      "AI productivity insights",
      "Calendar integration",
      "Focus mode with website blocking",
      "Daily/weekly reports"
    ],
    "revenue_model": "subscription",
    "pricing": "$9/month",
    "technical_complexity": "low",
    "time_to_mvp_weeks": 3,
    "revenue_potential": "$5k-20k/mo",
    "unique_angle": "Passive tracking without manual timers",
    "go_to_market": "Content marketing, SEO for 'productivity tracking'",
    "category": "productivity"
  }
]
```
"""

        return "Mock LLM response"


async def test_trend_scanner():
    """Тест Trend Scanner агента."""
    print("\n=== Testing Trend Scanner Agent ===\n")

    try:
        # Импорт с mock зависимостями
        from agents.trend_scanner.agent import TrendScannerAgent
        from agents.trend_scanner.scorer import TrendScorer

        # Создаем агента с mock LLM
        agent = TrendScannerAgent()
        agent.llm = MockLLM()

        print("✓ Trend Scanner Agent initialized")

        # Тест scorer
        scorer = TrendScorer()

        test_trend = {
            "source": "reddit",
            "score": 1200,
            "num_comments": 150,
            "category": "productivity",
            "market_size": "large",
            "timestamp": "2026-02-06T10:00:00"
        }

        score = scorer.calculate_score(test_trend)
        print(f"✓ Scorer working: {score}/100")

        # Тест анализа тренда
        from agents.trend_scanner.analyzer import TrendAnalyzer

        analyzer = TrendAnalyzer(llm=MockLLM())
        analysis = await analyzer.analyze(test_trend)

        if analysis:
            print(f"✓ Analyzer working: category={analysis.get('category', 'N/A')}")

        print("\n✅ Trend Scanner tests PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Trend Scanner tests FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_business_generator():
    """Тест Business Generator агента."""
    print("\n=== Testing Business Generator Agent ===\n")

    try:
        from agents.business_generator.agent import BusinessGeneratorAgent
        from agents.business_generator.idea_generator import IdeaGenerator
        from agents.business_generator.prioritizer import IdeaPrioritizer

        # Создаем агента с mock LLM
        agent = BusinessGeneratorAgent()
        agent.llm = MockLLM()
        agent.idea_generator.llm = MockLLM()

        print("✓ Business Generator Agent initialized")

        # Тест генерации идей
        generator = IdeaGenerator(llm=MockLLM())

        test_trend = {
            "query": "project management frustration",
            "category": "productivity",
            "user_pain": "Complex PM tools overwhelming",
            "market_size": "large",
            "score": 85
        }

        ideas = await generator.generate(test_trend, num_ideas=2)

        if ideas:
            print(f"✓ Generated {len(ideas)} ideas")
            print(f"  - {ideas[0]['name']}: {ideas[0]['tagline']}")

        # Тест prioritizer
        prioritizer = IdeaPrioritizer()

        test_idea = {
            "name": "TaskFlow AI",
            "revenue_potential": "$20k-100k/mo",
            "technical_complexity": "medium",
            "time_to_mvp_weeks": 6,
            "competition_level": "medium",
            "market_size": "large",
            "trend_score": 85
        }

        priority = prioritizer.calculate_priority(test_idea)
        print(f"✓ Prioritizer working: {priority}/100")

        print("\n✅ Business Generator tests PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Business Generator tests FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_integration():
    """Интеграционный тест: Trend Scanner → Business Generator."""
    print("\n=== Testing Integration (Trend Scanner → Business Generator) ===\n")

    try:
        # Mock тренды (как будто от Trend Scanner)
        mock_trends = [
            {
                "source": "reddit",
                "query": "project management frustration",
                "score": 85,
                "category": "productivity",
                "user_pain": "Complex PM tools overwhelming",
                "market_size": "large",
                "target_audience": "Small teams"
            }
        ]

        print(f"Input: {len(mock_trends)} trends")

        # Business Generator обрабатывает тренды
        from agents.business_generator.agent import BusinessGeneratorAgent

        agent = BusinessGeneratorAgent()
        agent.llm = MockLLM()
        agent.idea_generator.llm = MockLLM()

        ideas = await agent.generate_business_ideas(
            trends=mock_trends,
            ideas_per_trend=2,
            min_priority_score=0,  # Принимаем все для теста
            validate_competition=False  # Отключаем для быстрого теста
        )

        print(f"Output: {len(ideas)} business ideas generated")

        if ideas:
            for i, idea in enumerate(ideas[:2], 1):
                print(f"\n{i}. {idea['name']}")
                print(f"   Priority: {idea['priority_score']}/100")
                print(f"   Complexity: {idea['technical_complexity']}")
                print(f"   Revenue: {idea['revenue_potential']}")

        print("\n✅ Integration test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Запуск всех тестов."""
    print("=" * 60)
    print("AI AGENTS TEST SUITE")
    print("=" * 60)

    results = []

    # Тест 1: Trend Scanner
    results.append(await test_trend_scanner())

    # Тест 2: Business Generator
    results.append(await test_business_generator())

    # Тест 3: Integration
    results.append(await test_integration())

    # Итоги
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"\nPassed: {passed}/{total}")

    if all(results):
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

## Business Generator Agent

Агент для генерации бизнес-идей из трендов.

## Функции

- 💡 **Генерация идей** - 3-5 SaaS идей на каждый тренд
- 🔍 **Валидация** - поиск конкурентов и оценка рынка
- 📊 **Приоритизация** - score (0-100) для каждой идеи
- ✅ **Одобрение** - workflow для одобрения идей
- 🚀 **Интеграция** - передача идей в Developer Agent

## Установка

```bash
cd agents/business-generator
pip install -r requirements.txt
```

## Использование

### Базовое использование

```python
from agents.business_generator import BusinessGeneratorAgent

# Создаем агента
agent = BusinessGeneratorAgent()

# Получаем тренды (от Trend Scanner)
trends = [
    {
        "query": "project management frustration",
        "category": "productivity",
        "user_pain": "Complex PM tools overwhelming",
        "market_size": "large",
        "score": 85
    }
]

# Генерируем бизнес-идеи
ideas = await agent.generate_business_ideas(
    trends=trends,
    ideas_per_trend=5,
    min_priority_score=70,
    validate_competition=True
)

# Выводим результаты
for idea in ideas[:5]:
    print(f"{idea['name']}: {idea['priority_score']}/100")
    print(f"  {idea['tagline']}")
    print(f"  Revenue: {idea['revenue_potential']}")
    print(f"  Complexity: {idea['technical_complexity']}")
    print()
```

### Получить топ-идеи

```python
# Топ-10 идей
top_ideas = await agent.get_top_ideas(limit=10)

# Фильтр по категории
tech_ideas = await agent.get_top_ideas(
    limit=10,
    category="technology"
)

# Только простые идеи (low complexity)
simple_ideas = await agent.get_top_ideas(
    limit=10,
    max_complexity="low"
)
```

### Одобрить идею

```python
# Одобрить идею для разработки
idea = await agent.approve_idea(idea_id="abc-123")

# Получить все одобренные идеи
approved = await agent.get_approved_ideas()
```

## Архитектура

```
business-generator/
├── agent.py              # Основной класс BusinessGeneratorAgent
├── idea_generator.py     # Генерация идей с помощью LLM
├── validator.py          # Валидация через поиск конкурентов
├── prioritizer.py        # Приоритизация идей
├── requirements.txt      # Зависимости
└── README.md             # Документация
```

## Workflow

1. **Получить тренды** - от Trend Scanner Agent
2. **Генерация идей** - LLM создает 3-5 идей на тренд
3. **Валидация** - поиск конкурентов, анализ рынка
4. **Приоритизация** - расчет priority score (0-100)
5. **Фильтрация** - только идеи с score >= threshold
6. **Сохранение** - запись в JSON файлы
7. **Одобрение** - ручное или авто-одобрение топ-идей
8. **Передача** - одобренные идеи → Developer Agent

## Priority Scoring

Priority score (0-100) рассчитывается на основе 5 факторов:

| Фактор | Вес | Описание |
|--------|-----|----------|
| **Revenue Potential** | 30% | Потенциальный доход ($X/mo) |
| **Feasibility** | 25% | Простота реализации (complexity + time) |
| **Competition** | 20% | Уровень конкуренции |
| **Market Size** | 15% | Размер рынка (large/medium/small) |
| **Trend Strength** | 10% | Сила тренда (score от Trend Scanner) |

## Пример результата

```json
{
  "id": "abc-123-def-456",
  "name": "TaskFlow AI",
  "tagline": "Project management that thinks for you",
  "description": "AI-powered PM tool that learns from your team's patterns...",
  "target_audience": "Freelancers and teams of 2-10 people",
  "key_features": [
    "AI task prioritization",
    "Automatic deadline prediction",
    "Smart workflow suggestions"
  ],
  "revenue_model": "freemium",
  "pricing": "Free + $19/month Pro",
  "technical_complexity": "medium",
  "time_to_mvp_weeks": 6,
  "revenue_potential": "$20k-100k/mo",
  "unique_angle": "Uses ML to learn from actual behavior, not templates",
  "go_to_market": "Launch on Product Hunt, target indie hackers",

  "competitors_found": 2,
  "competition_level": "medium",
  "competition_score": 70,

  "priority_score": 82,
  "status": "generated",
  "generated_at": "2026-02-06T15:30:00"
}
```

## Сохранение данных

Идеи сохраняются в `data/businesses/`:

```
data/businesses/
├── ideas_20260206_153022.json     # Timestamped files
├── ideas_20260206_160115.json
├── latest.json                     # Последняя генерация
└── approved/                       # Одобренные идеи
    ├── abc-123.json
    └── def-456.json
```

## Интеграция с Trend Scanner

```python
from agents.trend_scanner import TrendScannerAgent
from agents.business_generator import BusinessGeneratorAgent

# Сканируем тренды
trend_agent = TrendScannerAgent()
trends = await trend_agent.scan_trends(min_score=60, limit=20)

# Генерируем идеи
business_agent = BusinessGeneratorAgent()
ideas = await business_agent.generate_business_ideas(
    trends=trends,
    ideas_per_trend=5,
    min_priority_score=70
)

print(f"Generated {len(ideas)} high-priority business ideas!")
```

## Генерация идей

### Промпт-инжиниринг

IdeaGenerator использует продвинутые промпты для генерации качественных идей:

- Конкретные требования (SaaS, digital продукты)
- MVP-able в 2-8 недель
- Реалистичный revenue potential
- Четкая дифференциация
- Go-to-market стратегия

### Refinement

Можно уточнить идею на основе feedback:

```python
idea = ideas[0]

refined_idea = await generator.refine_idea(
    idea=idea,
    feedback="Make it more focused on AI automation"
)
```

## Валидация

### Поиск конкурентов

Validator ищет существующие решения:

- Google Search (через SerpAPI)
- Product Hunt
- AlternativeTo
- Manual scraping

### Анализ конкуренции

- **Low competition**: 0-2 конкурента → score 90
- **Medium competition**: 3-5 конкурентов → score 70
- **High competition**: 6-10 конкурентов → score 40
- **Very high**: 10+ конкурентов → score 20

### Domain availability

```python
available = await validator.check_domain_available("taskflowai")

domains = validator.suggest_domain_names(idea, num=5)
# ['taskflowai.com', 'gettaskflowai.com', 'taskflowapp.com', ...]
```

## Стоимость

При использовании Claude Sonnet для генерации:

- **1 идея**: ~2000 tokens = $0.006
- **5 идей на тренд**: ~$0.03
- **20 трендов × 5 идей**: ~$3
- **Ежедневный запуск**: ~$90/месяц

Оптимизация:
- Используйте Claude Haiku для простых идей ($0.0008 на идею)
- Batch processing для снижения latency
- Кеширование повторных запросов

## Troubleshooting

### Генерация идей не работает

Проверьте LLM клиент:
```python
response = await agent.llm.generate("Test prompt")
print(response)
```

### Валидация не находит конкурентов

Настройте API ключи для поиска (SerpAPI, Google Custom Search).

### Priority scores слишком низкие

Настройте веса в prioritizer:
```python
prioritizer = IdeaPrioritizer()
prioritizer.weights["revenue_potential"] = 40  # Увеличить вес revenue
```

## TODO

- [ ] Интеграция с Google Search API для поиска конкурентов
- [ ] Автоматическая проверка доступности доменов
- [ ] ML модель для предсказания успеха идей
- [ ] A/B тестирование messaging
- [ ] Integration с Developer Agent
- [ ] Dashboard для визуализации идей

## Лицензия

MIT

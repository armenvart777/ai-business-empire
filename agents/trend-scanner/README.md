# Trend Scanner Agent

Агент для обнаружения новых трендов и бизнес-возможностей.

## Функции

- 🔍 **Мониторинг Google Trends** - отслеживание поисковых запросов
- 💬 **Анализ Reddit** - выявление проблем пользователей
- 🚀 **Парсинг Product Hunt** - новые продукты и идеи
- 🤖 **AI Анализ** - глубокий анализ с помощью Claude
- 📊 **Scoring** - оценка потенциала каждого тренда (0-100)

## Установка

```bash
cd agents/trend-scanner
pip install -r requirements.txt
```

## Настройка API ключей

### Reddit API

1. Создайте приложение на https://www.reddit.com/prefs/apps
2. Получите `client_id` и `client_secret`
3. Добавьте в `.env`:

```bash
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
```

### Product Hunt API (опционально)

1. Создайте приложение на https://www.producthunt.com/v2/oauth/applications
2. Получите access token
3. Добавьте в `.env`:

```bash
PRODUCT_HUNT_ACCESS_TOKEN=your_token
```

### Google Trends

Google Trends API не требует ключей (используется через `pytrends`).

## Использование

### Базовое использование

```python
from agents.trend_scanner import TrendScannerAgent

# Создаем агента
agent = TrendScannerAgent()

# Сканируем тренды
trends = await agent.scan_trends(
    sources=["google_trends", "reddit", "product_hunt"],
    min_score=60,  # Только тренды с score >= 60
    limit=20       # Топ-20 трендов
)

# Выводим результаты
for trend in trends:
    print(f"Score: {trend['score']}/100")
    print(f"Category: {trend['category']}")
    print(f"Pain: {trend['user_pain']}")
    print(f"Ideas: {trend['business_ideas']}")
    print()
```

### Получить топ-тренды

```python
# Получить топ-10 трендов из последнего скана
top_trends = await agent.get_top_trends(limit=10)

# Фильтр по категории
tech_trends = await agent.get_top_trends(
    limit=10,
    category="technology"
)
```

### Запуск как standalone скрипт

```bash
python -m agents.trend-scanner.agent
```

## Архитектура

```
trend-scanner/
├── agent.py          # Основной класс TrendScannerAgent
├── sources.py        # Интеграции с API (Google, Reddit, PH)
├── analyzer.py       # Анализ трендов с помощью LLM
├── scorer.py         # Оценка потенциала трендов
├── requirements.txt  # Зависимости
└── README.md         # Документация
```

## Workflow

1. **Сканирование источников** - параллельный сбор данных
2. **Фильтрация** - отбор релевантных трендов
3. **Анализ с LLM** - глубокий анализ каждого тренда
4. **Scoring** - оценка потенциала (0-100)
5. **Сохранение** - запись в JSON файлы
6. **Передача** - лучшие тренды → Business Generator

## Scoring Algorithm

Score (0-100) рассчитывается на основе 5 факторов:

| Фактор | Вес | Описание |
|--------|-----|----------|
| **Popularity** | 30% | Популярность (votes, upvotes, interest) |
| **Engagement** | 25% | Вовлеченность (комментарии, шеры) |
| **Market Size** | 20% | Размер рынка (small/medium/large) |
| **Category** | 15% | Категория (tech, health имеют выше score) |
| **Novelty** | 10% | Новизна (новые тренды лучше) |

## Пример результата

```json
{
  "source": "reddit",
  "subreddit": "SaaS",
  "title": "Frustrated with project management tools",
  "score": 85,
  "category": "productivity",
  "user_pain": "Users struggle with overly complex PM tools",
  "market_size": "large",
  "target_audience": "Freelancers and small teams",
  "business_ideas": [
    "Simplified PM tool with AI task automation",
    "No-code workflow builder for teams",
    "Smart deadline predictor based on past data"
  ],
  "reasoning": "Large market with clear pain points and low competition",
  "monetization": "subscription",
  "competition_level": "medium",
  "technical_complexity": "medium"
}
```

## Сохранение данных

Тренды сохраняются в `data/trends/`:

```
data/trends/
├── trends_20260206_143022.json  # Timestamped files
├── trends_20260206_150115.json
└── latest.json                   # Последний скан
```

## Мониторинг

Логи пишутся в stdout с уровнем `INFO`:

```
2026-02-06 14:30:22 - INFO - Trend Scanner Agent initialized
2026-02-06 14:30:22 - INFO - Starting trend scan from sources: ['google_trends', 'reddit']
2026-02-06 14:30:25 - INFO - Scanning Google Trends...
2026-02-06 14:30:27 - INFO - Found 15 trending searches from Google Trends
2026-02-06 14:30:28 - INFO - Scanning Reddit...
2026-02-06 14:30:31 - INFO - Found 24 posts from r/SaaS
2026-02-06 14:30:45 - INFO - Analyzed 32 trends successfully
2026-02-06 14:30:46 - INFO - Found 18 high-quality trends (score >= 60)
```

## Расширение

### Добавить новый источник

```python
# agents/trend-scanner/sources.py

class TwitterSource:
    async def get_trending_tweets(self, hashtags: List[str]):
        # Ваша реализация
        pass

# agents/trend-scanner/agent.py

async def _scan_twitter(self):
    tweets = await self.twitter.get_trending_tweets(["#SaaS", "#AI"])
    return tweets
```

### Настроить scoring

```python
# agents/trend-scanner/scorer.py

scorer = TrendScorer()

# Изменить веса
scorer.weights = {
    "popularity": 40,     # Больше вес популярности
    "engagement": 20,
    "market_size": 20,
    "category": 10,
    "novelty": 10
}
```

## Стоимость

При использовании Claude Haiku для анализа:

- **Анализ 1 тренда**: ~1000 tokens = $0.0008
- **Скан 50 трендов**: ~$0.04
- **Ежедневный скан**: ~$1.20/месяц

Оптимизация: используйте батчинг и кеширование для снижения затрат.

## Troubleshooting

### Google Trends не работает

```bash
pip install --upgrade pytrends
```

### Reddit 401 Unauthorized

Проверьте `REDDIT_CLIENT_ID` и `REDDIT_CLIENT_SECRET` в `.env`.

### Product Hunt no data

Используется mock data если нет токена. Получите токен на https://www.producthunt.com/v2/oauth/applications.

## TODO

- [ ] Добавить Twitter/X integration
- [ ] Добавить HackerNews integration
- [ ] Реализовать хранение в PostgreSQL
- [ ] Добавить дедупликацию трендов
- [ ] Webhook уведомления о новых топ-трендах
- [ ] Dashboard для визуализации трендов

## Лицензия

MIT

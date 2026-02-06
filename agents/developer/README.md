# Developer Agent

Агент для автоматической разработки MVP от идеи до production.

## Функции

- 🏗️ **Проектирование архитектуры** - выбор tech stack
- 💻 **Генерация кода** - все компоненты проекта
- 🐙 **GitHub интеграция** - создание репо, PR, CI/CD
- 🚀 **Автоматический деплой** - Vercel/Railway
- ✅ **End-to-end automation** - от идеи до production URL

## Workflow

```
Business Idea
  ↓
Tech Spec
  ↓
Architecture Design
  ↓
Code Generation
  ↓
GitHub Repo Created
  ↓
Code Pushed
  ↓
GitHub Actions CI/CD
  ↓
Auto-merge PR
  ↓
Deploy to Vercel
  ↓
Production URL ✅
```

## Установка

```bash
cd agents/developer
pip install -r requirements.txt
```

## Настройка

### GitHub Token

1. Создайте Personal Access Token на https://github.com/settings/tokens
2. Права: `repo`, `workflow`, `write:packages`
3. Добавьте в `.env`:

```bash
GITHUB_TOKEN=ghp_your_token_here
GITHUB_ORG=your-github-org
```

### Vercel Token (для деплоя)

1. Получите токен на https://vercel.com/account/tokens
2. Добавьте в `.env`:

```bash
VERCEL_TOKEN=your_vercel_token
```

### Railway Token (опционально)

```bash
RAILWAY_TOKEN=your_railway_token
```

## Использование

### Базовый пример

```python
from agents.developer import DeveloperAgent

# Бизнес-идея от Business Generator
business_idea = {
    "id": "test-123",
    "name": "TaskFlow AI",
    "tagline": "Project management that thinks for you",
    "description": "AI-powered PM tool for small teams",
    "target_audience": "Freelancers and teams of 2-10",
    "key_features": [
        "AI task prioritization",
        "Automatic deadline prediction",
        "Smart workflow suggestions"
    ],
    "revenue_model": "freemium",
    "pricing": "Free + $19/month Pro",
    "technical_complexity": "medium",
    "time_to_mvp_weeks": 6
}

# Создаем агента
agent = DeveloperAgent()

# Создаем MVP
result = await agent.create_mvp(
    business_idea=business_idea,
    auto_deploy=True,
    auto_merge=True
)

print(f"✅ MVP Created!")
print(f"Repository: {result['repository']['url']}")
print(f"Production: {result['deployment']['url']}")
```

### Только генерация кода (без деплоя)

```python
result = await agent.create_mvp(
    business_idea=business_idea,
    auto_deploy=False,
    auto_merge=False
)
# Вернет repo URL и PR URL, но не будет деплоить
```

## Архитектура

```
developer/
├── agent.py              # Основной класс DeveloperAgent
├── architect.py          # Проектирование архитектуры
├── code_generator.py     # Генерация кода
├── github_manager.py     # GitHub операции
├── deployer.py           # Деплой на platforms
├── requirements.txt      # Зависимости
└── README.md             # Документация
```

## Поддерживаемые Tech Stacks

### Next.js SaaS (default)

```
frontend: Next.js 14 + TypeScript + Tailwind CSS
backend: Next.js API Routes
database: PostgreSQL (Supabase)
auth: NextAuth.js
hosting: Vercel
```

**Использование:** SaaS проекты средней сложности

### Next.js Landing Page

```
frontend: Next.js 14 + TypeScript + Tailwind CSS
backend: None (static)
database: None
auth: None
hosting: Vercel
```

**Использование:** Простые landing pages, marketing sites

### FastAPI Backend

```
frontend: None (API only)
backend: FastAPI + Python
database: PostgreSQL
auth: JWT
hosting: Railway
```

**Использование:** API-only проекты, microservices

## Генерируемые файлы

Для Next.js SaaS проекта:

```
project/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Homepage
│   │   ├── dashboard/
│   │   │   └── page.tsx          # Dashboard
│   │   └── api/
│   │       └── generate/
│   │           └── route.ts      # API endpoint
│   └── components/
│       ├── Hero.tsx
│       ├── Features.tsx
│       └── AuthProvider.tsx
├── migrations/
│   └── 001_initial_schema.sql    # Database schema
├── .github/
│   └── workflows/
│       └── ci.yml                # GitHub Actions
├── package.json
├── .env.example
├── .gitignore
└── README.md
```

## GitHub Actions CI/CD

Автоматически создается workflow:

```yaml
name: CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    - Lint code
    - Build project
    - Run tests

  deploy:
    - Deploy to Vercel
    - Get production URL
```

## Стоимость

### LLM API (Claude Sonnet)

- **Tech spec**: ~1000 tokens = $0.003
- **Architecture**: ~2000 tokens = $0.006
- **Code generation** (10 компонентов): ~20,000 tokens = $0.060

**Total per MVP**: ~$0.07

### Infrastructure

- **GitHub**: Free (public repos)
- **Vercel**: Free tier (100GB/month)
- **Railway**: Free tier → $5/month
- **Supabase**: Free tier (500MB)

**Total**: $0-5/month per project

## Пример результата

```json
{
  "business_id": "test-123",
  "business_name": "TaskFlow AI",
  "status": "deployed",
  "repository": {
    "name": "business-123-taskflow-ai",
    "url": "https://github.com/ai-business-empire/business-123-taskflow-ai",
    "clone_url": "git@github.com:ai-business-empire/business-123-taskflow-ai.git"
  },
  "pull_request": {
    "number": 1,
    "url": "https://github.com/ai-business-empire/business-123-taskflow-ai/pull/1",
    "merged": true
  },
  "deployment": {
    "url": "https://business-123-taskflow-ai.vercel.app",
    "provider": "vercel"
  },
  "files_generated": 15,
  "created_at": "2026-02-06T16:30:00"
}
```

## Интеграция с другими агентами

```python
from agents.trend_scanner import TrendScannerAgent
from agents.business_generator import BusinessGeneratorAgent
from agents.developer import DeveloperAgent

# 1. Scan trends
trend_agent = TrendScannerAgent()
trends = await trend_agent.scan_trends(min_score=70)

# 2. Generate ideas
business_agent = BusinessGeneratorAgent()
ideas = await business_agent.generate_business_ideas(
    trends=trends,
    min_priority_score=75
)

# 3. Develop MVP
developer_agent = DeveloperAgent()

for idea in ideas[:3]:  # Топ-3 идеи
    result = await developer_agent.create_mvp(
        business_idea=idea,
        auto_deploy=True
    )

    print(f"✅ {idea['name']} deployed: {result['deployment']['url']}")
```

## Troubleshooting

### GitHub Token не работает

Проверьте права токена:
- `repo` (full control)
- `workflow` (update workflows)

### Vercel деплой не работает

1. Убедитесь что `VERCEL_TOKEN` установлен
2. Подключите GitHub repo к Vercel проекту
3. Получите `VERCEL_PROJECT_ID` и `VERCEL_ORG_ID`

### Code generation fails

Увеличьте `max_tokens` для LLM или упростите архитектуру (меньше компонентов).

## Ограничения текущей версии

- Mock implementation для GitHub API (требует настройки PyGithub)
- Mock implementation для Vercel/Railway API
- Ограниченный выбор tech stacks (3 варианта)
- Нет rollback механизма при ошибках
- Нет advanced code review

## TODO

- [ ] Полная интеграция с GitHub API (PyGithub)
- [ ] Полная интеграция с Vercel API
- [ ] Railway API integration
- [ ] Code review агент (проверка качества)
- [ ] Automated testing generation
- [ ] More tech stacks (Vue, Svelte, Go, Rust)
- [ ] Rollback on deployment failure
- [ ] Cost estimation before deployment
- [ ] A/B testing setup
- [ ] Analytics integration (Plausible/PostHog)

## Лицензия

MIT

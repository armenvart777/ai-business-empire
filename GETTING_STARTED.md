# 🚀 Getting Started - Быстрый Старт

Этот гайд поможет тебе начать работу с проектом AI Business Empire.

## Текущий Статус

**Фаза**: 0 - Подготовка ✅
**Следующее**: Фаза 1 - Исследования

---

## Что Уже Готово

✅ Структура проекта создана
✅ Документация написана:
  - [README.md](README.md) - обзор проекта
  - [SYSTEM_OVERVIEW.md](docs/architecture/SYSTEM_OVERVIEW.md) - архитектура
  - [RESEARCH_PLAN.md](docs/research/RESEARCH_PLAN.md) - план исследований
  - [BUDGET_OPTIMIZATION.md](docs/plans/BUDGET_OPTIMIZATION.md) - бюджет
  - [ROADMAP.md](docs/plans/ROADMAP.md) - дорожная карта

✅ Шаблоны для агентов
✅ Конфигурационные файлы

---

## Следующие Шаги

### 1. Настройка Окружения

#### Git Repository

```bash
# Инициализация Git
git init
git add .
git commit -m "Initial commit: project structure and documentation

- Created project structure
- Added comprehensive documentation
- Set up agent templates
- Configured .gitignore

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Создать репозиторий на GitHub и запушить
git remote add origin <your-repo-url>
git push -u origin main
```

#### Environment Variables

Создай файл `.env` в корне проекта:

```bash
# .env

# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-...

# Database (Supabase)
SUPABASE_URL=https://....supabase.co
SUPABASE_KEY=eyJ...

# Redis (Upstash)
REDIS_URL=redis://...

# Google Trends
# (не требует ключа, используется pytrends)

# Reddit
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=ai-business-empire/1.0

# Product Hunt (опционально)
PRODUCTHUNT_TOKEN=...

# Monitoring (опционально)
SENTRY_DSN=...

# Email (SendGrid)
SENDGRID_API_KEY=SG...

# Environment
ENVIRONMENT=development
```

#### Python Environment

```bash
# Создать виртуальное окружение
python3 -m venv venv

# Активировать
source venv/bin/activate  # macOS/Linux
# или
.\venv\Scripts\activate  # Windows

# Установить зависимости (когда появятся)
# pip install -r backend/requirements.txt
```

#### Node.js Environment

```bash
# Установить Node.js (если нет)
# brew install node  # macOS
# или скачать с nodejs.org

# Проверить версию
node --version  # должна быть v18+
npm --version
```

---

### 2. Начало Исследований (Week 1-4)

Следуй плану из [RESEARCH_PLAN.md](docs/research/RESEARCH_PLAN.md)

#### Week 1: AI Agents & Tech Stack

**Задачи**:
1. Изучить AutoGPT, LangChain, CrewAI
2. Проанализировать кейсы (Pieter Levels, Tony Dinh)
3. Финализировать tech stack

**Полезные ссылки**:
- [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT)
- [LangChain](https://python.langchain.com/)
- [CrewAI](https://github.com/joaomdmoura/crewAI)
- [Levels.io blog](https://levels.io)
- [Tony Dinh Twitter](https://twitter.com/tdinh_me)

#### Week 2: Trend Discovery

**Задачи**:
1. Настроить Google Trends API
2. Настроить Reddit API
3. Создать первый trend scanner скрипт
4. Собрать 100+ трендов

**Инструменты**:
```bash
# Установить зависимости для trend scanner
pip install pytrends praw requests beautifulsoup4
```

#### Week 3: Code Generation

**Задачи**:
1. Протестировать Cursor AI
2. Протестировать v0.dev
3. Сгенерировать 3 тестовых SaaS

**Инструменты**:
- [Cursor](https://cursor.sh)
- [v0.dev](https://v0.dev)
- [Replit](https://replit.com)

#### Week 4: Deployment & Marketing

**Задачи**:
1. Настроить Vercel
2. Настроить Railway
3. Изучить marketing automation

---

### 3. Создание Первого Агента (Trend Scanner)

После завершения исследований, приступить к разработке:

```bash
# Создать файлы агента
cd agents/trend-scanner/

# Структура:
mkdir prompts tests
touch __init__.py agent.py config.yaml
touch prompts/analyze_trend.txt
touch tests/test_agent.py
```

Использовать [template_agent.py](agents/shared/template_agent.py) как базу.

---

### 4. Разработка Dashboard

```bash
# Создать Next.js приложение
cd frontend/
npx create-next-app@latest . --typescript --tailwind --app

# Установить зависимости
npm install @tanstack/react-query axios recharts
npm install -D @types/node

# Запустить dev сервер
npm run dev
```

---

## Полезные Команды

### Разработка

```bash
# Backend
cd backend/
uvicorn api.main:app --reload  # Запустить FastAPI

# Frontend
cd frontend/
npm run dev  # Запустить Next.js

# Агенты
cd agents/
python trend-scanner/agent.py  # Запустить агента вручную
```

### Тестирование

```bash
# Python tests
pytest agents/ -v

# Frontend tests
cd frontend/
npm test
```

### Deployment

```bash
# Frontend (Vercel)
cd frontend/
vercel deploy

# Backend (Railway)
# Через Railway CLI или GitHub integration
```

---

## Чек-лист Фазы 0

Убедись что всё готово перед началом исследований:

- [ ] Git репозиторий создан
- [ ] `.env` файл настроен
- [ ] Python venv создан
- [ ] Node.js установлен
- [ ] Прочитана вся документация в `/docs`
- [ ] Понятна архитектура системы
- [ ] Понятен план исследований
- [ ] Понятна структура проекта

---

## Ресурсы для Обучения

### AI Agents
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [Building AI Agents Tutorial](https://www.youtube.com/watch?v=...)
- [Multi-Agent Systems](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/)

### Indie Hacking
- [Indie Hackers](https://www.indiehackers.com)
- [r/SideProject](https://reddit.com/r/SideProject)
- [Product Hunt](https://www.producthunt.com)

### Tech Stack
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Next.js Learn](https://nextjs.org/learn)
- [Supabase Docs](https://supabase.com/docs)

---

## Получение Помощи

### Документация
- Проверь [README.md](README.md) для общего обзора
- Проверь [SYSTEM_OVERVIEW.md](docs/architecture/SYSTEM_OVERVIEW.md) для деталей архитектуры
- Проверь [ROADMAP.md](docs/plans/ROADMAP.md) для timeline

### Community
- GitHub Issues для багов и вопросов
- Discord/Slack (создать если нужно)

---

## Метрики Успеха

### После исследований (Week 4):
- [ ] 100+ трендов проанализировано
- [ ] Tech stack выбран и задокументирован
- [ ] 3 тестовых SaaS сгенерировано
- [ ] Инфраструктура для деплоя готова

### После MVP (Week 8):
- [ ] Trend Scanner собирает 10+ трендов/день
- [ ] Business Generator создаёт 3-5 идей на тренд
- [ ] Dashboard показывает данные
- [ ] 50+ бизнес-идей в базе

### После запуска (Week 16):
- [ ] 10 бизнесов запущено
- [ ] 3+ с первыми пользователями
- [ ] Бюджет <$500/мес
- [ ] Автоматизация >90%

---

## Troubleshooting

### Проблема: API ключи не работают
**Решение**: Проверь `.env` файл, перезапусти сервер

### Проблема: Превышен бюджет LLM
**Решение**: Включи кэширование, используй более дешёвые модели

### Проблема: Агент не запускается
**Решение**: Проверь логи в `/logs/`, включи DEBUG режим

---

**Готов начинать? Погнали! 🚀**

Начни с Week 1 из [RESEARCH_PLAN.md](docs/research/RESEARCH_PLAN.md)

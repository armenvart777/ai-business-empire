# Backend API для AI Agents

REST API для управления AI-агентами из веб-интерфейса.

## Быстрый старт

### 1. Установка зависимостей

```bash
cd backend
pip install fastapi uvicorn python-multipart
```

### 2. Запуск сервера

```bash
# Development
python agents_api.py

# Или с uvicorn напрямую
uvicorn agents_api:app --reload --port 8000
```

Сервер запустится на `http://localhost:8000`

### 3. Проверка работы

Откройте в браузере: http://localhost:8000

Вы увидите:
```json
{
  "service": "AI Business Empire - Agents API",
  "status": "running",
  "version": "1.0.0",
  "agents_available": [
    "trend-scanner",
    "business-generator",
    "developer",
    "marketing",
    "sales"
  ]
}
```

### 4. API Документация

Интерактивная документация: http://localhost:8000/docs

## API Endpoints

### Запуск агентов

```bash
# Trend Scanner
curl -X POST http://localhost:8000/api/agents/scan-trends \
  -H "Content-Type: application/json" \
  -d '{
    "sources": ["google_trends", "reddit"],
    "min_score": 70,
    "limit": 20
  }'

# Business Generator
curl -X POST http://localhost:8000/api/agents/generate-ideas \
  -H "Content-Type: application/json" \
  -d '{
    "ideas_per_trend": 5,
    "min_priority_score": 70
  }'

# Developer (создать MVP)
curl -X POST http://localhost:8000/api/agents/create-mvp \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "idea-123",
    "auto_deploy": true,
    "auto_merge": true
  }'

# Marketing
curl -X POST http://localhost:8000/api/agents/create-marketing \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "idea-123",
    "deployment_url": "https://example.vercel.app",
    "duration_weeks": 4,
    "channels": ["blog", "email", "social"],
    "budget": 500
  }'

# Sales
curl -X POST http://localhost:8000/api/agents/create-sales \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "idea-123",
    "deployment_url": "https://example.vercel.app",
    "target_mrr": 5000,
    "channels": ["email", "demo", "chat"],
    "automation_level": "high"
  }'

# Full Pipeline (все агенты)
curl -X POST http://localhost:8000/api/agents/full-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "trend_sources": ["google_trends", "reddit"],
    "min_trend_score": 70,
    "ideas_per_trend": 3,
    "min_idea_score": 75,
    "auto_deploy": true,
    "marketing_budget": 500,
    "target_mrr": 5000
  }'
```

### Проверка статуса

```bash
# Получить статус конкретного job
curl http://localhost:8000/api/jobs/{job_id}

# Получить список всех jobs
curl http://localhost:8000/api/jobs

# Фильтр по типу агента
curl http://localhost:8000/api/jobs?agent_type=trend-scanner
```

## Интеграция с фронтендом

### React/Next.js

```javascript
import { scanTrends, waitForJob } from './api/agents';

function MyComponent() {
  const handleScan = async () => {
    // Запустить агента
    const jobId = await scanTrends({ minScore: 70 });

    // Дождаться результата
    const result = await waitForJob(jobId, {
      onProgress: (status) => {
        console.log('Status:', status.status);
      }
    });

    console.log('Trends:', result.trends);
  };

  return (
    <button onClick={handleScan}>
      Scan Trends
    </button>
  );
}
```

### Vue.js

```vue
<template>
  <button @click="scanTrends" :disabled="loading">
    {{ loading ? 'Scanning...' : 'Scan Trends' }}
  </button>
</template>

<script>
import { scanTrends, waitForJob } from './api/agents';

export default {
  data() {
    return {
      loading: false
    }
  },
  methods: {
    async scanTrends() {
      this.loading = true;

      const jobId = await scanTrends({ minScore: 70 });
      const result = await waitForJob(jobId);

      console.log('Trends:', result.trends);
      this.loading = false;
    }
  }
}
</script>
```

### Vanilla JavaScript

```html
<button id="scan-button">Scan Trends</button>

<script>
  document.getElementById('scan-button').addEventListener('click', async () => {
    const response = await fetch('http://localhost:8000/api/agents/scan-trends', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ min_score: 70 })
    });

    const { job_id } = await response.json();

    // Poll for result
    while (true) {
      const status = await fetch(`http://localhost:8000/api/jobs/${job_id}`);
      const data = await status.json();

      if (data.status === 'completed') {
        console.log('Trends:', data.result.trends);
        break;
      }

      await new Promise(r => setTimeout(r, 5000)); // Wait 5 sec
    }
  });
</script>
```

## Response Formats

### Job Response

Все endpoints возвращают:
```json
{
  "job_id": "trend-scanner-20260207-143022",
  "status": "pending",
  "message": "Trend scanner started"
}
```

### Job Status

```json
{
  "job_id": "trend-scanner-20260207-143022",
  "status": "completed",  // pending | running | completed | failed
  "agent_type": "trend-scanner",
  "created_at": "2026-02-07T14:30:22",
  "completed_at": "2026-02-07T14:32:15",
  "result": {
    "trends_count": 15,
    "trends": [...]
  },
  "error": null
}
```

## Environment Variables

```bash
# .env файл
ANTHROPIC_API_KEY=your_api_key_here
GITHUB_TOKEN=your_github_token
VERCEL_TOKEN=your_vercel_token

# Опционально
SENDGRID_API_KEY=your_sendgrid_key
HUBSPOT_API_KEY=your_hubspot_key
```

## CORS Configuration

По умолчанию разрешены запросы от всех доменов (`allow_origins=["*"]`).

В production измените на ваш домен:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # ← Ваш домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Production Deployment

### Option 1: Railway

```bash
# railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn backend.agents_api:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100
  }
}
```

### Option 2: Vercel (Serverless)

```bash
# vercel.json
{
  "builds": [
    {
      "src": "backend/agents_api.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "backend/agents_api.py"
    }
  ]
}
```

### Option 3: Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.agents_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t agents-api .
docker run -p 8000:8000 agents-api
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/
```

### Jobs List

```bash
# Последние 10 jobs
curl http://localhost:8000/api/jobs?limit=10

# Только failed jobs
curl http://localhost:8000/api/jobs | jq '.[] | select(.status == "failed")'
```

## Troubleshooting

### Agents import errors

Убедитесь что вы запускаете из корневой директории проекта:

```bash
cd /Users/armenvartanan/Documents/project/project1
python backend/agents_api.py
```

### CORS errors

Проверьте что CORS настроен правильно и фронтенд отправляет запросы на правильный URL.

### Jobs hang in "running" status

Проверьте логи агентов. Возможно ошибка в коде агента или недостаточно API quota.

## Next Steps

1. ✅ Запустите API сервер
2. ✅ Проверьте `/docs` endpoint
3. ✅ Попробуйте запустить Trend Scanner через API
4. ✅ Интегрируйте с вашим фронтендом
5. ⏭️ Деплой на Railway/Vercel

## Support

Issues: https://github.com/armenvart777/ai-business-empire/issues

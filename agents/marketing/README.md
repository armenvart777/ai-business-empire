# Marketing Agent

Автоматический маркетинг для MVP - от контента до деплоя кампаний.

## Функции

- 📝 **Генерация контента** - blog posts, social media, emails
- 🔍 **SEO оптимизация** - keyword research, on-page SEO
- 📧 **Email кампании** - welcome sequences, nurture, conversion
- 📱 **Social media** - посты для Twitter, LinkedIn, Reddit
- 📊 **Analytics** - tracking setup, performance analysis
- 🚀 **Launch campaigns** - Product Hunt, social media launches

## Workflow

```
Business Idea + Deployment URL
  ↓
Audience Analysis
  ↓
Content Calendar Creation
  ↓
Blog Posts Generation
  ↓
SEO Optimization
  ↓
Social Media Posts
  ↓
Email Campaigns Setup
  ↓
Ads Campaigns (optional)
  ↓
Analytics Tracking Setup
  ↓
Performance Monitoring & Optimization
```

## Установка

```bash
cd agents/marketing
pip install -r requirements.txt
```

## Настройка

### API Keys (опционально)

```bash
# В .env файле:
SENDGRID_API_KEY=your_key_here       # Email отправка
TWITTER_API_KEY=your_key_here        # Twitter posting
LINKEDIN_API_KEY=your_key_here       # LinkedIn posting
GOOGLE_ADS_API_KEY=your_key_here     # Google Ads (если используется)
```

## Использование

### Базовый пример

```python
from agents.marketing import MarketingAgent

# Бизнес-идея (из Business Generator)
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
    "pricing": "Free + $19/month Pro"
}

# Deployment URL (из Developer Agent)
deployment_url = "https://business-123-taskflow-ai.vercel.app"

# Создаем маркетинговую кампанию
agent = MarketingAgent()

campaign = await agent.create_marketing_campaign(
    business_idea=business_idea,
    deployment_url=deployment_url,
    duration_weeks=4,
    channels=["blog", "email", "social"],
    budget=500
)

print(f"✅ Campaign Created!")
print(f"Blog Posts: {len(campaign['blog_posts'])}")
print(f"Social Posts: {len(campaign['social_posts'])}")
print(f"Email Campaigns: {len(campaign['email_campaigns'])}")
print(f"Estimated Reach: {campaign['estimated_reach']:,} people")
```

### Только контент (без кампании)

```python
from agents.marketing import ContentGenerator

generator = ContentGenerator(llm=agent.llm)

# Генерация blog post
post = await generator.generate_blog_post(
    business_idea=business_idea,
    topic="10 Tips for Better Task Management",
    min_words=800
)

print(f"Title: {post['title']}")
print(f"Words: {post['word_count']}")
```

### Только SEO

```python
from agents.marketing import SEOOptimizer

seo = SEOOptimizer(llm=agent.llm)

strategy = await seo.create_seo_strategy(
    business_idea=business_idea,
    deployment_url=deployment_url,
    blog_posts=[]
)

print(f"SEO Score: {strategy['estimated_seo_score']}/100")
print(f"Keywords: {len(strategy['keywords']['primary_keywords'])}")
```

## Архитектура

```
marketing/
├── agent.py                # Основной класс MarketingAgent
├── content_generator.py    # Генерация контента
├── seo_optimizer.py        # SEO оптимизация
├── email_campaign.py       # Email маркетинг
├── social_media.py         # Social media management
├── analytics.py            # Analytics и tracking
├── requirements.txt        # Зависимости
└── README.md               # Документация
```

## Генерируемые материалы

### Blog Posts

Каждый blog post включает:
- SEO-optimized title (60 chars max)
- Meta description (155 chars max)
- Keywords
- Full markdown content (800+ words)
- Call to action
- Reading time estimate

### Social Media Posts

Для каждой платформы:
- **Twitter**: Краткие, engaging, 1-2 хэштега
- **LinkedIn**: Профессиональный тон, инсайты
- **Reddit**: Аутентичный, полезный, не promotional

### Email Campaigns

- **Welcome Sequence**: 5 emails (дни 0, 1, 3, 5, 7)
- **Nurture Campaign**: 4 emails для каждого сегмента
- **Conversion Campaign**: 3 emails (free → paid)

## SEO Стратегия

### Keyword Research

- Primary keywords (3-5) - высокий volume, высокий intent
- Secondary keywords (5-10) - средний volume
- Long-tail keywords (10-15) - специфичные, низкая конкуренция
- Question keywords (5-10) - для blog контента

### Technical SEO

Рекомендации включают:
- Image optimization
- Caching headers
- Mobile responsiveness
- Sitemap.xml
- robots.txt
- HTTPS enforcement
- Canonical tags
- Performance optimization

## Analytics Setup

### Tracking Events

- Page views
- User sessions
- Blog post views
- Email opens/clicks
- Social media clicks
- Signups
- Trial starts
- Paid conversions

### UTM Parameters

Автоматически генерируются для каждого канала:
```
utm_source=blog/email/twitter/linkedin
utm_medium=content/email/social/cpc
utm_campaign={{campaign_name}}
```

## Estimated Reach

Формула для оценки reach:
- **Blog**: 500 visitors/week (organic SEO)
- **Email**: 100 opens/week (email list)
- **Social**: 1000 impressions/week (organic)
- **Ads**: budget × 10 (CPC ~$0.10)

Пример: 4-week campaign, $500 budget:
- Blog: 2000 visitors
- Email: 400 opens
- Social: 4000 impressions
- Ads: 5000 clicks
- **Total: ~11,400 people reached**

## Стоимость

### LLM API (Claude Sonnet)

- **Content calendar**: ~1000 tokens = $0.003
- **Blog posts** (8 posts): ~16,000 tokens = $0.048
- **Social posts** (28 posts): ~10,000 tokens = $0.030
- **Email campaigns** (3 campaigns): ~6,000 tokens = $0.018
- **SEO strategy**: ~2000 tokens = $0.006

**Total per campaign**: ~$0.10

### Marketing Channels

- **Blog**: Free (hosting included)
- **Email**: $0 (SendGrid free tier: 100 emails/day)
- **Social**: Free (organic posting)
- **Ads**: $100-500/month (опционально)

**Total**: $0-10/month (без ads), $100-500/month (с ads)

## Пример результата

```json
{
  "campaign_id": "campaign-test-123-20260207",
  "business_name": "TaskFlow AI",
  "status": "active",
  "duration_weeks": 4,
  "channels": ["blog", "email", "social"],
  "budget": 500,
  "audience_analysis": {
    "segments": [
      {
        "name": "Freelancers",
        "size": "30%"
      },
      {
        "name": "Small Teams",
        "size": "70%"
      }
    ]
  },
  "blog_posts": 8,
  "social_posts": 28,
  "email_campaigns": 3,
  "estimated_reach": 11400,
  "seo_strategy": {
    "estimated_seo_score": 75
  }
}
```

## Интеграция с другими агентами

```python
from agents.trend_scanner import TrendScannerAgent
from agents.business_generator import BusinessGeneratorAgent
from agents.developer import DeveloperAgent
from agents.marketing import MarketingAgent

# 1. Scan trends
trends = await TrendScannerAgent().scan_trends(min_score=70)

# 2. Generate business ideas
ideas = await BusinessGeneratorAgent().generate_business_ideas(
    trends=trends,
    min_priority_score=75
)

# 3. Develop MVP
mvp_result = await DeveloperAgent().create_mvp(
    business_idea=ideas[0],
    auto_deploy=True
)

# 4. Launch marketing campaign
campaign = await MarketingAgent().create_marketing_campaign(
    business_idea=ideas[0],
    deployment_url=mvp_result['deployment']['url'],
    duration_weeks=4,
    channels=["blog", "email", "social"],
    budget=500
)

print(f"✅ {ideas[0]['name']} is live and marketed!")
print(f"URL: {mvp_result['deployment']['url']}")
print(f"Estimated reach: {campaign['estimated_reach']:,} people")
```

## Performance Optimization

### После запуска кампании

```python
# Collect performance data (из Google Analytics, email provider, etc.)
performance_data = {
    "total_visitors": 5000,
    "total_signups": 100,
    "blog_data": {
        "visitors": 2000,
        "signups": 50
    },
    "email_data": {
        "visitors": 800,
        "signups": 30
    }
}

# Анализ и рекомендации
insights = await agent.analytics.analyze_performance(performance_data)

for recommendation in insights['recommendations']:
    print(f"[{recommendation['priority']}] {recommendation['recommendation']}")
```

## Ограничения текущей версии

- Mock implementation для email/social APIs (требует настройки SendGrid, Twitter API, etc.)
- Нет автоматического posting (требует manual copy-paste или API интеграции)
- Ограниченный A/B testing (только setup, нет автоматического запуска)
- Нет integration с Google Ads / Facebook Ads APIs

## TODO

- [ ] Полная интеграция с SendGrid для автоматической отправки emails
- [ ] Twitter API integration для автоматического posting
- [ ] LinkedIn API integration
- [ ] Reddit API integration (требует осторожности с правилами)
- [ ] Google Ads API integration
- [ ] Facebook Ads API integration
- [ ] Automated A/B testing execution
- [ ] Image generation для social media (DALL-E, Midjourney)
- [ ] Video script generation
- [ ] Influencer outreach automation
- [ ] Community management (Discord, Slack)

## Best Practices

### Content Quality

- Фокус на value, не на промоушене
- Authentic tone, как от человека
- Регулярность важнее количества
- Engage с комментариями и responses

### SEO

- Keyword stuffing = плохо
- Natural language, user-first
- Internal linking между blog posts
- Backlinks важнее on-page оптимизации

### Email

- Personalization увеличивает open rate на 26%
- Subject lines до 45 символов работают лучше
- Send time: 8-10am или 5-6pm (timezone аудитории)
- A/B test subject lines

### Social Media

- Consistency > Perfection
- Engage в течение первого часа после posting
- Reshare top-performing content
- Mix content types (text, images, videos, polls)

## Лицензия

MIT

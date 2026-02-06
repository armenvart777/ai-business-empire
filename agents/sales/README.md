# Sales Agent

Автоматизация продаж для SaaS - от lead generation до revenue optimization.

## Функции

- 🎯 **Sales Funnel Design** - проектирование воронок продаж
- 🧲 **Lead Generation** - lead magnets, scoring, qualification
- 📧 **Sales Email Sequences** - trial conversion, demo follow-up
- 💼 **CRM Integration** - HubSpot, Pipedrive setup
- 📊 **Conversion Optimization** - A/B testing, pricing optimization
- 💰 **Revenue Tracking** - MRR, ARR, LTV, CAC

## Workflow

```
Business Idea + Deployment URL
  ↓
Design Sales Funnel
  ↓
Setup Lead Generation
  ↓
Create Email Sequences
  ↓
CRM Integration
  ↓
Demo/Chat Flows
  ↓
Pricing Optimization
  ↓
Analytics & Tracking
  ↓
Performance Monitoring & Optimization
```

## Установка

```bash
cd agents/sales
pip install -r requirements.txt
```

## Настройка

### API Keys (опционально)

```bash
# В .env файле:
HUBSPOT_API_KEY=your_key_here         # HubSpot CRM
PIPEDRIVE_API_KEY=your_key_here       # Pipedrive CRM (альтернатива)
```

## Использование

### Базовый пример

```python
from agents.sales import SalesAgent

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

# Создаем sales систему
agent = SalesAgent()

sales_system = await agent.create_sales_system(
    business_idea=business_idea,
    deployment_url=deployment_url,
    target_mrr=5000,
    channels=["email", "demo", "chat"],
    automation_level="high"
)

print(f"✅ Sales System Created!")
print(f"Funnel stages: {len(sales_system['funnel']['stages'])}")
print(f"Email sequences: {len(sales_system['email_sequences'])}")
print(f"Conversion rate: {sales_system['estimated_conversion_rate'] * 100:.1f}%")
print(f"Customers needed: {sales_system['estimated_customers_needed']}")
```

### Только Funnel Design

```python
from agents.sales import FunnelBuilder

builder = FunnelBuilder(llm=agent.llm)

funnel = await builder.design_funnel(
    business_idea=business_idea,
    deployment_url=deployment_url,
    channels=["email", "demo"]
)

print(f"Funnel: {funnel['funnel_name']}")
print(f"Stages: {len(funnel['stages'])}")
```

### Lead Generation Strategy

```python
from agents.sales import LeadGenerator

generator = LeadGenerator(llm=agent.llm)

strategy = await generator.create_lead_strategy(
    business_idea=business_idea,
    funnel=funnel,
    target_mrr=5000
)

print(f"Lead magnets: {len(strategy['lead_magnets'])}")
print(f"Monthly leads needed: {strategy['targets']['monthly_leads_needed']}")
```

## Архитектура

```
sales/
├── agent.py                    # Основной класс SalesAgent
├── funnel_builder.py           # Проектирование sales funnels
├── lead_generator.py           # Lead generation & qualification
├── crm_manager.py              # CRM интеграция
├── email_sequences.py          # Sales email sequences
├── conversion_optimizer.py     # Conversion optimization
├── requirements.txt            # Зависимости
└── README.md                   # Документация
```

## Sales Funnel Stages

### Self-Serve Trial Funnel (default для freemium)

```
1. Visitor (website traffic)
   ↓ 30% conversion
2. Signup (created account)
   ↓ 40% conversion
3. Trial Started (activated trial)
   ↓ 25% conversion
4. Paid Customer
```

**Overall conversion: 3% (visitor → paid)**

### Demo-Based Funnel

```
1. Visitor
   ↓ 5% conversion
2. Demo Requested
   ↓ 60% conversion (demo attendance)
3. Demo Completed
   ↓ 40% conversion
4. Paid Customer
```

**Overall conversion: 1.2% (visitor → paid)**

## Lead Magnets

Типы lead magnets, которые генерируются:

1. **Checklists/Templates** - быстро создать, высокая ценность
2. **Ebooks/Guides** - больше effort, позиционирует как эксперта
3. **Free Tools** - высокая conversion, требует development
4. **Webinars** - личный контакт, high-intent leads
5. **Case Studies** - социальное доказательство

Conversion rates:
- Homepage signup: ~3%
- Lead magnet download: ~25%
- Demo request: ~10%

## Lead Scoring Model

### Критерии (0-100 points)

- **Company Size** (20 points) - 6-20 employees = sweet spot
- **Industry** (15 points) - target industry = full points
- **Engagement** (30 points) - pricing page visit, demo view
- **Role/Title** (20 points) - decision maker = full points
- **Budget** (15 points) - mentioned budget or enterprise

### Классификация

- **Hot (70-100)**: Immediate sales contact
- **Warm (40-69)**: Nurture sequence
- **Cold (0-39)**: Educational content

## Email Sequences

### Trial → Paid Conversion (7 emails)

- Day 0: Welcome, quick start
- Day 2: Feature highlight #1
- Day 5: Feature highlight #2
- Day 8: Customer success story
- Day 11: Trial ending soon (urgency)
- Day 13: LAST CHANCE
- Day 15: Trial expired, special offer

**Expected conversion: 20-30%**

### Demo Follow-Up (5 emails)

- Day 0: Thank you + recap
- Day 1: Resources + FAQ
- Day 3: Check-in
- Day 5: Case study
- Day 7: Time-limited offer

**Expected conversion: 30-40%**

### Win-Back Sequence (4 emails)

- Day 0: We miss you
- Day 7: What's new
- Day 14: Special comeback offer (20% discount)
- Day 30: Last chance

**Expected conversion: 5-10%**

## CRM Setup

### HubSpot Integration

- **Pipeline Stages**: Auto-created from sales funnel
- **Contact Properties**: Company size, industry, role, lead score, etc.
- **Deal Properties**: MRR, ARR, plan type, contract length
- **Automation Workflows**: 5 workflows (nurture, hot lead alert, trial, won, lost)
- **Dashboards**: Sales performance, lead quality, revenue metrics

### Pipelines Created

1. **Sales Pipeline**: Visitor → Signup → Trial → Paid
2. **Demo Pipeline**: Demo Request → Demo Scheduled → Demo Completed → Closed Won/Lost

## Pricing Optimization

### Рекомендации по pricing:

- **Free Tier**: Ограничения (5 projects, basic features)
- **Pro Tier**: $19-29/month - sweet spot для small teams
- **Business Tier**: $49-99/month - advanced features
- **Enterprise**: Custom pricing

### Pricing Psychology

- **Anchor pricing**: показать Enterprise цену первой
- **Decoy pricing**: средний tier самый attractive
- **Annual discount**: 15-20% off (2-3 месяца бесплатно)
- **Trial duration**: 14 дней оптимально (7 дней слишком мало, 30 слишком долго)

## Conversion Rate Benchmarks (SaaS)

- **Visitor → Signup**: 2-5%
- **Signup → Trial**: 30-50%
- **Trial → Paid**: 20-30%
- **Overall (Visitor → Paid)**: 1-3%

## Revenue Metrics

### Отслеживаемые метрики:

- **MRR (Monthly Recurring Revenue)**: Monthly subscription revenue
- **ARR (Annual Recurring Revenue)**: MRR × 12
- **LTV (Lifetime Value)**: Average revenue per customer lifetime
- **CAC (Customer Acquisition Cost)**: Marketing + sales cost per customer
- **Payback Period**: Time to recover CAC (ideally < 12 months)
- **Churn Rate**: % customers leaving per month (goal: < 5%)

### Example Calculation:

```
Target MRR: $5,000
Average Price: $19/month
Customers Needed: 263

With 2.5% conversion rate:
Traffic Needed: 10,520 visitors/month
```

## Стоимость

### LLM API (Claude Sonnet)

- **Funnel design**: ~2000 tokens = $0.006
- **Lead strategy**: ~2000 tokens = $0.006
- **Email sequences** (3 sequences): ~7000 tokens = $0.021
- **Pricing optimization**: ~2000 tokens = $0.006
- **Total per sales system**: ~$0.04

### Infrastructure

- **CRM**: $0 (HubSpot free tier: 1M contacts)
- **Email sending**: $0 (SendGrid free tier)
- **Analytics**: $0 (Google Analytics free)

**Total**: $0/month

## Пример результата

```json
{
  "system_id": "sales-test-123-20260207",
  "business_name": "TaskFlow AI",
  "status": "active",
  "target_mrr": 5000,
  "channels": ["email", "demo", "chat"],
  "automation_level": "high",
  "funnel": {
    "funnel_type": "self_serve_trial",
    "stages": 4,
    "estimated_overall_conversion": 0.025
  },
  "email_sequences": 3,
  "estimated_conversion_rate": 0.03,
  "estimated_customers_needed": 263,
  "crm_setup": {
    "provider": "HubSpot",
    "pipelines": 1,
    "automation_workflows": 5
  }
}
```

## Интеграция с другими агентами

```python
from agents.trend_scanner import TrendScannerAgent
from agents.business_generator import BusinessGeneratorAgent
from agents.developer import DeveloperAgent
from agents.marketing import MarketingAgent
from agents.sales import SalesAgent

# 1. Scan trends
trends = await TrendScannerAgent().scan_trends(min_score=70)

# 2. Generate business ideas
ideas = await BusinessGeneratorAgent().generate_business_ideas(
    trends=trends,
    min_priority_score=75
)

# 3. Develop MVP
mvp = await DeveloperAgent().create_mvp(
    business_idea=ideas[0],
    auto_deploy=True
)

# 4. Launch marketing
campaign = await MarketingAgent().create_marketing_campaign(
    business_idea=ideas[0],
    deployment_url=mvp['deployment']['url'],
    duration_weeks=4,
    channels=["blog", "email", "social"],
    budget=500
)

# 5. Setup sales system
sales_system = await SalesAgent().create_sales_system(
    business_idea=ideas[0],
    deployment_url=mvp['deployment']['url'],
    target_mrr=5000,
    channels=["email", "demo", "chat"],
    automation_level="high"
)

print(f"✅ {ideas[0]['name']} is LIVE, MARKETED, and SELLING!")
print(f"URL: {mvp['deployment']['url']}")
print(f"Marketing reach: {campaign['estimated_reach']:,}")
print(f"Sales conversion: {sales_system['estimated_conversion_rate'] * 100:.1f}%")
```

## Optimization Loop

### После запуска sales system:

```python
# Collect performance data
performance_data = {
    "stage_0": {"visitors": 1000, "converted": 200},
    "stage_1": {"visitors": 200, "converted": 100},
    "stage_2": {"visitors": 100, "converted": 25}
}

# Analyze and optimize
optimizations = await agent.optimize_conversion_rate(
    system_id=sales_system['system_id'],
    performance_data=performance_data
)

for rec in optimizations['recommendations']:
    print(f"[{rec['priority']}] {rec['recommendation']}")
```

## Ограничения текущей версии

- Mock implementation для CRM APIs (требует настройки HubSpot/Pipedrive API)
- Нет автоматического A/B testing execution
- Simplified lead scoring (требует ML модель для точности)
- Нет integration с payment providers (Stripe, Paddle)

## TODO

- [ ] Полная интеграция с HubSpot API
- [ ] Pipedrive API integration
- [ ] Stripe/Paddle payment integration
- [ ] Automated A/B testing platform
- [ ] ML-based lead scoring
- [ ] Churn prediction model
- [ ] Revenue forecasting
- [ ] Sales call scheduling (Calendly integration)
- [ ] Proposal/quote generation
- [ ] Contract management

## Best Practices

### Lead Qualification

- **BANT Framework**: Budget, Authority, Need, Timeline
- Qualify early, don't waste time on unqualified leads
- Focus on high-intent signals (pricing page, demo request)

### Trial Optimization

- Show value quickly (first 5 minutes)
- Pre-populate sample data
- Send timely emails (days 0, 3, 7, 11, 13)
- In-app upgrade prompts at key moments

### Pricing

- Don't compete on price (compete on value)
- Test pricing regularly (annual increases OK)
- Annual plans reduce churn (offer discount)
- Enterprise tier = custom pricing (don't show on website)

### CRM Hygiene

- Clean data regularly
- Document qualification criteria
- Update deal stages consistently
- Review pipeline weekly

## Лицензия

MIT

"""
Project Architect - проектирование архитектуры приложения.

Выбирает tech stack и создает структуру проекта.
"""

import json
import logging
from typing import Dict, Any


logger = logging.getLogger(__name__)


class ProjectArchitect:
    """
    Архитектор проекта.

    Функции:
    - Выбор tech stack
    - Проектирование архитектуры
    - Определение компонентов
    - Database schema design
    """

    def __init__(self, llm):
        """
        Инициализация архитектора.

        Args:
            llm: LLM клиент
        """
        self.llm = llm

        # Готовые tech stacks для разных типов проектов
        self.tech_stacks = {
            "nextjs-saas": {
                "frontend": "Next.js 14 + TypeScript + Tailwind CSS",
                "backend": "Next.js API Routes",
                "database": "PostgreSQL (Supabase)",
                "auth": "NextAuth.js",
                "hosting": "vercel",
                "template": "nextjs-saas-starter"
            },
            "nextjs-landing": {
                "frontend": "Next.js 14 + TypeScript + Tailwind CSS",
                "backend": "None (static)",
                "database": "None",
                "auth": "None",
                "hosting": "vercel",
                "template": "nextjs-landing-template"
            },
            "fastapi-api": {
                "frontend": "None (API only)",
                "backend": "FastAPI + Python",
                "database": "PostgreSQL",
                "auth": "JWT",
                "hosting": "railway",
                "template": "fastapi-starter"
            }
        }

    async def design_architecture(
        self,
        business_idea: Dict[str, Any],
        tech_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Спроектировать архитектуру приложения.

        Args:
            business_idea: Бизнес-идея
            tech_spec: Техническое задание

        Returns:
            Dict: Архитектура проекта
        """
        # Выбираем подходящий tech stack
        tech_stack_key = self._select_tech_stack(business_idea)
        tech_stack = self.tech_stacks[tech_stack_key]

        # Генерируем детальную архитектуру с помощью LLM
        prompt = self._create_architecture_prompt(business_idea, tech_spec, tech_stack)

        response = await self.llm.generate(
            prompt=prompt,
            max_tokens=3000,
            temperature=0.3
        )

        # Парсим ответ
        architecture = self._parse_architecture(response)

        # Добавляем выбранный tech stack
        architecture["tech_stack"] = tech_stack

        logger.info(f"Architecture designed: {tech_stack_key}")

        return architecture

    def _select_tech_stack(self, business_idea: Dict[str, Any]) -> str:
        """
        Выбрать подходящий tech stack.

        Args:
            business_idea: Бизнес-идея

        Returns:
            str: Ключ tech stack
        """
        complexity = business_idea.get("technical_complexity", "medium")
        category = business_idea.get("category", "unknown")

        # Простые проекты → Landing page
        if complexity == "low":
            return "nextjs-landing"

        # SaaS проекты → Next.js full-stack
        if "saas" in category.lower() or complexity in ["medium", "high"]:
            return "nextjs-saas"

        # API-only проекты
        if "api" in business_idea.get("description", "").lower():
            return "fastapi-api"

        # Default
        return "nextjs-saas"

    def _create_architecture_prompt(
        self,
        business_idea: Dict[str, Any],
        tech_spec: Dict[str, Any],
        tech_stack: Dict[str, Any]
    ) -> str:
        """Создать промпт для проектирования архитектуры."""

        return f"""Design a detailed technical architecture for this SaaS application.

**Product:**
- Name: {business_idea['name']}
- Description: {business_idea['description']}
- Features: {', '.join(business_idea['key_features'])}

**Tech Stack (predetermined):**
- Frontend: {tech_stack['frontend']}
- Backend: {tech_stack['backend']}
- Database: {tech_stack['database']}
- Auth: {tech_stack['auth']}

**Requirements:**
{json.dumps(tech_spec.get('mvp_scope', []), indent=2)}

Generate architecture in JSON format:

{{
  "description": "Brief architecture overview (2-3 sentences)",
  "components": [
    {{
      "name": "Homepage",
      "type": "page",
      "file_path": "src/app/page.tsx",
      "description": "Main landing page",
      "dependencies": ["Hero", "Features", "CTA"]
    }},
    {{
      "name": "API: Generate",
      "type": "api",
      "file_path": "src/app/api/generate/route.ts",
      "description": "Main API endpoint for generation",
      "dependencies": []
    }},
    {{
      "name": "AuthProvider",
      "type": "component",
      "file_path": "src/components/AuthProvider.tsx",
      "description": "Authentication context provider",
      "dependencies": ["NextAuth"]
    }}
  ],
  "database_schema": [
    {{
      "table": "users",
      "columns": [
        {{"name": "id", "type": "uuid", "primary_key": true}},
        {{"name": "email", "type": "varchar", "unique": true}},
        {{"name": "created_at", "type": "timestamp"}}
      ]
    }}
  ],
  "api_endpoints": [
    {{
      "path": "/api/generate",
      "method": "POST",
      "description": "Generate content",
      "auth_required": true
    }}
  ],
  "environment_variables": [
    {{"name": "DATABASE_URL", "description": "PostgreSQL connection string"}},
    {{"name": "NEXTAUTH_SECRET", "description": "NextAuth secret key"}}
  ]
}}

Requirements:
- Focus on MVP - keep it simple
- All components should be functional and ready to code
- Use modern best practices
- Include only essential features
- Make it deployable in one go"""

        return prompt

    def _parse_architecture(self, response: str) -> Dict[str, Any]:
        """Парсинг ответа от LLM."""
        import re

        try:
            # Извлекаем JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                architecture = json.loads(json_match.group())
                return architecture
        except:
            pass

        # Default architecture
        return {
            "description": "Standard Next.js SaaS application",
            "components": [],
            "database_schema": [],
            "api_endpoints": [],
            "environment_variables": []
        }


# Пример использования
if __name__ == "__main__":
    import asyncio

    async def main():
        # Mock LLM
        class MockLLM:
            async def generate(self, prompt: str, **kwargs):
                return """
{
  "description": "Modern Next.js SaaS application with AI-powered features",
  "components": [
    {
      "name": "Homepage",
      "type": "page",
      "file_path": "src/app/page.tsx",
      "description": "Landing page with hero and features",
      "dependencies": ["Hero", "Features"]
    }
  ],
  "database_schema": [
    {
      "table": "users",
      "columns": [
        {"name": "id", "type": "uuid", "primary_key": true},
        {"name": "email", "type": "varchar", "unique": true}
      ]
    }
  ],
  "api_endpoints": [
    {
      "path": "/api/generate",
      "method": "POST",
      "description": "Generate AI content",
      "auth_required": true
    }
  ],
  "environment_variables": [
    {"name": "DATABASE_URL", "description": "PostgreSQL URL"},
    {"name": "OPENAI_API_KEY", "description": "OpenAI API key"}
  ]
}
"""

        architect = ProjectArchitect(llm=MockLLM())

        business_idea = {
            "name": "TaskFlow AI",
            "description": "AI PM tool",
            "key_features": ["AI prioritization", "Smart workflows"],
            "technical_complexity": "medium",
            "category": "productivity"
        }

        tech_spec = {
            "mvp_scope": ["User auth", "Task management", "AI suggestions"]
        }

        architecture = await architect.design_architecture(business_idea, tech_spec)

        print("Architecture:")
        print(json.dumps(architecture, indent=2))

    asyncio.run(main())

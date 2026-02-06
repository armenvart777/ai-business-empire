"""
Code Generator - генерация кода для всех компонентов проекта.

Использует LLM для генерации React компонентов, API routes, database schemas.
"""

import logging
from typing import Dict, Any, List
from pathlib import Path
import json


logger = logging.getLogger(__name__)


class CodeGenerator:
    """
    Генератор кода.

    Генерирует все файлы проекта на основе архитектуры.
    """

    def __init__(self, llm):
        """
        Инициализация генератора.

        Args:
            llm: LLM клиент
        """
        self.llm = llm

    async def generate_project(
        self,
        architecture: Dict[str, Any],
        business_idea: Dict[str, Any],
        output_dir: Path
    ) -> List[str]:
        """
        Сгенерировать весь проект.

        Args:
            architecture: Архитектура из ProjectArchitect
            business_idea: Бизнес-идея
            output_dir: Директория для сохранения файлов

        Returns:
            List[str]: Список сгенерированных файлов
        """
        generated_files = []

        # Генерируем каждый компонент
        for component in architecture.get("components", []):
            file_path = await self._generate_component(
                component=component,
                business_idea=business_idea,
                output_dir=output_dir
            )

            if file_path:
                generated_files.append(str(file_path))

        # Генерируем конфигурационные файлы
        config_files = await self._generate_config_files(
            architecture=architecture,
            business_idea=business_idea,
            output_dir=output_dir
        )

        generated_files.extend(config_files)

        # Генерируем database migrations
        if architecture.get("database_schema"):
            migration_files = await self._generate_migrations(
                schema=architecture["database_schema"],
                output_dir=output_dir
            )
            generated_files.extend(migration_files)

        # Генерируем README
        readme = await self._generate_readme(
            business_idea=business_idea,
            architecture=architecture,
            output_dir=output_dir
        )
        generated_files.append(readme)

        logger.info(f"Generated {len(generated_files)} files")

        return generated_files

    async def _generate_component(
        self,
        component: Dict[str, Any],
        business_idea: Dict[str, Any],
        output_dir: Path
    ) -> Path:
        """Генерация одного компонента."""

        component_type = component.get("type", "component")
        file_path = component.get("file_path", "")

        # Промпт для генерации
        prompt = self._create_component_prompt(component, business_idea)

        # Генерируем код
        code = await self.llm.generate(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.4
        )

        # Извлекаем код из markdown
        code_content = self._extract_code(code)

        # Сохраняем в файл
        full_path = output_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(code_content)

        logger.debug(f"Generated: {file_path}")

        return full_path

    def _create_component_prompt(
        self,
        component: Dict[str, Any],
        business_idea: Dict[str, Any]
    ) -> str:
        """Создать промпт для генерации компонента."""

        component_type = component.get("type", "component")
        name = component.get("name", "Component")
        description = component.get("description", "")

        if component_type == "page":
            return f"""Generate a Next.js 14 page component for: {name}

Description: {description}
Product: {business_idea.get('name', '')}

Requirements:
- TypeScript + React Server Component
- Tailwind CSS для стилей
- Clean, modern design
- Include basic SEO metadata

Return ONLY the code, no explanations."""

        elif component_type == "api":
            return f"""Generate a Next.js 14 API route for: {name}

Description: {description}

Requirements:
- TypeScript
- Proper error handling
- Input validation
- RESTful best practices

Return ONLY the code."""

        elif component_type == "component":
            return f"""Generate a React component for: {name}

Description: {description}

Requirements:
- TypeScript
- Functional component
- Tailwind CSS
- Proper TypeScript types

Return ONLY the code."""

        return f"Generate code for: {name}"

    def _extract_code(self, response: str) -> str:
        """Извлечь код из markdown ответа."""
        import re

        # Ищем код в markdown блоках
        code_blocks = re.findall(r'```(?:typescript|tsx|ts|javascript|jsx)?\n(.*?)```', response, re.DOTALL)

        if code_blocks:
            return code_blocks[0].strip()

        # Если нет code blocks, возвращаем весь ответ
        return response.strip()

    async def _generate_config_files(
        self,
        architecture: Dict[str, Any],
        business_idea: Dict[str, Any],
        output_dir: Path
    ) -> List[str]:
        """Генерация конфигурационных файлов."""

        files = []

        # package.json
        package_json = {
            "name": business_idea.get("name", "app").lower().replace(" ", "-"),
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "14.0.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "typescript": "^5.0.0",
                "@types/react": "^18.2.0",
                "@types/node": "^20.0.0",
                "tailwindcss": "^3.3.0",
                "autoprefixer": "^10.4.16",
                "postcss": "^8.4.31"
            }
        }

        package_path = output_dir / "package.json"
        with open(package_path, "w") as f:
            json.dump(package_json, f, indent=2)
        files.append(str(package_path))

        # .env.example
        env_vars = architecture.get("environment_variables", [])
        env_content = "\n".join(
            f"{var['name']}=# {var.get('description', '')}"
            for var in env_vars
        )

        env_path = output_dir / ".env.example"
        with open(env_path, "w") as f:
            f.write(env_content)
        files.append(str(env_path))

        # .gitignore
        gitignore_content = """node_modules/
.next/
.env
.env.local
.vercel
dist/
build/
*.log"""

        gitignore_path = output_dir / ".gitignore"
        with open(gitignore_path, "w") as f:
            f.write(gitignore_content)
        files.append(str(gitignore_path))

        return files

    async def _generate_migrations(
        self,
        schema: List[Dict[str, Any]],
        output_dir: Path
    ) -> List[str]:
        """Генерация database migrations (SQL)."""

        files = []

        # Создаем SQL миграцию
        sql_content = "-- Database schema\n\n"

        for table in schema:
            table_name = table.get("table", "unknown")
            columns = table.get("columns", [])

            sql_content += f"CREATE TABLE {table_name} (\n"

            column_defs = []
            for col in columns:
                col_def = f"  {col['name']} {col['type']}"

                if col.get("primary_key"):
                    col_def += " PRIMARY KEY"
                if col.get("unique"):
                    col_def += " UNIQUE"
                if col.get("not_null"):
                    col_def += " NOT NULL"
                if col.get("default"):
                    col_def += f" DEFAULT {col['default']}"

                column_defs.append(col_def)

            sql_content += ",\n".join(column_defs)
            sql_content += "\n);\n\n"

        # Сохраняем
        migrations_dir = output_dir / "migrations"
        migrations_dir.mkdir(exist_ok=True)

        migration_path = migrations_dir / "001_initial_schema.sql"
        with open(migration_path, "w") as f:
            f.write(sql_content)

        files.append(str(migration_path))

        return files

    async def _generate_readme(
        self,
        business_idea: Dict[str, Any],
        architecture: Dict[str, Any],
        output_dir: Path
    ) -> str:
        """Генерация README.md."""

        readme_content = f"""# {business_idea.get('name', 'Project')}

{business_idea.get('tagline', '')}

## Description

{business_idea.get('description', '')}

## Features

{chr(10).join(f"- {feature}" for feature in business_idea.get('key_features', []))}

## Tech Stack

{chr(10).join(f"- **{k.title()}**: {v}" for k, v in architecture.get('tech_stack', {}).items())}

## Getting Started

### Prerequisites

- Node.js 18+
- PostgreSQL (or Supabase account)

### Installation

1. Clone the repository
2. Install dependencies:

```bash
npm install
```

3. Copy `.env.example` to `.env` and fill in the values

4. Run database migrations (if needed)

5. Start development server:

```bash
npm run dev
```

6. Open http://localhost:3000

## Deployment

Deploy to Vercel:

```bash
vercel
```

## License

MIT

---

🤖 Generated by [AI Business Empire](https://github.com/armenvart777/ai-business-empire)
"""

        readme_path = output_dir / "README.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        return str(readme_path)


# Пример использования
if __name__ == "__main__":
    import asyncio
    import tempfile

    async def main():
        # Mock LLM
        class MockLLM:
            async def generate(self, prompt: str, **kwargs):
                return """
```tsx
export default function HomePage() {
  return (
    <div className="min-h-screen">
      <h1>Welcome to TaskFlow AI</h1>
    </div>
  )
}
```
"""

        generator = CodeGenerator(llm=MockLLM())

        architecture = {
            "components": [
                {
                    "name": "Homepage",
                    "type": "page",
                    "file_path": "src/app/page.tsx",
                    "description": "Main landing page"
                }
            ],
            "database_schema": [],
            "tech_stack": {
                "frontend": "Next.js 14",
                "backend": "Next.js API",
                "database": "PostgreSQL"
            },
            "environment_variables": [
                {"name": "DATABASE_URL", "description": "PostgreSQL URL"}
            ]
        }

        business_idea = {
            "name": "TaskFlow AI",
            "tagline": "PM that thinks",
            "description": "AI-powered project management",
            "key_features": ["AI prioritization", "Smart workflows"]
        }

        # Генерируем в временную директорию
        with tempfile.TemporaryDirectory() as tmpdir:
            files = await generator.generate_project(
                architecture=architecture,
                business_idea=business_idea,
                output_dir=Path(tmpdir)
            )

            print(f"Generated {len(files)} files:")
            for file in files[:5]:
                print(f"  - {file}")

    asyncio.run(main())

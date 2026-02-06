"""
Developer Agent - автоматическая разработка MVP для бизнесов.

Функции:
- Генерация технического задания из бизнес-идеи
- Создание архитектуры приложения
- Генерация кода (используя Claude Code)
- Создание GitHub репозитория
- Настройка CI/CD (GitHub Actions)
- Деплой на Vercel/Railway
- Мониторинг и health checks
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path
import subprocess
import tempfile

from agents.shared.template_agent import TemplateAgent, AgentConfig
from agents.developer.architect import ProjectArchitect
from agents.developer.code_generator import CodeGenerator
from agents.developer.github_manager import GitHubManager
from agents.developer.deployer import Deployer


class DeveloperAgent(TemplateAgent):
    """
    Developer Agent - создание MVP от идеи до деплоя.

    Workflow:
    1. Получить одобренную бизнес-идею
    2. Создать техническое задание
    3. Спроектировать архитектуру
    4. Выбрать tech stack
    5. Создать GitHub репозиторий
    6. Сгенерировать код для всех компонентов
    7. Push код в GitHub
    8. Настроить CI/CD (GitHub Actions)
    9. Создать Pull Request
    10. Дождаться CI/CD
    11. Auto-merge if tests pass
    12. Деплой на Vercel
    13. Вернуть production URL
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Инициализация Developer Agent.

        Args:
            config: Конфигурация агента
        """
        config = config or AgentConfig(
            name="developer-agent",
            llm_model="claude-sonnet-3-5-20241022",  # Мощная модель для кода
            temperature=0.3,  # Меньше креативности, больше точности
            max_tokens=4000
        )
        super().__init__(config)

        # Компоненты
        self.architect = ProjectArchitect(llm=self.llm)
        self.code_generator = CodeGenerator(llm=self.llm)
        self.github_manager = GitHubManager()
        self.deployer = Deployer()

        # Путь для локальной разработки
        self.workspace_dir = Path(__file__).parent.parent.parent / "workspace"
        self.workspace_dir.mkdir(exist_ok=True)

        # Путь для сохранения проектов
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "projects"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("Developer Agent initialized")

    async def create_mvp(
        self,
        business_idea: Dict[str, Any],
        auto_deploy: bool = True,
        auto_merge: bool = True
    ) -> Dict[str, Any]:
        """
        Создать MVP от идеи до production.

        Args:
            business_idea: Бизнес-идея от Business Generator
            auto_deploy: Автоматический деплой после merge
            auto_merge: Автоматический merge PR после успешного CI

        Returns:
            Dict: Результат разработки с URLs и метриками
        """
        business_id = business_idea.get("id", "unknown")
        business_name = business_idea.get("name", "Unnamed")

        self.logger.info(f"Starting MVP development for: {business_name}")

        try:
            # 1. Создать техническое задание
            self.logger.info("Step 1/13: Creating technical specification...")
            tech_spec = await self._create_tech_spec(business_idea)

            # 2. Спроектировать архитектуру
            self.logger.info("Step 2/13: Designing architecture...")
            architecture = await self.architect.design_architecture(
                business_idea=business_idea,
                tech_spec=tech_spec
            )

            # 3. Выбрать tech stack
            self.logger.info("Step 3/13: Selecting tech stack...")
            tech_stack = architecture["tech_stack"]

            # 4. Создать GitHub репозиторий
            self.logger.info("Step 4/13: Creating GitHub repository...")
            repo = await self.github_manager.create_repository(
                business_id=business_id,
                name=self._slugify(business_name),
                description=business_idea.get("tagline", ""),
                template=tech_stack.get("template")
            )

            # 5. Клонировать локально
            self.logger.info("Step 5/13: Cloning repository...")
            local_path = await self._clone_repository(repo["clone_url"])

            # 6. Генерировать код
            self.logger.info("Step 6/13: Generating code...")
            generated_files = await self.code_generator.generate_project(
                architecture=architecture,
                business_idea=business_idea,
                output_dir=local_path
            )

            self.logger.info(f"Generated {len(generated_files)} files")

            # 7. Создать feature branch
            self.logger.info("Step 7/13: Creating feature branch...")
            branch_name = "feature/initial-mvp"
            await self._git_create_branch(local_path, branch_name)

            # 8. Commit код
            self.logger.info("Step 8/13: Committing code...")
            await self._git_commit_all(
                local_path,
                message=f"feat: Initial MVP for {business_name}\n\nGenerated by Developer Agent"
            )

            # 9. Push в GitHub
            self.logger.info("Step 9/13: Pushing to GitHub...")
            await self._git_push(local_path, branch_name)

            # 10. Создать Pull Request
            self.logger.info("Step 10/13: Creating Pull Request...")
            pr = await self.github_manager.create_pull_request(
                repo_name=repo["full_name"],
                head_branch=branch_name,
                base_branch="main",
                title=f"🚀 Initial MVP: {business_name}",
                body=self._generate_pr_description(business_idea, architecture)
            )

            # 11. Дождаться CI/CD
            self.logger.info("Step 11/13: Waiting for CI/CD...")
            ci_success = await self._wait_for_ci(
                repo_name=repo["full_name"],
                pr_number=pr["number"],
                timeout=600  # 10 минут
            )

            if not ci_success:
                raise Exception("CI/CD failed. Check logs on GitHub.")

            deployment_url = None

            if auto_merge and ci_success:
                # 12. Auto-merge PR
                self.logger.info("Step 12/13: Merging Pull Request...")
                await self.github_manager.merge_pull_request(
                    repo_name=repo["full_name"],
                    pr_number=pr["number"],
                    method="squash"
                )

                if auto_deploy:
                    # 13. Дождаться деплоя
                    self.logger.info("Step 13/13: Waiting for deployment...")
                    deployment_url = await self.deployer.wait_for_deployment(
                        repo_name=repo["full_name"],
                        timeout=300  # 5 минут
                    )

            # Сохранить результат
            result = {
                "business_id": business_id,
                "business_name": business_name,
                "status": "deployed" if deployment_url else "developed",
                "repository": {
                    "name": repo["name"],
                    "url": repo["html_url"],
                    "clone_url": repo["clone_url"]
                },
                "pull_request": {
                    "number": pr["number"],
                    "url": pr["html_url"],
                    "merged": auto_merge and ci_success
                },
                "deployment": {
                    "url": deployment_url,
                    "provider": tech_stack.get("hosting", "vercel")
                },
                "tech_stack": tech_stack,
                "files_generated": len(generated_files),
                "architecture": architecture,
                "created_at": datetime.now().isoformat()
            }

            await self._save_project(result)

            self.logger.info(f"✅ MVP created successfully: {deployment_url or repo['html_url']}")

            return result

        except Exception as e:
            self.logger.error(f"❌ Failed to create MVP: {e}")
            raise

    async def _create_tech_spec(
        self,
        business_idea: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Создать техническое задание из бизнес-идеи.

        Args:
            business_idea: Бизнес-идея

        Returns:
            Dict: Техническое задание
        """
        prompt = f"""Create a detailed technical specification for this SaaS product.

Business Idea:
- Name: {business_idea['name']}
- Tagline: {business_idea['tagline']}
- Description: {business_idea['description']}
- Target Audience: {business_idea['target_audience']}
- Key Features: {', '.join(business_idea['key_features'])}
- Revenue Model: {business_idea['revenue_model']}

Generate technical specification in JSON format:

{{
  "user_stories": [
    "As a <user>, I want to <action> so that <benefit>",
    ...
  ],
  "functional_requirements": [
    "Requirement 1",
    "Requirement 2",
    ...
  ],
  "non_functional_requirements": {{
    "performance": "Page load < 2s",
    "security": "Authentication required",
    "scalability": "Support 1000 concurrent users"
  }},
  "mvp_scope": [
    "Feature 1 (must have)",
    "Feature 2 (must have)",
    ...
  ],
  "future_features": [
    "Feature X (nice to have)",
    ...
  ]
}}

Focus on MVP - minimum viable product. Keep it simple and achievable in {business_idea.get('time_to_mvp_weeks', 4)} weeks."""

        response = await self.llm.generate(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.3
        )

        # Parse JSON
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())

        return {}

    async def _clone_repository(self, clone_url: str) -> Path:
        """
        Клонировать репозиторий локально.

        Args:
            clone_url: URL для клонирования

        Returns:
            Path: Путь к локальной копии
        """
        # Создаем временную директорию
        repo_name = clone_url.split("/")[-1].replace(".git", "")
        local_path = self.workspace_dir / repo_name

        # Удаляем если существует
        if local_path.exists():
            import shutil
            shutil.rmtree(local_path)

        # Клонируем
        subprocess.run(
            ["git", "clone", clone_url, str(local_path)],
            check=True,
            capture_output=True
        )

        return local_path

    async def _git_create_branch(self, repo_path: Path, branch_name: str):
        """Создать новую ветку."""
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=repo_path,
            check=True,
            capture_output=True
        )

    async def _git_commit_all(self, repo_path: Path, message: str):
        """Закоммитить все изменения."""
        # Add all files
        subprocess.run(
            ["git", "add", "."],
            cwd=repo_path,
            check=True
        )

        # Commit
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            check=True,
            capture_output=True
        )

    async def _git_push(self, repo_path: Path, branch_name: str):
        """Push в remote."""
        subprocess.run(
            ["git", "push", "-u", "origin", branch_name],
            cwd=repo_path,
            check=True,
            capture_output=True
        )

    def _generate_pr_description(
        self,
        business_idea: Dict[str, Any],
        architecture: Dict[str, Any]
    ) -> str:
        """Генерация описания PR."""
        return f"""## 🚀 Initial MVP: {business_idea['name']}

**Tagline:** {business_idea['tagline']}

### Features

{chr(10).join(f"- {feature}" for feature in business_idea['key_features'])}

### Tech Stack

- **Frontend:** {architecture['tech_stack'].get('frontend', 'N/A')}
- **Backend:** {architecture['tech_stack'].get('backend', 'N/A')}
- **Database:** {architecture['tech_stack'].get('database', 'N/A')}
- **Hosting:** {architecture['tech_stack'].get('hosting', 'N/A')}

### Architecture

{architecture.get('description', 'N/A')}

### Revenue Model

{business_idea.get('revenue_model', 'N/A')} - {business_idea.get('pricing', 'N/A')}

### Target Audience

{business_idea.get('target_audience', 'N/A')}

---

🤖 Generated by [Developer Agent](https://github.com/armenvart777/ai-business-empire)
"""

    async def _wait_for_ci(
        self,
        repo_name: str,
        pr_number: int,
        timeout: int = 600
    ) -> bool:
        """
        Дождаться завершения CI/CD.

        Args:
            repo_name: Имя репозитория
            pr_number: Номер PR
            timeout: Таймаут в секундах

        Returns:
            bool: True если CI прошел успешно
        """
        import time
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = await self.github_manager.get_pr_status(repo_name, pr_number)

            if status == "success":
                return True
            elif status == "failure":
                return False

            # Ждем 10 секунд
            await asyncio.sleep(10)

        # Timeout
        return False

    async def _save_project(self, project: Dict[str, Any]):
        """Сохранить информацию о проекте."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / f"project_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(project, f, indent=2, ensure_ascii=False)

        # Latest
        latest_file = self.data_dir / "latest.json"
        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(project, f, indent=2, ensure_ascii=False)

    def _slugify(self, text: str) -> str:
        """Преобразовать текст в slug."""
        import re
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        text = text.strip('-')
        return text


# Пример использования
if __name__ == "__main__":
    async def main():
        # Пример бизнес-идеи (от Business Generator)
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

        print(f"\n✅ MVP Created!")
        print(f"Repository: {result['repository']['url']}")
        print(f"Pull Request: {result['pull_request']['url']}")
        print(f"Deployment: {result['deployment']['url']}")

    asyncio.run(main())

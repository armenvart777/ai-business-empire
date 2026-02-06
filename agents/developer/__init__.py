"""
Developer Agent - автоматическая разработка MVP.

Экспорты:
- DeveloperAgent: Основной класс агента
- ProjectArchitect: Проектирование архитектуры
- CodeGenerator: Генерация кода
- GitHubManager: Управление GitHub
- Deployer: Деплой на Vercel/Railway
"""

from agents.developer.agent import DeveloperAgent
from agents.developer.architect import ProjectArchitect
from agents.developer.code_generator import CodeGenerator
from agents.developer.github_manager import GitHubManager
from agents.developer.deployer import Deployer

__all__ = [
    "DeveloperAgent",
    "ProjectArchitect",
    "CodeGenerator",
    "GitHubManager",
    "Deployer"
]

__version__ = "0.1.0"

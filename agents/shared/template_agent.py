"""
Template для создания нового агента.

Скопируйте этот файл в новую директорию агента и модифицируйте под свои нужды.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

# Импорты из shared модулей
from agents.shared.llm_client import LLMClient
from agents.shared.cache import Cache
from agents.shared.logger import setup_logger


@dataclass
class AgentConfig:
    """Конфигурация агента"""
    name: str
    llm_model: str = "gpt-4o-mini"  # Дешёвая модель по умолчанию
    max_retries: int = 3
    timeout: int = 30
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 час


class TemplateAgent:
    """
    Template класс для AI-агента.

    Каждый агент должен наследовать этот шаблон или следовать похожей структуре.
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Инициализация агента.

        Args:
            config: Конфигурация агента. Если не указана, используются дефолтные значения.
        """
        self.config = config or AgentConfig(name="template-agent")
        self.logger = setup_logger(self.config.name)
        self.llm = LLMClient(model=self.config.llm_model)
        self.cache = Cache(enabled=self.config.cache_enabled, ttl=self.config.cache_ttl)

        self.logger.info(f"Initialized {self.config.name} agent")

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Главный метод выполнения агента.

        Args:
            input_data: Входные данные для агента

        Returns:
            Результат работы агента

        Raises:
            ValueError: Если входные данные некорректны
            RuntimeError: Если произошла ошибка при выполнении
        """
        start_time = datetime.now()
        self.logger.info(f"Starting agent run with input: {input_data}")

        try:
            # 1. Валидация входных данных
            self._validate_input(input_data)

            # 2. Проверка кэша
            cache_key = self._get_cache_key(input_data)
            cached_result = self.cache.get(cache_key)
            if cached_result:
                self.logger.info("Returning cached result")
                return cached_result

            # 3. Основная логика агента
            result = self._execute(input_data)

            # 4. Валидация результата
            self._validate_output(result)

            # 5. Сохранение в кэш
            self.cache.set(cache_key, result)

            # 6. Логирование метрик
            duration = (datetime.now() - start_time).total_seconds()
            self._log_metrics(duration, result)

            return result

        except Exception as e:
            self.logger.error(f"Error in agent run: {str(e)}", exc_info=True)
            raise

    def _validate_input(self, input_data: Dict[str, Any]) -> None:
        """
        Валидация входных данных.

        Args:
            input_data: Данные для валидации

        Raises:
            ValueError: Если данные невалидны
        """
        # Пример валидации
        required_fields = ["field1", "field2"]  # Заменить на реальные поля

        for field in required_fields:
            if field not in input_data:
                raise ValueError(f"Missing required field: {field}")

        self.logger.debug("Input validation passed")

    def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Основная логика агента. ПЕРЕОПРЕДЕЛИТЬ В НАСЛЕДНИКЕ!

        Args:
            input_data: Входные данные

        Returns:
            Результат работы агента
        """
        # Пример использования LLM
        prompt = self._build_prompt(input_data)
        llm_response = self.llm.generate(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.7
        )

        # Обработка ответа LLM
        result = self._parse_llm_response(llm_response)

        return result

    def _build_prompt(self, input_data: Dict[str, Any]) -> str:
        """
        Построение промпта для LLM.

        Args:
            input_data: Входные данные

        Returns:
            Сформированный промпт
        """
        # Загружаем промпт из файла
        prompt_template = self._load_prompt_template("main_prompt.txt")

        # Заполняем переменные
        prompt = prompt_template.format(**input_data)

        return prompt

    def _load_prompt_template(self, filename: str) -> str:
        """
        Загрузка промпт-шаблона из файла.

        Args:
            filename: Имя файла в директории prompts/

        Returns:
            Содержимое промпта
        """
        # Путь к файлу промпта
        import os
        agent_dir = os.path.dirname(__file__)
        prompt_path = os.path.join(agent_dir, "prompts", filename)

        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Парсинг ответа от LLM.

        Args:
            response: Ответ от LLM

        Returns:
            Структурированный результат
        """
        # Пример парсинга JSON из ответа
        import json

        try:
            # Предполагаем, что LLM возвращает JSON
            parsed = json.loads(response)
            return parsed
        except json.JSONDecodeError:
            # Если не JSON, возвращаем как текст
            return {"output": response}

    def _validate_output(self, output: Dict[str, Any]) -> None:
        """
        Валидация выходных данных.

        Args:
            output: Данные для валидации

        Raises:
            ValueError: Если данные невалидны
        """
        # Пример валидации
        if not output:
            raise ValueError("Output is empty")

        self.logger.debug("Output validation passed")

    def _get_cache_key(self, input_data: Dict[str, Any]) -> str:
        """
        Генерация ключа для кэша.

        Args:
            input_data: Входные данные

        Returns:
            Ключ кэша
        """
        import hashlib
        import json

        # Создаём уникальный хэш из входных данных
        data_str = json.dumps(input_data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()

    def _log_metrics(self, duration: float, result: Dict[str, Any]) -> None:
        """
        Логирование метрик выполнения.

        Args:
            duration: Время выполнения в секундах
            result: Результат работы
        """
        metrics = {
            "agent": self.config.name,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat(),
            "llm_tokens_used": self.llm.get_tokens_used(),
            "llm_cost_usd": self.llm.get_cost(),
            "cache_hit": getattr(self, '_cache_hit', False)
        }

        self.logger.info(f"Agent metrics: {metrics}")

        # Можно отправлять метрики в monitoring систему
        # self._send_to_monitoring(metrics)


# Пример использования
if __name__ == "__main__":
    # Создание агента
    config = AgentConfig(
        name="example-agent",
        llm_model="gpt-4o-mini",
        cache_enabled=True
    )

    agent = TemplateAgent(config)

    # Запуск агента
    input_data = {
        "field1": "value1",
        "field2": "value2"
    }

    result = agent.run(input_data)
    print(f"Result: {result}")

# AI Support Assistant

[![Tests](https://github.com/tolendi/ai-support-assistant/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/tolendi/ai-support-assistant/actions/workflows/tests.yml)

**RU** · [English](#english)

🎬 [Демо на YouTube](https://youtu.be/jMNf9-BI0OI) — показана более ранняя версия MVP.

> **Статус:** работающий портфолио-MVP, не предназначенный для промышленного использования.

## О проекте

**AI Support Assistant** — система автоматизации поддержки клиентов через Telegram с локальной LLM и обязательным подтверждением ответов оператором (*human-in-the-loop*).

Клиент отправляет сообщение → FastAPI принимает его → Qwen3-4B определяет категорию и приоритет (при сбое используется Python fallback) → система ищет статьи базы знаний и готовит черновик → заявка сохраняется в PostgreSQL → n8n уведомляет оператора → оператор одобряет, редактирует или отклоняет ответ. **Клиент получает ответ только после одобрения.**

### Что реализовано

- Telegram webhook, автоматическое подтверждение получения заявки и защита от дубликатов.
- Классификация заявок, проверка приоритетов и поиск недостающей информации.
- Генерация черновиков на русском, английском и казахском; проверка языка и fallback-ответы.
- **RAG:** поиск статей по ключевым словам в локальном JSON и передача контекста в Qwen3.
- PostgreSQL: заявки, статусы, история, решения оператора, результаты доставки и метаданные классификации (`knowledge_article_ids`, `missing_information`), доступные через REST API.
- n8n: уведомления оператора; одобрение/отклонение в Telegram, редактирование через REST API.
- Защита webhook, API-ключ оператора, базовые фильтры опасных запросов в ответах.
- **166 пройденных тестов** в последнем локальном запуске.

### Технологии

**Python 3.12 · FastAPI · Pydantic · SQLAlchemy · PostgreSQL 17 · Qwen3-4B (локальный OpenAI-совместимый API) · n8n · Telegram Bot API · pytest · ngrok**

### Архитектура

```text
Клиент → Telegram → FastAPI → классификация (LLM / Python fallback)
                                  ↓
                          поиск статей (RAG)
                                  ↓
                     черновик ответа + проверки
                                  ↓
                              PostgreSQL
                                  ↓
                        n8n → оператор Telegram
                                  ↓
                        одобрить / отклонить
                                  ↓
                     отправка одобренного ответа
```

### Локальный запуск

1. Установить Python, PostgreSQL, n8n и локальный сервер LLM (например, Bionic или LM Studio). Для входящих Telegram webhook использовать публичный HTTPS-адрес, например через ngrok.
2. Создать окружение и установить зависимости:

   ```bash
   python -m venv .venv
   source .venv/Scripts/activate  # Windows Git Bash
   python -m pip install -r requirements.txt
   ```

3. Создать пустую базу PostgreSQL `ai_support_assistant` и выполнить в ней SQL-скрипты по порядку:
   - [`000_initial_schema.sql`](sql/000_initial_schema.sql) — создание таблиц, ограничений и индексов.
   - [`001_human_in_the_loop.sql`](sql/001_human_in_the_loop.sql) — совместимость с механизмом согласования ответов.
   - [`002_classification_metadata.sql`](sql/002_classification_metadata.sql) — добавление метаданных классификации.

   Для существующей базы с уже применённой миграцией `001` достаточно выполнить `002`. У старых заявок новые поля содержат пустые списки (исторические метаданные не восстанавливаются).
4. Скопировать `.env.example` в `.env`, указать параметры БД, Telegram, оператора и LLM. Не публиковать `.env` и токены. Для текущего варианта используются `LLM_CLASSIFIER_MODEL=qwen3-4b` и `LLM_REPLY_MODEL=qwen3-4b`.
5. Запустить API:

   ```bash
   python -m uvicorn app.main:app --reload
   ```

6. Настроить Telegram webhook с секретом, импортировать workflow из [`n8n/`](n8n/), подключить PostgreSQL и Telegram и активировать workflow.

Документация API при запущенном сервере: **http://127.0.0.1:8000/docs**. Внутренние маршруты `/tickets` требуют заголовок `X-Operator-API-Key`.

### Тестирование и оценка AI

```bash
python -m pytest -q
python -m evaluation.evaluate_classification
python -m evaluation.evaluate_replies
```

| Метрика | Результат |
| --- | ---: |
| Тесты | 166 passed (последний локальный запуск) |
| Категории, 20 обращений | 100% в обоих прогонах |
| Приоритеты, 20 обращений | 75% (первый прогон); 65% (после настройки Qwen3-4B) |
| Macro F1 по категориям | 1.0000 |
| Качество ответов, ручная оценка 10 примеров | Groundedness 80%; язык 100%; безопасность 100%; релевантность 80% |

Это **небольшие тестовые наборы**, а не производственные показатели. Классификация оценивается для всего приложения с возможным fallback, а не отдельно для LLM. Ручная оценка безопасности не гарантирует отсутствие уязвимостей.

### Ограничения и планы

- Поиск RAG основан на ключевых словах, без embeddings и векторной БД; ответы LLM могут содержать неточности.
- Фильтры безопасности и качество казахских ответов ограничены; **проверка оператором обязательна**.
- Нет полноценной системы аккаунтов и ролей; доставка сообщений не гарантирует exactly-once.
- Для полной работы интеграций нужны активные внешние сервисы; инициализация БД выполняется SQL-скриптами.

**Далее:** Надёжность доставки и логирование → улучшение базы знаний и AI Evaluation → релиз v1.0.0.

---

<a id="english"></a>

## English

🎬 [YouTube demo](https://youtu.be/jMNf9-BI0OI) — shows an earlier MVP version.

> **Status:** working portfolio MVP; not production-ready.

### Overview

**AI Support Assistant** automates Telegram customer support with a local LLM and mandatory human approval before delivering replies.

A Telegram message is received by FastAPI, classified by Qwen3-4B (with a Python-rule fallback), matched against a JSON knowledge base, and saved to PostgreSQL with a draft reply. n8n notifies the operator, who can approve or reject via Telegram or edit and approve through the REST API. **Only approved replies are sent to customers.**

### Features

- Secure Telegram webhook, acknowledgments, duplicate protection, ticket status and history.
- LLM classification, priority safeguards, missing-information detection, Python-rule fallback.
- Russian, English, and Kazakh draft replies, language validation, localized fallbacks.
- **Keyword-based RAG:** retrieve relevant JSON knowledge articles and pass them to Qwen3.
- PostgreSQL persistence, including classification metadata (`knowledge_article_ids`, `missing_information`) exposed via REST API; n8n operator notifications and Telegram inline review buttons.
- Reply delivery tracking and basic safeguards against sensitive-credential requests.
- **166 passing tests** in the latest local run.

### Stack

**Python 3.12 · FastAPI · Pydantic · SQLAlchemy · PostgreSQL 17 · Qwen3-4B (local OpenAI-compatible API) · n8n · Telegram Bot API · pytest · ngrok**

### Architecture

```text
Customer → Telegram → FastAPI → LLM classification / Python fallback
                                  ↓
                           Knowledge search (RAG)
                                  ↓
                        Draft reply + guardrails
                                  ↓
                              PostgreSQL
                                  ↓
                       n8n → Telegram operator
                                  ↓
                          Approve / reject
                                  ↓
                         Send approved reply
```

### Local setup

1. Install Python, PostgreSQL, n8n, and a local LLM API server (e.g., Bionic or LM Studio). Expose the Telegram webhook through HTTPS (e.g., ngrok).
2. Create an environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/Scripts/activate  # Windows Git Bash
   python -m pip install -r requirements.txt
   ```

3. Create an empty PostgreSQL database named `ai_support_assistant` and run the SQL scripts in order:
   - [`000_initial_schema.sql`](sql/000_initial_schema.sql) — create tables, constraints, and indexes.
   - [`001_human_in_the_loop.sql`](sql/001_human_in_the_loop.sql) — maintain compatibility with the human review workflow.
   - [`002_classification_metadata.sql`](sql/002_classification_metadata.sql) — add classification metadata.

   For an existing database with migration `001` already applied, run `002` only. Older tickets receive empty lists (historical metadata is not backfilled).
4. Configure `.env` from `.env.example` with database, Telegram, operator, and LLM settings. Do not commit secrets. The current configuration uses `qwen3-4b` for classification and reply generation.
5. Start FastAPI:

   ```bash
   python -m uvicorn app.main:app --reload
   ```

6. Register the Telegram webhook with its secret; import the workflow from [`n8n/`](n8n/), configure credentials and the operator chat, and activate it.

Swagger UI: **http://127.0.0.1:8000/docs**. Internal `/tickets` routes require `X-Operator-API-Key`.

### Tests and evaluation

```bash
python -m pytest -q
python -m evaluation.evaluate_classification
python -m evaluation.evaluate_replies
```

| Metric | Result |
| --- | ---: |
| Automated tests | 166 passed (latest local run) |
| Category accuracy (20 cases) | 100% in both runs |
| Priority accuracy (20 cases) | 75% baseline; 65% after Qwen3-4B configuration |
| Category macro F1 | 1.0000 |
| Manually scored replies (10 cases) | Groundedness 80%; language 100%; safety 100%; relevance 80% |

These are **small portfolio evaluations**, not production benchmarks. Classification scores reflect the application pipeline (which may use a rules fallback), not isolated LLM accuracy. Manual safety scores do not guarantee security.

### Limitations and roadmap

- RAG uses keyword matching rather than semantic/vector search; LLM responses may be inaccurate.
- Safety checks are limited, Kazakh output quality needs improvement, and **human approval is mandatory**.
- Single-operator authentication; no full role/account management or exactly-once message delivery guarantee.
- Full integration functionality requires running external services; database initialization uses SQL scripts.

**Next:** Delivery reliability and logging → knowledge base and AI evaluation improvements → v1.0.0 release.

---

**Author:** [tolendi](https://github.com/tolendi)

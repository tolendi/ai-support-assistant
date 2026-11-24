# AI Support Assistant

🎬 **[Watch Project Demo on YouTube](https://youtu.be/jMNf9-BI0OI)** (earlier MVP demo)

**A Telegram-based customer support automation system with human-in-the-loop approval, built with Python, FastAPI, PostgreSQL, a local LLM, and n8n.**

> **Project status:** Working portfolio MVP with human-in-the-loop review. Not production-ready.

## Overview

AI Support Assistant receives customer support messages through Telegram, classifies them by category and priority using a local LLM with a rule-based fallback, stores tickets in PostgreSQL, and automatically acknowledges incoming requests.

An n8n workflow retrieves tickets awaiting review and sends their proposed replies to an operator via Telegram. The operator can approve or reject a reply using inline buttons, or edit and approve it through the REST API. Only approved support replies are delivered to customers.

The project demonstrates AI integration, Python backend development, SQL persistence, workflow automation, human-in-the-loop decision-making, API security, and automated testing.

## Implemented Features

- **Telegram intake:** receive messages through a secured FastAPI webhook.
- **Classification:** assign a support category, priority (`critical`, `high`, `medium`, `low`), and supporting fields.
- **Local LLM with fallback:** use Qwen3 through Bionic when available; fall back to Python keyword rules when the LLM is unavailable or classification fails.
- **Automatic acknowledgment:** confirm receipt of customer requests without sending unapproved draft replies.
- **Ticket persistence:** store requests, Telegram chat IDs, and review and delivery information in PostgreSQL.
- **Ticket API:** list, filter, retrieve, and update tickets, with status transition validation and status history.
- **Operator notifications:** n8n retrieves eligible tickets awaiting review regardless of priority, sends notifications with draft replies and inline buttons, and records notifications.
- **Human-in-the-loop:** operators approve or reject draft replies in Telegram, or edit and approve replies through the REST API.
- **Approved reply delivery:** send approved responses to the original customer chat and record delivery outcomes.
- **Duplicate protection:** prevent duplicate Telegram ticket inserts, repeated approval decisions, and repeated delivery attempts through normal application flows.
- **Security:** validate Telegram webhook secrets, protect internal ticket endpoints with an operator API key, and verify the Telegram operator's user ID.
- **Automated testing:** 140 tests passed in the latest reported local run.
- **AI reply generation:** generate personalized customer support drafts using Qwen3-4B.
- **Multilingual support:** detect customer language and generate replies in Russian, English, and Kazakh.
- **Language validation:** validate the generated reply language before accepting the draft.
- **Multilingual fallback:** use predefined localized replies when LLM generation fails.
- **Missing information detection:** identify missing ticket details using category-specific rules and regular expressions.
- **Priority guardrail:** prevent the LLM from lowering rule-based ticket priorities.
- **Knowledge-base retrieval (RAG):** retrieve relevant support articles from a JSON knowledge base using keyword matching and category-based ranking.
- **Grounded reply generation:** provide retrieved article content to Qwen3 when generating customer support drafts.
- **Knowledge-aware fallback:** use safe predefined replies when no relevant knowledge articles are found.
- **Reply safety guardrails:** detect selected requests for sensitive credentials and replace flagged replies with safe fallbacks.


## Tech Stack

- **Backend:** Python 3.12, FastAPI, Pydantic, SQLAlchemy
- **Database:** PostgreSQL 17, Psycopg
- **AI:** Qwen3-1.7B for classification, Qwen3-4B for reply generation, Bionic, Python rule-based fallback
- **Language detection:** Lingua Language Detector
- **Automation:** n8n
- **Messaging:** Telegram Bot API
- **Testing:** pytest, FastAPI TestClient
- **Local webhook exposure (development):** ngrok

Docker Compose is **not** required for the current local setup.

## Architecture

Three connected processes handle intake, operator notifications, and human review.

### 1. Customer message processing

```text
Customer -> Telegram Bot -> FastAPI webhook
                               |
                               v
                     Webhook secret validation
                               |
                               v
                     LLM classification
                     (Python rules fallback)
                               |
                               v
                     Priority guardrail
                               |
                               v
                     Language detection
                               |
                               v
                     Missing information detection
                               |
                               v
                     AI reply generation (Qwen3-4B)
                               |
                               v
                     Language validation
                     (Multilingual fallback)
                               |
                               v
                     PostgreSQL: Save Ticket
                               |
                               v
                     Telegram acknowledgment
```

### 2. Operator review notifications

```text
n8n Schedule Trigger
         |
         v
PostgreSQL: Get Pending Tickets
(new + pending_review + chat_id + not previously notified)
         |
         v
Telegram: Notify Operator
(message + draft reply + Approve / Reject buttons)
         |
         v
PostgreSQL: Save Notification
```

The workflow export is located in [`n8n/`](n8n/).

### 3. Human review and reply delivery

```text
Operator -> Telegram inline button -> FastAPI webhook
                                          |
                                          v
                                 Operator ID validation
                                          |
                            +-------------+-------------+
                            |                           |
                         Approve                      Reject
                            |                           |
                     Save approval               Save rejection
                            |                           |
                     Send approved reply         No reply sent
                            |
                     Record delivery status
```

Operators can also approve, edit, reject, and initiate delivery through protected REST API endpoints.

## Human-in-the-loop (HITL)

The review workflow separates automatic acknowledgment from the actual support reply.

Draft replies are generated by Qwen3-4B using the customer message, detected language, ticket category, priority, and missing information. Multilingual predefined replies are used when generation fails.

All support replies require human approval before delivery.

### Operator actions

| Action | Behavior |
| --- | --- |
| Approve in Telegram | Approve the current draft and initiate delivery |
| Reject in Telegram | Record rejection without sending the draft |
| Approve via REST API | Submit an original or edited reply for approval |
| Send via REST API | Deliver an already approved reply |

The system records the approved text, operator ID, review timestamp, delivery status, and successful delivery timestamp.

### Status management

| Field | Supported values |
| --- | --- |
| `status` | `new`, `in_progress`, `resolved`, `closed` |
| `review_status` | `pending_review`, `approved`, `rejected` |
| `reply_status` | `pending`, `sent`, `failed` |
| `approved_reply_status` | `pending`, `sending`, `sent`, `failed`, `unknown` |

Ticket lifecycle, review decisions, acknowledgment delivery, and approved reply delivery are tracked separately. A rejected reply retains its pending delivery status but cannot be sent. An `unknown` delivery outcome is not automatically retried to reduce the risk of duplicate messages.

## Support Categories

- `payment_issue`
- `order_status`
- `delivery_issue`
- `return_refund`
- `account_access`
- `product_question`
- `complaint`
- `other`

## API Overview

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `POST` | `/tickets/classify` | Classify a message and save a ticket |
| `GET` | `/tickets` | List, filter, and paginate tickets |
| `GET` | `/tickets/{ticket_id}` | Retrieve a ticket |
| `PATCH` | `/tickets/{ticket_id}/status` | Update ticket status with transition checks |
| `GET` | `/tickets/{ticket_id}/history` | Retrieve status change history |
| `POST` | `/tickets/{ticket_id}/approve` | Approve an original or edited reply |
| `POST` | `/tickets/{ticket_id}/reject` | Reject a draft reply |
| `POST` | `/tickets/{ticket_id}/send-reply` | Send an approved reply and record the outcome |
| `POST` | `/telegram/webhook` | Process Telegram messages and operator callbacks |

All `/tickets` endpoints require the `X-Operator-API-Key` header. The Telegram webhook requires `X-Telegram-Bot-Api-Secret-Token`. The health endpoint is public.

Interactive API documentation is available at `http://127.0.0.1:8000/docs` while FastAPI is running.

## Local Setup

This project runs as a set of local services.

1. Install Python, PostgreSQL, Node.js/n8n, and optionally Bionic and ngrok.
2. Create and activate a Python virtual environment, then install dependencies:

   ```bash
   python -m venv .venv
   source .venv/Scripts/activate  # Windows Git Bash
   python -m pip install -r requirements.txt
   ```

3. Create the PostgreSQL database and base tables (`tickets`, `ticket_status_history`, and `ticket_notifications`). Ensure `telegram_update_id` is unique and nullable, `reply_status` exists, and `ticket_notifications.ticket_id` is unique and references `tickets.id`. Apply [`sql/001_human_in_the_loop.sql`](sql/001_human_in_the_loop.sql) to add the review and delivery fields. This script upgrades an existing schema; it does not initialize an empty database.
4. Configure `.env` using `.env.example` as a reference. Required application settings include:

   | Variable | Purpose |
   | --- | --- |
   | `DATABASE_URL` | PostgreSQL connection string |
   | `TELEGRAM_BOT_TOKEN` | Telegram bot token |
   | `TELEGRAM_WEBHOOK_SECRET` | Secret used by Telegram webhook validation |
   | `OPERATOR_API_KEY` | API key for internal ticket endpoints |
   | `OPERATOR_ID` | Internal operator identifier |
   | `OPERATOR_TELEGRAM_ID` | Authorized Telegram user ID |

   Configure local LLM settings as needed. Never commit `.env` or real credentials.
5. Start the API:

   ```bash
   python -m uvicorn app.main:app --reload
   ```

6. For external Telegram webhook delivery, expose port 8000 through ngrok and register the resulting HTTPS URL ending in `/telegram/webhook` using Telegram's `setWebhook` method. Supply the same `secret_token` configured in `.env` and ensure message and callback query updates are enabled.
7. Optionally start Bionic with the configured Qwen3 model and local API server. Python rules provide a fallback when it is unavailable.
8. Start n8n, import the workflow JSON from `n8n/`, reconnect PostgreSQL and Telegram credentials, and configure the operator's actual Telegram chat ID. Use the same bot for sending review buttons and receiving callbacks.
9. Review the Schedule Trigger interval, then publish/activate the workflow. Keep the required local services running.

Before sharing the workflow export, remove real credentials, local credential identifiers, and personal chat IDs.

## Testing

Run backend tests from the project root:

```bash
python -m pytest -q
```

**Latest reported local result: 140 passed.**

The suite covers classification, ticket API operations, authorization, webhook handling, approval and rejection, Telegram callbacks, delivery status transitions, and error handling. External dependencies are mocked in relevant unit tests; some tests may still require local configuration.

The following end-to-end scenarios were verified manually in the local environment:

- Telegram intake, ticket creation, and automatic acknowledgment.
- Scheduled n8n notifications containing draft replies and inline buttons.
- Operator approval and delivery of the approved reply to Telegram.
- Operator rejection without delivery of the draft reply.
- Review and delivery status persistence in PostgreSQL.

These are functional checks, not performance or production reliability benchmarks.

Additional test coverage includes:

- AI reply generation and HTTP response validation.
- Multilingual fallback scenarios.
- Reply language mismatch handling.
- Missing information detection.
- Classifier and reply generator integration.
- Rule-based priority protection.

### Manual demonstration

Run missing information detection:

```bash
python -m scripts.demo_missing_information
```

Run AI reply generation:

```bash
python -m scripts.demo_reply_generation
```

## AI Evaluation

The classification pipeline was evaluated on a labeled dataset of 20 customer support messages in English, Russian, and Kazakh.

### Baseline Results

| Metric | Result |
|---|---:|
| Category Accuracy | 100% (20/20) |
| Priority Accuracy | 75% (15/20) |
| Macro Precision (categories) | 1.0000 |
| Macro Recall (categories) | 1.0000 |
| Macro F1-score (categories) | 1.0000 |
| Evaluated Categories | 8 |

All 20 category predictions matched the expected labels. Five priority predictions differed from the manually assigned reference labels.

### Reproduce the Evaluation

Run from the project root:

```bash
python -m evaluation.evaluate_classification
```

Files:

- `evaluation/datasets/classification.csv` — labeled evaluation dataset.
- `evaluation/evaluate_classification.py` — evaluation script.
- `evaluation/classification_results.csv` — saved predictions and comparison results.

### Limitations

- The dataset contains only 20 relatively simple examples and is not representative of production traffic.
- Priority reference labels are provisional and have not been validated against a formal SLA policy.
- Results evaluate the application classification pipeline, including its fallback behavior, rather than isolated LLM performance.
- Answer quality, hallucination rate, and multilingual response quality have not been quantitatively evaluated.
- Results may vary between runs depending on the local LLM configuration and availability.

These metrics represent an initial portfolio baseline, not production-level quality assurance.

## Security and Known Limitations

- The project is a **portfolio MVP**, not a production support platform.
- RAG uses keyword-based retrieval from a small local JSON knowledge base. Semantic search, embeddings, and vector databases are not implemented.
- Retrieved articles provide context but do not guarantee factual correctness. LLM-generated replies may still contain hallucinations.
- When no relevant article is found, the reply generator uses a predefined fallback. This conservative behavior may reduce answer specificity.
- Reply safety guardrails use limited pattern matching. They may produce false positives or miss unsafe requests, especially with complex negations or unsupported languages.
- Prompt injection resistance has only been tested in limited scenarios and is not guaranteed.
- Human approval remains mandatory before sending generated support replies.
- Kazakh reply generation quality requires further improvement.
- Independent language detection and fallback replies currently support Russian, English, and Kazakh only.
- LLM endpoint and model configuration are currently hardcoded.
- Missing information detection is limited to supported patterns and formats.
- Language validation does not guarantee grammatical or factual accuracy.
- LLM-generated replies may contain hallucinations; human approval remains mandatory.
- Classification confidence is currently a fixed heuristic rather than a calibrated probability.
- Operator authentication currently supports a single configured operator. There is no full user-account or role-based access system.
- Telegram inline buttons approve the existing draft; editing is available through the REST API before approval.
- Rejected drafts cannot currently be reopened or regenerated through the review workflow.
- The local services must remain running; ngrok is used for external Telegram webhooks in development.
- Notification records are inserted after Telegram reports success. A crash between sending and recording may cause a duplicate notification. Some historical notification records were created as a baseline and do not prove delivery.
- Approved reply delivery uses status checks and row locking to reduce duplicate sends. A crash can leave a reply in `sending`; recovery and retry policies are not implemented. Exactly-once delivery is not guaranteed.
- Database setup is partly manual; the upgrade SQL script is not a complete migration framework.
- Comprehensive security, privacy, load, and fault-tolerance testing has not been performed. Avoid using real customer data.

## Roadmap

- [x] Define support categories and priority rules
- [x] Implement request schemas, validation, and FastAPI endpoints
- [x] Add PostgreSQL ticket storage and status history
- [x] Integrate local LLM classification with Python-rule fallback
- [x] Connect Telegram webhook and automatic acknowledgments
- [x] Add scheduled n8n operator notifications and notification tracking
- [x] Implement webhook security and operator authentication
- [x] Implement human-in-the-loop approval, rejection, and reply delivery
- [x] Add Telegram inline buttons for operator review
- [x] Add automated tests and verify end-to-end review scenarios
- [x] Generate personalized draft replies using Qwen3-4B
- [x] Implement multilingual support and fallback replies
- [x] Detect and validate customer language
- [x] Detect missing ticket information
- [x] Implement rule-based priority guardrails
- [x] Verify AI reply generation end-to-end
- [x] Add knowledge-base retrieval and grounded answers (RAG)
- [x] Evaluate classification accuracy and priority accuracy on a labeled dataset
- [ ] Evaluate generated answer quality on a labeled dataset
- [ ] Externalize LLM configuration through environment variables
- [ ] Implement reproducible database initialization
- [ ] Add CI pipeline for automated testing
- [ ] Improve notification and reply delivery reliability
- [ ] Improve logging and observability
- [ ] Finalize documentation and release v1.0.0

## Project Structure

```text
app/              FastAPI application, models, schemas, and services
n8n/              n8n workflow export
scripts/          Manual demonstration scripts
sql/              Database schema upgrade scripts
tests/            Automated backend tests
docs/             Project requirements and architecture notes
.env.example      Environment configuration template
README.md         Project overview and setup
requirements.txt  Python dependencies
knowledge_base/   JSON support articles for retrieval
```

## Author

GitHub: [tolendi](https://github.com/tolendi)

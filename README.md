# AI Support Assistant

**A Telegram-based customer support triage system using FastAPI, PostgreSQL, a local LLM, and n8n.**

> **Project status:** Working portfolio MVP (local development). Not production-ready.

## Overview

AI Support Assistant processes incoming customer support messages, assigns a category and priority, stores tickets, and sends an automatic reply. A separate n8n workflow checks for new high-priority tickets and alerts an operator through Telegram.

The project demonstrates API integration, Python backend development, SQL persistence, LLM-assisted classification with a rule-based fallback, workflow orchestration, and automated tests.

## Implemented Features

- **Telegram intake:** receive messages through a FastAPI webhook and send replies using the Telegram Bot API.
- **Classification:** assign a support category, priority (`critical`, `high`, `medium`, `low`), confidence, and supporting fields.
- **Local LLM with fallback:** use a locally hosted Qwen3 model through LM Studio when available; fall back to Python keyword rules when the LLM is unavailable.
- **Ticket persistence:** store incoming requests in PostgreSQL and track ticket status changes in a history table.
- **Ticket API:** list and filter tickets, retrieve a ticket, change its status with transition validation, and view status history.
- **Duplicate Telegram update handling:** use a unique Telegram update identifier to avoid duplicate ticket inserts.
- **Operator alerts:** an n8n workflow queries PostgreSQL for new `high`/`critical` tickets, sends a Telegram notification, and records the notification afterward.
- **Automated tests:** a pytest suite covering backend behavior; the latest reported local run passed **54 tests** with LM Studio turned off. Run the suite again to confirm the current count.

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Pydantic, SQLAlchemy
- **Database:** PostgreSQL 17, Psycopg
- **AI:** Qwen3 (local model via LM Studio), Python rule-based fallback
- **Automation:** n8n
- **Messaging:** Telegram Bot API
- **Testing:** pytest, FastAPI TestClient
- **Local webhook exposure (development):** ngrok

Docker Compose is **not** required for the current local setup.

## Architecture

Two connected processes operate independently:

### 1. Customer message processing

```text
Customer -> Telegram Bot -> FastAPI webhook
                               |
                               v
                     LLM classification
                     (Python rules fallback)
                               |
                               v
                           PostgreSQL
                               |
                               v
                      Telegram reply
```

### 2. Operator priority alerts

```text
n8n Schedule Trigger
         |
         v
PostgreSQL: Get Pending Tickets
  (new + high/critical + not previously recorded)
         |
         v
Telegram: Notify Operator
         |
         v
PostgreSQL: Save Notification
```

The notification workflow is exported as [`n8n/AI_Support_Assistant_Priority_Alerts_public.json`](n8n/AI_Support_Assistant_Priority_Alerts_public.json).

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
| `POST` | `/tickets/classify` | Classify a message without saving a ticket |
| `GET` | `/tickets` | List tickets; filter by status, category, and priority; paginate |
| `GET` | `/tickets/{id}` | Retrieve a ticket |
| `PATCH` | `/tickets/{id}/status` | Update ticket status with transition checks |
| `GET` | `/tickets/{id}/history` | Retrieve status change history |
| `POST` | `/telegram/webhook` | Process incoming Telegram updates |

Interactive API documentation is available at `http://127.0.0.1:8000/docs` while FastAPI is running.

## Local Setup

This project currently runs as a set of local services. The instructions below outline the verified workflow; exact credentials and database initialization depend on the local configuration and SQL scripts in the repository.

1. Install Python, PostgreSQL, Node.js/n8n, and (optionally) LM Studio and ngrok.
2. Create a Python virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   python -m pip install -r requirements.txt
   ```

3. Create and configure the PostgreSQL database and application tables (`tickets`, `ticket_status_history`, and `ticket_notifications`). Ensure `ticket_notifications.ticket_id` is unique and references `tickets.id`.
4. Configure the application's database connection and Telegram bot token using local environment settings. **Never commit `.env` or credentials.**
5. Start the API:

   ```bash
   python -m uvicorn app.main:app --reload
   ```

6. For real Telegram webhook delivery to a local server, expose port 8000 through ngrok and register the resulting HTTPS URL with Telegram.
7. Optionally start LM Studio with the locally configured model/server; the Python rules provide a fallback if it is unavailable.
8. Start n8n, import the JSON from `n8n/`, reconnect **PostgreSQL** and **Telegram** credentials, and replace `REPLACE_WITH_OPERATOR_CHAT_ID` with the operator's actual Telegram chat ID.
9. Review the **Schedule Trigger interval** in n8n, then publish/activate the workflow. Keep the required local services running.

**Note:** The exported workflow intentionally excludes credentials and local credential identifiers. It will not work immediately after import until they are configured.

## Testing

Run backend tests from the project root:

```bash
python -m pytest -q
```

An end-to-end local test has verified the following sequence: Telegram message -> ticket creation -> scheduled n8n notification -> entry in `ticket_notifications` (ticket #40). This is a functional test, not a performance or production reliability benchmark.

## Safety and Known Limitations

- The project is a **portfolio MVP**, not a production support platform.
- The current bot sends a draft reply automatically; a mandatory human approval step before sending is **not** implemented. The `requires_human_review` field is metadata, not an enforced approval workflow.
- Knowledge-base retrieval and grounded answer generation are not yet implemented end to end.
- The local services must remain running; ngrok is needed for external Telegram webhooks in the local setup.
- Notification records are inserted **after** Telegram reports success. A crash between Telegram delivery and the database insert can still lead to a duplicate notification on retry. The unique `ticket_id` constraint prevents duplicate database records, not every possible duplicate message.
- Earlier high-priority tickets were marked in `ticket_notifications` to establish a baseline without sending historical alerts; their timestamps should **not** be interpreted as proof that those notifications were delivered.
- The system has not undergone comprehensive security, privacy, load, or fault-tolerance testing. Avoid using real customer data.

## Roadmap

- [x] Define support categories and priority rules
- [x] Implement request schemas, validation, and FastAPI endpoints
- [x] Add PostgreSQL ticket storage and status history
- [x] Integrate local LLM classification with Python-rule fallback
- [x] Connect Telegram webhook and automated replies
- [x] Add scheduled n8n operator alerts and notification tracking
- [x] Add automated backend tests and run an end-to-end local demo
- [ ] Add knowledge-base retrieval and grounded answers
- [ ] Add an enforced human-review/approval workflow
- [ ] Evaluate classification quality on a labeled dataset
- [ ] Improve notification delivery guarantees, deployment, and observability

## Project Structure

```text
app/             FastAPI application, models, schemas, and services
n8n/             Sanitized n8n workflow export
tests/           Automated backend tests
docs/            Project requirements and architecture notes
README.md        Project overview and setup
requirements.txt Python dependencies
```

Additional SQL, data, or knowledge-base directories may be present depending on the repository revision.

## Author

GitHub: [tolendi](https://github.com/tolendi)

# AI Support Assistant

**An AI-powered customer support triage system built with Python, n8n, PostgreSQL, and LLMs.**

> Project status: In Progress

## Overview

AI Support Assistant is a portfolio project designed to automate the initial processing of customer support requests.

The system receives messages through Telegram, classifies them by category and priority, retrieves relevant information from a knowledge base, and generates draft replies for human review.

The goal is to demonstrate practical AI automation skills, including API integration, workflow orchestration, database design, LLM integration, and automated testing.

## Key Features

Planned features:

- **Request classification** — categorize incoming support messages.
- **Priority detection** — identify critical, high, medium, and low-priority requests.
- **AI-generated drafts** — prepare responses for human review.
- **Knowledge base integration** — ground draft replies in available support documentation.
- **PostgreSQL storage** — persist tickets and processing history.
- **Workflow automation** — orchestrate the process using n8n.
- **Human-in-the-loop** — route uncertain or sensitive cases to a human operator.
- **Error handling** — handle invalid model outputs, API failures, and duplicate events.
- **Automated testing** — evaluate classification quality and critical-case detection.

## Tech Stack

- Python
- FastAPI
- Pydantic
- PostgreSQL
- n8n
- Telegram Bot API
- Large Language Models (LLMs)
- pytest
- Docker Compose

## Architecture

```text
Telegram Bot
     |
     v
    n8n
     |
     v
Python / FastAPI
     |
     +------> LLM
     |          |
     |          v
     |     Classification
     |     and draft reply
     |
     +------> PostgreSQL
     |          |
     |          v
     |     Tickets and history
     |
     v
Human Review
```

## Support Categories

The initial version will support the following categories:

- `payment_issue`
- `order_status`
- `delivery_issue`
- `return_refund`
- `account_access`
- `product_question`
- `complaint`
- `other`

## Safety and Reliability

The system is designed with the following principles:

- AI-generated replies require human approval before being sent to customers.
- Invalid or unexpected model outputs must be validated before processing.
- Low-confidence classifications are routed for human review.
- Critical requests are escalated according to predefined business rules.
- Duplicate Telegram events should not create duplicate tickets.
- Secrets and API credentials must not be committed to version control.

## Testing and Evaluation

The project will include a labeled dataset of sample support requests and automated tests.

Planned evaluation metrics:

- Classification accuracy and per-category precision/recall.
- Recall for critical requests.
- Rate of requests routed for human review.
- Correctness of knowledge-base references.
- Duplicate-event handling and error recovery.

Results will be documented after implementation and testing.

## Project Structure

```text
app/             Python application
sql/             Database migrations and seed data
n8n/             Workflow exports
knowledge_base/  Sample support articles
tests/           Automated tests
data/            Sample support requests
docs/            Architecture and requirements
```

## Getting Started

Setup instructions will be added after the initial implementation.

## Limitations

This is an educational portfolio project. It is not intended for production use without further security, reliability, privacy, and performance testing.

## Roadmap

- [ ] Define requirements and prioritization rules
- [ ] Implement request schemas and validation
- [ ] Set up PostgreSQL storage
- [ ] Integrate an LLM for classification
- [ ] Implement knowledge-base retrieval
- [ ] Generate draft replies
- [ ] Connect Telegram and n8n
- [ ] Add automated tests and evaluation metrics
- [ ] Prepare a working demo

## Author

GitHub: [tolendi](https://github.com/tolendi)

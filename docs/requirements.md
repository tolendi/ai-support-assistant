# AI Support Assistant — Requirements

## 1. Project Goal

Build an AI-powered customer support assistant that receives customer requests through Telegram, classifies them by category and priority, retrieves relevant information from a knowledge base, and generates draft replies for human review.

The system is designed as a portfolio project demonstrating AI automation, API integration, workflow orchestration, database management, and automated testing.

## 2. Scope

### In Scope

- Receive text messages through Telegram.
- Validate incoming requests.
- Classify requests using an LLM.
- Assign a priority to each request.
- Identify missing information needed to resolve a request.
- Retrieve relevant knowledge-base articles.
- Generate draft replies grounded in available information.
- Store requests and processing results in PostgreSQL.
- Route uncertain or sensitive requests for human review.
- Handle duplicate events and processing failures.
- Evaluate system quality using a labeled test dataset.

### Out of Scope

- Automatically sending AI-generated replies to customers.
- Processing real payments or issuing refunds.
- Accessing real customer accounts or order-management systems.
- Handling voice messages, images, and attachments in the initial version.
- Autonomous execution of sensitive customer-support actions.

## 3. Request Categories

Each request must be assigned exactly one category.

| Category | Description |
|---|---|
| `payment_issue` | Payment failures, unexpected charges, missing payment confirmation |
| `order_status` | Order confirmation and order-status questions |
| `delivery_issue` | Delivery delays and courier-related problems |
| `return_refund` | Product returns and refund requests |
| `account_access` | Login problems and account access |
| `product_question` | Product information, availability, and specifications |
| `complaint` | Complaints about service or customer experience |
| `other` | Requests that do not fit another category |

If the category cannot be determined reliably, the system must flag the request for human review. The output must still conform to the defined data schema.

## 4. Priority Levels

Each request must have exactly one priority level.

| Priority | Description |
|---|---|
| `critical` | Potential security incident, suspected account compromise, or suspected widespread payment issue |
| `high` | Significant payment problems or other issues requiring prompt investigation |
| `medium` | Delivery problems, routine refund questions, or account-access issues without security indicators |
| `low` | General product questions and other non-urgent requests |

### Prioritization Rules

1. Known critical indicators must trigger escalation according to predefined business rules.
2. A suspected security incident must be escalated even if the request category is not `account_access`.
3. A payment issue must not automatically be classified as critical solely because money was charged but an order is missing.
4. The LLM may propose a priority, but Python business rules must validate the final routing decision.
5. Low classification confidence must trigger human review.
6. If the priority cannot be determined reliably, the request must not be treated as low priority by default.

These rules are initial assumptions for a fictional online store and may be refined during testing.

## 5. Classification Output

The classification result must contain:

- `category` — one of the supported categories.
- `priority` — one of the supported priority levels.
- `confidence` — a numeric score between 0 and 1.
- `reason` — a short explanation of the classification.
- `missing_information` — a list of information needed to investigate the request.
- `knowledge_article_ids` — IDs of relevant articles actually retrieved from the knowledge base.
- `draft_reply` — a proposed response to the customer.
- `requires_human_review` — whether the request requires human review.

The application must validate the output before using it.

An invalid output must not be stored as a successful classification.

## 6. Knowledge Base

- The initial knowledge base will contain fictional customer-support articles.
- Articles must have an ID, title, content, category, and update timestamp.
- The system must retrieve relevant articles before generating a draft reply.
- The draft must not introduce unsupported policies, refund guarantees, delivery dates, or other factual claims.
- The system must not invent knowledge-base article IDs.
- If no relevant information is found, the system must indicate that the available information is insufficient and route the request for review when necessary.

The initial implementation may use keyword-based retrieval. More advanced retrieval methods can be considered later.

## 7. Human Review

A request must be flagged for human review when:

- Its priority is `critical`.
- Classification confidence is below the configured threshold.
- The classification output is invalid or incomplete.
- A suspected security incident is detected.
- The knowledge base does not contain sufficient information for a reliable response.
- An unexpected processing error prevents safe completion.

AI-generated replies must remain drafts until explicitly approved by a human operator.

## 8. Data Storage

PostgreSQL must store:

- The original incoming request.
- Telegram identifiers required to identify the message and sender.
- The assigned category and priority.
- The classification confidence and reason.
- Retrieved knowledge-base article references.
- The generated draft reply.
- The current processing and review status.
- Processing timestamps and relevant error information.

The system must maintain a processing history sufficient to investigate failures and understand how a result was produced.

Telegram events must be handled idempotently so that processing the same event again does not create duplicate tickets.

## 9. Error Handling

The system must handle the following situations:

- Invalid or empty incoming messages.
- LLM API timeouts or unavailable services.
- Invalid JSON or schema violations in model output.
- Database connection failures.
- Missing or irrelevant knowledge-base articles.
- Duplicate Telegram events.
- Unexpected errors in the n8n workflow.

Errors must be logged without exposing API keys, bot tokens, or unnecessary personal data.

When safe processing is not possible, the system must record the failure when possible and avoid presenting an unverified result as successful.

## 10. Testing and Evaluation

The project must include a labeled dataset of sample support requests with expected categories and priorities.

The initial target is at least 50 test requests.

Evaluation must include:

- Overall classification accuracy.
- Precision and recall by category.
- Recall for critical requests.
- The number and percentage of requests routed for human review.
- Correctness of knowledge-base article references.
- Validation of malformed LLM outputs.
- Idempotency checks for duplicate events.
- Tests for database and LLM failures.

Evaluation results must be documented after the implementation is tested. No performance results should be claimed before they are measured.

## 11. Security and Privacy

- API keys and bot tokens must be stored outside source code.
- Secret files must be excluded from version control.
- Incoming user messages must be treated as untrusted input.
- Instructions embedded in customer messages must not override the application's system instructions or business rules.
- The initial version must use fictional test data.
- AI-generated responses must not be sent automatically to customers.

## 12. Definition of Done

The MVP is considered complete when:

- A Telegram message can be processed through the full workflow.
- The request and processing result are stored in PostgreSQL.
- The category and priority conform to the defined rules.
- Relevant knowledge-base references are validated.
- A draft reply is generated or the request is safely flagged for review.
- Duplicate events do not create duplicate tickets.
- Errors are handled without silently treating failed processing as successful.
- Automated tests run successfully.
- Setup instructions and measured evaluation results are documented in the README.

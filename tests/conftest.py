import os


# Isolated test environment
os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://test_user:test_password"
    "@127.0.0.1:1/test_db"
)

os.environ["TELEGRAM_BOT_TOKEN"] = "test_bot_token"
os.environ["TELEGRAM_WEBHOOK_SECRET"] = "test_webhook_secret"

os.environ["OPERATOR_API_KEY"] = "test_operator_api_key"
os.environ["OPERATOR_ID"] = "1"
os.environ["OPERATOR_TELEGRAM_ID"] = "123456789"

os.environ["LLM_BASE_URL"] = "http://127.0.0.1:1/v1"
os.environ["LLM_CLASSIFIER_MODEL"] = "qwen3-4b"
os.environ["LLM_REPLY_MODEL"] = "qwen3-4b"

os.environ["LLM_CLASSIFIER_TEMPERATURE"] = "0"
os.environ["LLM_CLASSIFIER_MAX_TOKENS"] = "150"

os.environ["LLM_REPLY_TEMPERATURE"] = "0.1"
os.environ["LLM_REPLY_MAX_TOKENS"] = "300"
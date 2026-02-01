"""
Constants for Output Monitoring Engines.

All configuration constants are defined here for easy modification.
Update these values when pricing changes or to tune retry behavior.
"""

# =============================================================================
# RETRY CONFIGURATION
# =============================================================================
# These settings control how the engines handle rate limits and transient errors

MAX_RETRIES = 3                  # Number of retry attempts before failing
RETRY_DELAY = 2.0                # Initial delay in seconds before retry
RETRY_MULTIPLIER = 2.0           # Exponential backoff multiplier


# =============================================================================
# MODEL DEFAULTS
# =============================================================================
# Default parameters for API calls

DEFAULT_MAX_TOKENS = 1000        # Maximum tokens in response
DEFAULT_TEMPERATURE = 0.7        # Response randomness (0.0 = deterministic)


# =============================================================================
# OPENAI PRICING (GPT-4o-mini - cheapest capable model)
# =============================================================================
# Update these values when OpenAI changes pricing

OPENAI_INPUT_COST_PER_1M = 0.15      # $0.15 per 1M input tokens
OPENAI_OUTPUT_COST_PER_1M = 0.60     # $0.60 per 1M output tokens


# =============================================================================
# ANTHROPIC PRICING (Claude 3.5 Haiku - cheapest capable model)
# =============================================================================
# Update these values when Anthropic changes pricing

ANTHROPIC_INPUT_COST_PER_1M = 0.80   # $0.80 per 1M input tokens
ANTHROPIC_OUTPUT_COST_PER_1M = 4.00  # $4.00 per 1M output tokens


# =============================================================================
# GEMINI PRICING (Gemini 2.0 Flash-Lite - cheapest model)
# =============================================================================
# Update these values when Google changes pricing

GEMINI_INPUT_COST_PER_1M = 0.075    # $0.075 per 1M input tokens
GEMINI_OUTPUT_COST_PER_1M = 0.30    # $0.30 per 1M output tokens


# =============================================================================
# SEARCHGPT PRICING (OpenAI GPT-4o with search - gpt-4o-search-preview)
# =============================================================================
# SearchGPT uses GPT-4o pricing plus search costs
# https://openai.com/api/pricing/

SEARCHGPT_INPUT_COST_PER_1M = 2.50   # $2.50 per 1M input tokens
SEARCHGPT_OUTPUT_COST_PER_1M = 10.00 # $10.00 per 1M output tokens


# =============================================================================
# BING COPILOT PRICING (via Azure OpenAI with Bing grounding)
# =============================================================================
# Uses Azure OpenAI GPT-4o pricing
# https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/

BING_COPILOT_INPUT_COST_PER_1M = 2.50    # $2.50 per 1M input tokens
BING_COPILOT_OUTPUT_COST_PER_1M = 10.00  # $10.00 per 1M output tokens

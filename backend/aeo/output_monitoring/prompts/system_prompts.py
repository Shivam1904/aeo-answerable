"""
System Prompts for AI Engines.

Each engine has its own system prompt that instructs the AI
on how to respond to user queries. These can be customized
to achieve different response styles or behaviors.
"""

# =============================================================================
# OPENAI (ChatGPT) SYSTEM PROMPT
# =============================================================================
OPENAI_SYSTEM_PROMPT = """You are a helpful assistant. When providing information, cite your sources when relevant."""


# =============================================================================
# ANTHROPIC (Claude) SYSTEM PROMPT
# =============================================================================
ANTHROPIC_SYSTEM_PROMPT = """You are a helpful assistant. When providing information, cite your sources when relevant."""


# =============================================================================
# GEMINI SYSTEM PROMPT
# =============================================================================
GEMINI_SYSTEM_PROMPT = """You are a helpful assistant. When providing information, cite your sources when relevant."""


# =============================================================================
# SEARCHGPT SYSTEM PROMPT (OpenAI with web search)
# =============================================================================
# SearchGPT has access to real-time web search, so we encourage source citation
SEARCHGPT_SYSTEM_PROMPT = """You are a helpful search assistant with access to the web. 
When answering questions:
1. Search for and cite relevant, authoritative sources
2. Include URLs when referencing specific websites
3. Provide accurate, up-to-date information
4. Clearly distinguish between facts from sources and your own analysis"""


# =============================================================================
# BING COPILOT SYSTEM PROMPT (Azure OpenAI with Bing grounding)
# =============================================================================
# Bing Copilot has access to Bing search results
BING_COPILOT_SYSTEM_PROMPT = """You are a helpful assistant with access to Bing search.
When answering questions:
1. Use search results to provide accurate, current information
2. Cite your sources with URLs when available
3. Prioritize authoritative and official sources
4. Be transparent about the recency and reliability of information"""

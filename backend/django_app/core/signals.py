from django.dispatch import Signal, receiver
from .models import LLMInteraction
import logging

logger = logging.getLogger(__name__)

# Define the signal
# Arguments: sender, interaction_data (dict)
llm_request_executed = Signal()

@receiver(llm_request_executed)
def log_llm_interaction(sender, interaction_data, **kwargs):
    """
    Listener that saves LLM interaction details to the database.
    This runs synchronously by default in Django, so it saves immediately.
    """
    try:
        LLMInteraction.objects.create(
            target_url=interaction_data.get('target_url', ''),
            query_text=interaction_data.get('query_text', ''),
            engine=interaction_data.get('engine', 'unknown'),
            model_name=interaction_data.get('model_name'),
            prompt_text=interaction_data.get('prompt_text', ''),
            response_text=interaction_data.get('response_text', ''),
            tokens_input=interaction_data.get('tokens_input', 0),
            tokens_output=interaction_data.get('tokens_output', 0),
            cost_usd=interaction_data.get('cost_usd', 0.0),
            latency_ms=interaction_data.get('latency_ms', 0),
            success=interaction_data.get('success', True),
            error_message=interaction_data.get('error_message'),
            metadata=interaction_data.get('metadata', {})
        )
        logger.info(f"Logged LLM interaction for {interaction_data.get('engine')}")
        
    except Exception as e:
        logger.error(f"Failed to log LLM interaction: {e}")

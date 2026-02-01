import asyncio
from aeo.output_monitoring.base import QueryEngine, QueryResult

class MockEngine(QueryEngine):
    """
    Simulates an LLM engine for testing/demo purposes when no API keys are present.
    """
    def __init__(self, name="mock-gpt"):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    async def query(self, prompt: str, context_url: str) -> QueryResult:
        # Simulate network latency
        await asyncio.sleep(1.5)
        
        return QueryResult(
            engine=self.name,
            response=f"This is a mocked response from {self.name}. The user asked: '{prompt}'. I found context at {context_url}.",
            citations=[],
            tokens_used=100,
            cost_usd=0.001,
            latency_ms=1500
        )

    def estimate_cost(self, prompt: str) -> float:
        return 0.001

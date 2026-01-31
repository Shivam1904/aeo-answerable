from typing import List
from bs4 import BeautifulSoup

class ContentChunker:
    def chunk_semantic(self, soup: BeautifulSoup) -> List[str]:
        """Splits by Header sections."""
        chunks = []
        current_chunk = []
        
        # Simple strategy: Every H1-H6 starts a new chunk.
        # Everything else is appended to current chunk.
        
        for element in soup.body.descendants if soup.body else []:
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                current_chunk.append(element.get_text(strip=True))
            elif element.name in ['p', 'li', 'pre', 'code', 'table']:
                 text = element.get_text(strip=True)
                 if text:
                     current_chunk.append(text)
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return [c for c in chunks if len(c) > 50] # Filter tiny chunks

    def chunk_sliding(self, text: str, window_size: int = 1000) -> List[str]:
        """Fixed character/word count windows."""
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + window_size
            # Try to find a space near the end to avoid splitting words
            if end < text_len:
                while end > start and text[end] != ' ':
                    end -= 1
                if end == start: # No space found, forced split
                    end = start + window_size
            
            chunks.append(text[start:end].strip())
            start = end
            
        return [c for c in chunks if len(c) > 50]

    def compare_strategies(self, semantic_chunks: List[str], sliding_chunks: List[str]) -> float:
        """Returns a consistency score (Delta)."""
        # Simple heuristic: Ratio of chunk counts.
        # If semantic structure is good, it might produce more coherent chunks than blind sliding.
        # This is strictly a heuristic for the report.
        if not sliding_chunks:
            return 0.0
        
        ratio = len(semantic_chunks) / len(sliding_chunks)
        # We define "consistency" as being within a reasonable range (0.5 to 1.5)
        # If semantic methods produce 10x more chunks (tiny headers) or 0.1x (giant walls of text), that's a signal.
        
        deviation = abs(1.0 - ratio)
        score = max(0.0, 1.0 - deviation)
        return round(score, 2)

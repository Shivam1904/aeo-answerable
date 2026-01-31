from typing import List, Dict, Optional
try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None

class LocalRetriever:
    def __init__(self):
        self.bm25 = None
        self.corpus: List[str] = []

    def build_index(self, chunks: List[str]):
        """Builds BM25 index."""
        if not BM25Okapi:
            return
        
        self.corpus = chunks
        # Simple whitespace tokenization for speed. 
        # For production, we'd use NLTK or SpaCy.
        tokenized_corpus = [doc.lower().split(" ") for doc in chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def query(self, q: str, top_k: int = 5) -> List[str]:
        """Returns top K chunks."""
        if not self.bm25:
            return []
        
        tokenized_query = q.lower().split(" ")
        return self.bm25.get_top_n(tokenized_query, self.corpus, n=top_k)

    def simulate_recall(self, pages_data: List[Dict]) -> Dict:
        """
        Generates queries from headings and measures recall.
        
        Strategy:
        1. Extract H2/H3 text from page data.
        2. Treat that header as a "User Query".
        3. Check if the chunk containing that header is retrieved in Top-5.
        
        Returns:
            Dict with 'recall_at_1', 'recall_at_5', 'query_count'
        """
        if not self.bm25:
            return {"error": "BM25 not initialized"}

        hits_at_1 = 0
        hits_at_5 = 0
        query_count = 0
        
        for page in pages_data:
            chunks = page.get('chunks', {}).get('semantic', [])
            headings = page.get('headings', [])
            
            if not chunks: 
                continue

            # We need to map headings to the chunks they are in.
            # Since our chunker is semantic (Heading + Content), the heading text 
            # SHOULD be at the start of one of the chunks.
            
            for h in headings:
                if h['level'] not in [2, 3]: # Only test H2/H3
                    continue
                
                query_text = h['text']
                if len(query_text) < 10: # Skip tiny headings
                    continue

                query_count += 1
                
                # Find ground truth chunk (the one starting with this heading)
                # This is a heuristic matching.
                ground_truth_chunk = None
                for c in chunks:
                    if c.startswith(query_text):
                        ground_truth_chunk = c
                        break
                
                if not ground_truth_chunk:
                    continue

                # Run Retrieval
                retrieved = self.query(query_text, top_k=5)
                
                if retrieved and retrieved[0] == ground_truth_chunk:
                    hits_at_1 += 1
                
                if ground_truth_chunk in retrieved:
                    hits_at_5 += 1

        if query_count == 0:
            return {"recall_at_1": 0.0, "recall_at_5": 0.0, "query_count": 0}

        return {
            "recall_at_1": round(hits_at_1 / query_count, 2),
            "recall_at_5": round(hits_at_5 / query_count, 2),
            "query_count": query_count
        }

from typing import Dict, List
from bs4 import BeautifulSoup



class ContentAuditor:
    def audit_structure(self, soup: BeautifulSoup) -> Dict:
        """Checks for H1 existence and hierarchy."""
        h1s = soup.find_all('h1')
        h1_count = len(h1s)
        h1_found = h1_count > 0
        
        # Check hierarchy
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        skipped_levels = []
        last_level = 0
        
        for h in headers:
            current_level = int(h.name[1])
            # If we go deeper than +1 level (e.g. 2 -> 4), it's a skip.
            # 2 -> 3 is fine. 2 -> 2 is fine. 4 -> 2 is fine.
            if current_level > last_level + 1 and last_level > 0:
                skipped_levels.append(f"Jumped from H{last_level} to H{current_level} at '{h.get_text(strip=True)[:30]}...'")
            last_level = current_level

        structure_score = 1.0
        if not h1_found:
            structure_score -= 0.5
        if skipped_levels:
            structure_score -= 0.1 * len(skipped_levels)
        
        structure_score = max(0.0, structure_score)

        return {
            "h1_found": h1_found,
            "h1_count": h1_count,
            "skipped_levels": skipped_levels,
            "score": round(structure_score, 2)
        }

    def audit_clarity(self, text: str) -> Dict:
        """Basic pronoun density check."""
        pronouns = ['it', 'this', 'that', 'they', 'them', 'he', 'she', 'these', 'those']
        words = text.lower().split()
        if not words:
            return {"pronoun_density": 0.0, "score": 1.0}
            
        pronoun_count = sum(1 for w in words if w in pronouns)
        density = pronoun_count / len(words)
        
        # Arbitrary thresholds: > 5% pronouns is suspicious for technical docs
        score = 1.0
        if density > 0.05:
            score = max(0.0, 1.0 - (density - 0.05) * 10)
            
        return {
            "pronoun_density": round(density, 4),
            "pronoun_count": pronoun_count,
            "word_count": len(words),
            "score": round(score, 2),
            "flags": ["High pronoun density"] if score < 0.8 else []
        }

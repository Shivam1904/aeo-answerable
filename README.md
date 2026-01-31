# AEO-Answerable

> **"Lighthouse for Answer Engines"** — An open-source tool that audits websites for Answer Engine Optimization (AEO)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![Node.js](https://img.shields.io/badge/Node.js-20+-green.svg)](https://nodejs.org/)

---

## 🎯 What is AEO-Answerable?

AEO-Answerable analyzes your website and tells you **how well AI answer engines can understand and cite your content**. 

Instead of measuring web performance, it measures **answerability** — how easily an LLM-powered search engine can:

1. **Find** your content through retrieval
2. **Understand** it in context
3. **Quote** it accurately without hallucination

## 🚀 Key Features

### 📊 Answerability Score (0-100)
Get a single, actionable score that tells you how "answer-engine-ready" your site is.

### ✅ Deterministic Audits (No LLM Required)
- **Structure Audit**: Heading hierarchy, H1 presence, logical flow
- **Context Clarity Audit**: Pronoun density, dangling references
- **Specificity Audit**: Citable facts vs. vague marketing copy
- **Extractability Audit**: Content accessibility for crawlers

### 🔎 Retrieval Stress Tests
Simulates RAG (Retrieval-Augmented Generation) to check if the right content surfaces for obvious queries.

### 🤖 LLM Mode (BYOK - Bring Your Own Key)
- Synthetic question generation
- Answer faithfulness verification
- Hallucination detection

### 📝 Actionable Reports
- JSON output for CI/CD integration
- HTML reports with "Agent View"

---

## 📦 Installation

```bash
# Not yet available - coming soon!
npm install -g aeo-answerable
```

## 🛠️ Usage

```bash
# Basic scan
aeo scan https://example.com

# With options
aeo scan https://example.com --max-pages 200 --mode fast

# Full rendered mode (for JS-heavy sites)
aeo scan https://example.com --mode rendered

# Generate HTML report
aeo report output.json --html
```

## ⚙️ Configuration

Create an `aeo.config.json` in your project root:

```json
{
  "maxPages": 200,
  "mode": "fast",
  "respectRobots": true,
  "concurrency": 5,
  "timeout": 15000,
  "include": ["/docs/**", "/blog/**"],
  "exclude": ["/admin/**", "/api/**"],
  "llm": {
    "provider": "openai",
    "model": "gpt-4o-mini"
  }
}
```

---

## 📊 Understanding the Score

| Component | Weight | What It Measures |
|-----------|--------|------------------|
| Extractability | 20% | Can content be cleanly extracted? |
| Structure | 15% | Proper heading hierarchy and flow |
| Context Clarity | 15% | Low pronoun density, explicit references |
| Specificity | 10% | Facts, numbers, named entities present |
| Retrieval Robustness | 25% | Can correct chunks be retrieved? |
| Faithfulness | 15% | Can LLM answer without hallucinating? |

> **Note**: If LLM mode is disabled, faithfulness weight is redistributed to other categories.

---

## 🏗️ Project Structure

The project logic resides in the `backend/` directory.

### 🔙 Backend (`/backend`)
The core logic and execution engine (Python).
-   **CLI**: Command-line interface for running scans.
-   **Crawler**: Fetches pages and handles `robots.txt`.
-   **Extractor**: Cleans HTML into "Agent-Readable" text.
-   **Scoring Engine**: Runs audits and calculates the answerability score.
-   **Retrieval**: stress-tests content findability (RAG simulation).

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Backend (Python)
# 1. Create venv in root (if not exists)
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
cd backend
pip install -r requirements.txt

# 3. Run a scan
python -m aeo.cli scan https://example.com
```

---

## 📚 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Crawler Specification](docs/CRAWLER.md)
- [Extractor Specification](docs/EXTRACTOR.md)
- [Chunking Strategy](docs/CHUNKING.md)
- [Audit Specifications](docs/AUDITS.md)
- [Retrieval System](docs/RETRIEVAL.md)
- [Scoring Methodology](docs/SCORING.md)
- [Report Generation](docs/REPORT.md)
- [CLI Reference](docs/CLI.md)
- [Development Roadmap](docs/ROADMAP.md)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Inspired by the need to optimize content for the AI-first search era. Special thanks to the web performance community and tools like Lighthouse that paved the way.

---

<p align="center">
  <strong>Built for the age of AI-powered search 🚀</strong>
</p>

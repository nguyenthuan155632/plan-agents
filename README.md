# 🤖 Dual AI Collaboration Framework

> Watch two AI agents brainstorm, debate, and collaborate in real-time with human moderation.

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
cd web && npm install && cd ..

# 2. Configure API keys (IMPORTANT!)
cp env.example .env
# Edit .env and add your actual API keys

# 3. Start the application
chmod +x start.sh
./start.sh

# 4. Open browser
# http://localhost:3000
```

> **⚠️ Security Note**: Never commit your `.env` file! It's already in `.gitignore`.  
> See [ENV_SETUP.md](ENV_SETUP.md) for detailed configuration guide.

## ✨ Features

- 🤖 **Dual Agent System**: GLM-4.5-air + Gemini-2.5-flash collaborate
- 💬 **Real-time Debates**: Watch agents discuss and brainstorm
- 🧠 **Smart Turn-Taking**: Asynchronous, file-based signal system
- 👤 **Human Control**: Interrupt, guide, or stop conversations anytime
- 🎨 **Neobrutalism UI**: Bold, high-contrast, modern design
- 🌐 **Bilingual**: Auto-detects and responds in Vietnamese or English

## 📸 Screenshots

### Neobrutalism Design
- **Bold borders** (2-3px black)
- **Hard shadows** (offset, no blur)
- **Bright colors** (yellow, pink, blue, purple)
- **Heavy typography** (uppercase, font-black)

### Agent Personalities
- **Agent A (GLM)**: Solution-focused executor, respects human requests
- **Agent B (Gemini)**: Critical thinker, provides alternative perspectives

## 🏗️ Architecture

```
Web UI (Next.js) ←→ REST API ←→ Python Backend ←→ AI Models
                                      ↕
                              SQLite Database
                                      ↕
                                Signal Files
```

## 📚 Full Documentation

For complete documentation, see **[DOCUMENTATION.md](DOCUMENTATION.md)**:

- 📖 **System Architecture** - High-level design and components
- 🛠️ **Tech Stack** - Technologies used
- 🎨 **UI/UX Design** - Neobrutalism design system
- 🚀 **Getting Started** - Detailed installation guide
- 📘 **Usage Guide** - How to use the framework
- ⚙️ **Agent Configuration** - Agent personalities and prompts
- 🔌 **API Reference** - REST endpoints
- 🧠 **Knowledge Base** - Key concepts and best practices
- 💻 **Development Guide** - For contributors

## 🔑 Prerequisites

- Python 3.13+
- Node.js 18+
- API Keys:
  - [z.ai API key](https://z.ai) for GLM-4.5-air
  - [Google AI API key](https://ai.google.dev/) for Gemini-2.5-flash

## 🎯 Use Cases

- **Software Architecture Debates**: Compare monolithic vs microservices
- **Code Reviews**: Agents analyze and discuss code quality
- **Design Decisions**: Database schema, API design, etc.
- **Technology Comparisons**: React vs Vue, SQL vs NoSQL
- **Problem Solving**: Brainstorm solutions with AI assistance

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Backend | Python 3.13, SQLite3, Typer |
| AI Models | GLM-4.5-air (z.ai), Gemini-2.5-flash (Google) |
| Design | Neobrutalism (bold colors, hard shadows, heavy typography) |

## 📝 Example Usage

1. **Start a new conversation**: "Best practices for microservices architecture"
2. **Agent A responds**: Provides initial solution/perspective
3. **Agent B responds**: Offers alternative view, points out trade-offs
4. **You interrupt**: "I prefer Agent A's approach but with B's concern about scaling"
5. **Agents discuss**: Refine solution based on your feedback
6. **You stop**: Agents provide comprehensive summary with final recommendations

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [z.ai](https://z.ai) for GLM API access
- [Google AI](https://ai.google.dev/) for Gemini API
- Neobrutalism design inspiration from the design community

## 📧 Support

For questions or issues:
- Open an [issue on GitHub](https://github.com/your-repo/issues)
- Check [DOCUMENTATION.md](DOCUMENTATION.md) for detailed guides

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: October 25, 2025


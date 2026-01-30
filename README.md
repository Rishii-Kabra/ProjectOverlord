# Project Overlord: Autonomous Agentic Framework

Project Overlord is a high-efficiency autonomous system architected to solve complex engineering tasks through multi-agent orchestration. Built with Python and the Gemini 2.5 Flash API, it moves beyond simple chatbots by implementing a self-correcting execution loop with persistent memory and a dedicated security layer.

## 🚀 Key Features

- **Autonomous Orchestration:** Uses a "Think-Act-Observe" loop to decompose user requests into executable tool calls.
- **Multi-Agent Security:** Features a dedicated `CodeValidator` agent that audits AI-generated code for malicious patterns (e.g., file deletion, unauthorized system access) before execution.
- **Persistent State Management:** Integrated SQLite database to maintain long-term memory across sessions, allowing the agent to remember user preferences and past results.
- **Tool-Chaining:** Seamlessly integrates:
  - **ShellTool:** Python execution and package management.
  - **WebBrowser:** Real-time information retrieval via Serper API.
  - **FileManager:** Secure file I/O within a sandboxed workspace.
- **Context Optimization:** Implements sliding-window memory and token-pruning to maximize efficiency and minimize API costs.

## 🛠️ Tech Stack

- **Language:** Python 3.12+
- **AI Model:** Gemini 2.5 Flash (Google GenAI SDK)
- **Database:** SQLite3
- **Tools:** Serper.dev API, Pydantic (Data Validation), Rich (Terminal UI)

## 📁 Project Structure

```text
ProjectOverlord/
├── core/
│   ├── orchestrator.py  # The "Brain" (LLM Logic)
│   ├── memory.py        # SQLite Persistent Memory
│   └── validator.py     # Security Audit Agent
├── tools/
│   ├── file_manager.py  # File I/O Logic
│   ├── shell.py         # Code Execution Environment
│   └── browser.py       # Web Search Integration
├── workspace/           # Sandboxed directory for AI output
├── main.py              # The Autonomous Loop (UI)
└── .env                 # API Keys and Configuration
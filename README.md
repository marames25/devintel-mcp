# DevIntel — AI-Powered Repository Intelligence

An AI-powered software engineering assistant that analyzes local software repositories using **Groq, MCP, Python, and Gradio**.

DevIntel allows developers to ask questions about a local repository and automatically selects the appropriate MCP tool to retrieve the required information.

## Features

- Analyze local software repositories
- Explore project structure
- Identify technologies and dependencies
- Search repository files and code
- Read specific repository files
- Inspect available tests
- Check Git status
- Inspect Git history
- Inspect Git changes
- Ask questions using a conversational AI interface
- Automatic MCP tool selection

## Architecture

```text
                    User
                      │
                      ▼
                ┌───────────┐
                │  Gradio   │
                │    UI     │
                └─────┬─────┘
                      │
                      ▼
                ┌───────────┐
                │   Groq    │
                │    LLM    │
                └─────┬─────┘
                      │
              Tool Selection
                      │
                      ▼
                ┌───────────┐
                │ MCP Client│
                └─────┬─────┘
                      │
                      ▼
                ┌───────────┐
                │ MCP Server│
                └─────┬─────┘
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
    MCP Repository Tools    Local Repository
```

### How It Works

1. The user provides the local repository path.
2. The user asks a question about the repository.
3. Groq processes the request and determines which MCP tool is required.
4. The MCP client sends the tool request to the MCP server.
5. The MCP server performs the operation on the local repository.
6. The result is returned to the LLM.
7. The LLM generates a concise answer.
8. The answer is displayed in the Gradio interface.

## 🔧 MCP Tools

DevIntel currently provides 9 MCP tools:

| Tool                    | Purpose                                      |
| ----------------------- | -------------------------------------------- |
| `analyze_repo`          | General repository analysis                  |
| `project_info`          | Project type, technologies, and dependencies |
| `project_structure`     | Repository file and folder structure         |
| `search_repository`     | Search for files or code                     |
| `read_repository_file`  | Read a specific file                         |
| `repository_tests`      | Inspect available tests                      |
| `repository_git_status` | Show Git working-tree status                 |
| `repository_git_log`    | Inspect Git history                          |
| `repository_git_diff`   | Inspect Git changes                          |

## 🛠️ Tech Stack

- **Python**
- **Groq API**
- **GPT-OSS**
- **Model Context Protocol (MCP)**
- **Gradio**
- **AsyncIO**
- **python-dotenv**

## Project Structure

```text
devintel-mcp/
│
├── server.py
├── agent.py
├── ui.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### `server.py`

Contains the MCP server and repository-analysis tools.

### `agent.py`

Contains the command-line DevIntel agent and MCP client logic.

### `ui.py`

Provides the Gradio web interface and connects the user to the AI agent.

## Installation

Clone the repository:

```bash
git clone <YOUR_REPOSITORY_URL>
cd devintel-mcp
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

Never commit your `.env` file.

Make sure `.gitignore` contains:

```text
.env
.venv/
__pycache__/
```

## Running DevIntel

### Command Line

```bash
python agent.py
```

### Gradio UI

```bash
python ui.py
```

Then open the local Gradio URL shown in the terminal.

## Example Queries

After entering a repository path, you can ask:

```text
What technologies does this project use?
```

```text
Show me the project structure.
```

```text
What tests are implemented?
```

```text
Show me the current Git status.
```

```text
Read README.md.
```

```text
Where is the login functionality implemented?
```

```text
Give me a technical overview of this project.
```

## Example Agent Flow

For:

```text
Show me the project structure.
```

DevIntel may perform:

```text
User
  ↓
Groq
  ↓
project_structure
  ↓
MCP Server
  ↓
Local Repository
  ↓
Tool Result
  ↓
Groq
  ↓
Answer
```

The important part is that **the LLM does not directly access the repository**. It requests information through the available MCP tools, while the MCP server performs the repository operations.

## Purpose

DevIntel demonstrates how **LLMs can be connected to developer tools through MCP** to create an intelligent software engineering assistant.

Instead of manually navigating a repository, developers can interact with their codebase using natural language.

## Future Improvements

- Repository indexing and caching
- Code quality analysis
- Dependency vulnerability detection
- Pull request analysis
- Automatic test suggestions
- Code documentation generation
- Support for remote Git repositories
- More advanced software architecture analysis

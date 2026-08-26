import asyncio
import json
import os

import gradio as gr
from dotenv import load_dotenv
from groq import Groq

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


load_dotenv()

MODEL = "openai/gpt-oss-20b"

MAX_TOOL_RESULT_CHARS = 1500
MAX_HISTORY_MESSAGES = 2
MAX_AGENT_ITERATIONS = 4


groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


SYSTEM_PROMPT = """
You are DevIntel, an AI software engineering assistant.

You analyze local software repositories using MCP tools.

Rules:
- Use a tool when repository information is required.
- Use the exact tool names provided.
- Never invent repository information.
- Always use the repository path provided by the user.
- After getting the required information, answer concisely.

Tool selection:
project_info = technologies, frameworks, dependencies
project_structure = folders and files
search_repository = search code or files
read_repository_file = read a specific file
repository_tests = tests
repository_git_status = Git status
repository_git_log = Git history
repository_git_diff = Git changes
analyze_repo = general analysis
"""


TOOL_DESCRIPTIONS = {
    "analyze_repo": "Analyze a local repository and provide a technical overview.",
    "project_info": "Get project type, technologies, frameworks, dependencies, and metadata.",
    "project_structure": "Get the repository folder and file structure.",
    "search_repository": "Search repository files for a keyword, class, function, or code pattern.",
    "read_repository_file": "Read the contents of a specific repository file.",
    "repository_git_status": "Get the current Git status of the repository.",
    "repository_git_log": "Get Git commit history.",
    "repository_git_diff": "Get current Git changes and diff.",
    "repository_tests": "Detect and inspect repository tests.",
}


mcp_context = {
    "session": None,
    "stdio": None,
    "groq_tools": [],
}


def select_tools(user_message):
    text = user_message.lower()

    selected = []

    if any(word in text for word in [
        "technology",
        "technologies",
        "framework",
        "dependency",
        "dependencies",
        "library",
        "libraries",
        "tech stack",
        "language",
        "languages"
    ]):
        selected.append("project_info")

    if any(word in text for word in [
        "structure",
        "folder",
        "folders",
        "files",
        "directory",
        "directories",
        "tree"
    ]):
        selected.append("project_structure")

    if any(word in text for word in [
        "search",
        "find",
        "where",
        "class",
        "function",
        "method",
        "code"
    ]):
        selected.append("search_repository")

    if any(word in text for word in [
        "read",
        "show me",
        "contents",
        "content",
        "file"
    ]):
        selected.append("read_repository_file")

    if any(word in text for word in [
        "test",
        "tests",
        "testing",
        "test cases",
        "test suite"
    ]):
        selected.append("repository_tests")

    if any(word in text for word in [
        "git status",
        "status",
        "modified",
        "changes"
    ]):
        selected.append("repository_git_status")

    if any(word in text for word in [
        "git log",
        "commit",
        "commits",
        "history"
    ]):
        selected.append("repository_git_log")

    if any(word in text for word in [
        "diff",
        "git diff",
        "difference"
    ]):
        selected.append("repository_git_diff")

    if any(word in text for word in [
        "analyze",
        "analysis",
        "overview",
        "architecture",
        "understand",
        "explain project"
    ]):
        selected.append("analyze_repo")

    if not selected:
        selected = [
            "project_info",
            "project_structure",
            "analyze_repo"
        ]

    return list(dict.fromkeys(selected))


async def connect_mcp():

    if mcp_context["session"] is not None:
        return

    print("Connecting to DevIntel MCP Server...")

    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
    )

    stdio = stdio_client(server_params)

    read, write = await stdio.__aenter__()

    session = ClientSession(
        read,
        write
    )

    await session.__aenter__()

    await session.initialize()

    tools_result = await session.list_tools()

    mcp_context["session"] = session
    mcp_context["stdio"] = stdio

    groq_tools = []

    for tool in tools_result.tools:
        groq_tools.append({
            "type": "function",
            "function": {
                "name": str(tool.name),
                "description": str(tool.description or "MCP repository tool"),
                "parameters": tool.input_schema or {
                    "type": "object",
                    "properties": {}
                }
            }
        })

    mcp_context["groq_tools"] = groq_tools

    print("Tools sent to Groq:")
    for tool in groq_tools:
        print("-", tool["function"]["name"])

    print("Connected to DevIntel MCP Server.")
    print(f"Loaded {len(groq_tools)} tools.")


def get_selected_groq_tools(user_message):

    selected_names = select_tools(user_message)

    return [
        tool
        for tool in mcp_context["groq_tools"]
        if tool["function"]["name"] in selected_names
    ]


def build_history(history):

    if not history:
        return []

    messages = []

    for item in history[-MAX_HISTORY_MESSAGES:]:

        if not isinstance(item, dict):
            continue

        role = item.get("role")
        content = item.get("content")

        if role not in {"user", "assistant"}:
            continue

        if not content:
            continue

        content = str(content)

        if len(content) > 800:
            content = content[:800] + "\n[TRUNCATED]"

        messages.append({
            "role": role,
            "content": content
        })

    return messages


async def call_mcp_tool(
    session,
    tool_name,
    arguments
):

    try:

        result = await session.call_tool(
            tool_name,
            arguments
        )

        result_text = ""

        for content in result.content:

            if hasattr(content, "text"):
                result_text += content.text
            else:
                result_text += str(content)

        if len(result_text) > MAX_TOOL_RESULT_CHARS:

            result_text = (
                result_text[:MAX_TOOL_RESULT_CHARS]
                + "\n[RESULT TRUNCATED]"
            )

        return result_text

    except Exception as e:

        return f"Tool execution failed: {str(e)}"


async def ask_devintel(
    user_message,
    repo_path,
    history,
    activity_callback=None
):

    await connect_mcp()

    session = mcp_context["session"]

    groq_tools = get_selected_groq_tools(
        user_message
    )

    selected_names = [
        tool["function"]["name"]
        for tool in groq_tools
    ]

    tool_activity = []

    if activity_callback:

        await activity_callback(
            "🎯 Selected tools:\n"
            + "\n".join(
                f"• {name}"
                for name in selected_names
            )
        )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    messages.extend(
        build_history(history)
    )

    messages.append({
        "role": "user",
        "content": (
            f"Repository: {repo_path}\n"
            f"Request: {user_message}"
        )
    })

    for _ in range(MAX_AGENT_ITERATIONS):

        try:

            response = groq_client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=groq_tools,
                tool_choice="auto",
                temperature=0
            )

        except Exception as e:

            return (
                f"Groq error:\n\n{str(e)}",
                tool_activity
            )

        assistant_message = response.choices[0].message

        if not assistant_message.tool_calls:

            return (
                assistant_message.content
                or "No response was generated.",
                tool_activity
            )

        assistant_tool_calls = []

        for call in assistant_message.tool_calls:

            assistant_tool_calls.append({
                "id": call.id,
                "type": "function",
                "function": {
                    "name": call.function.name,
                    "arguments": call.function.arguments
                }
            })

        messages.append({
            "role": "assistant",
            "content": assistant_message.content or "",
            "tool_calls": assistant_tool_calls
        })

        for call in assistant_message.tool_calls:

            tool_name = call.function.name

            try:
                arguments = json.loads(
                    call.function.arguments
                )
            except Exception:
                arguments = {}

            tool_activity.append(
                f"🔄 Running: {tool_name}"
            )

            if activity_callback:

                await activity_callback(
                    "\n".join(tool_activity)
                )

            result_text = await call_mcp_tool(
                session,
                tool_name,
                arguments
            )

            tool_activity[-1] = (
                f"✅ {tool_name} completed"
            )

            if activity_callback:

                await activity_callback(
                    "\n".join(tool_activity)
                )

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result_text
            })

    return (
        "The analysis reached the maximum number "
        "of tool calls.",
        tool_activity
    )


async def chat(
    message,
    repo_path,
    history
):

    if not message or not message.strip():

        return (
            history,
            "",
            "⚠️ Please enter a message."
        )

    if not repo_path or not repo_path.strip():

        return (
            history,
            "",
            "⚠️ Please enter a repository path."
        )

    activity = [
        "🟢 DevIntel is starting..."
    ]

    async def update_activity(text):

        activity.clear()

        activity.extend(
            text.split("\n")
        )

    try:

        answer, tools = await ask_devintel(
            message,
            repo_path,
            history,
            activity_callback=update_activity
        )

        if tools:
            activity = tools

        else:
            activity.append(
                "ℹ️ No MCP tools were required."
            )

    except Exception as e:

        answer = (
            "❌ DevIntel encountered an error.\n\n"
            f"{str(e)}"
        )

        activity.append(
            "❌ Agent execution failed."
        )

    history = history + [
        {
            "role": "user",
            "content": message
        },
        {
            "role": "assistant",
            "content": answer
        }
    ]

    return (
        history,
        "",
        "\n".join(activity)
    )


def clear_chat():

    return [], "", "🟢 Ready"


with gr.Blocks(
    title="DevIntel",
    theme=gr.themes.Soft()
) as demo:

    gr.Markdown(
        """
# 🧠 DevIntel

### AI-Powered Repository Intelligence

Analyze, understand, and explore your local software projects
using **Groq + MCP + Python**.
"""
    )

    with gr.Row():

        repo_path = gr.Textbox(
            label="📂 Local Repository",
            placeholder=r"F:\Envnt\shaft-web-testng",
            info="Enter the local path of the repository you want to analyze.",
            scale=5
        )

        clear = gr.Button(
            "🗑 Clear",
            scale=1
        )

    gr.Markdown("### 💡 Try asking")

    with gr.Row():

        example_1 = gr.Button(
            "🔍 Analyze Repository"
        )

        example_2 = gr.Button(
            "📁 Show Structure"
        )

        example_3 = gr.Button(
            "🧪 Show Tests"
        )

        example_4 = gr.Button(
            "🔀 Git Status"
        )

    with gr.Row():

        with gr.Column(scale=3):

            gr.Markdown("## 💬 DevIntel")

            with gr.Row():

                message = gr.Textbox(
                    label="",
                    placeholder="Ask DevIntel about your repository...",
                    scale=5
                )

                send = gr.Button(
                    "➤ Send",
                    variant="primary",
                    scale=1
                )

            chatbot = gr.Chatbot(
                label="Conversation",
                height=500
            )

        with gr.Column(scale=1):

            gr.Markdown("## 🔧 MCP Activity")

            activity = gr.Textbox(
                label="Tool Execution",
                value="🟢 Ready",
                lines=18,
                interactive=False
            )

            gr.Markdown(
                """
**Architecture**

```text
User
 ↓
Gradio
 ↓
Groq
 ↓
MCP Client
 ↓
MCP Server
 ↓
Local Repository
DevIntel dynamically selects the
tools needed for each request.
"""
)
    send.click(
    fn=chat,
    inputs=[
        message,
        repo_path,
        chatbot
    ],
    outputs=[
        chatbot,
        message,
        activity
    ]
    )

    message.submit(
        fn=chat,
        inputs=[
            message,
            repo_path,
            chatbot
        ],
        outputs=[
            chatbot,
            message,
            activity
        ]
    )

    clear.click(
        fn=clear_chat,
        inputs=[],
        outputs=[
            chatbot,
            message,
            activity
        ]
    )

    example_1.click(
        fn=lambda: (
            "Analyze this repository and give me "
            "a concise technical overview."
        ),
        inputs=[],
        outputs=message
    )

    example_2.click(
        fn=lambda: "Show me the project structure.",
        inputs=[],
        outputs=message
    )

    example_3.click(
        fn=lambda: "What tests are available in this repository?",
        inputs=[],
        outputs=message
    )

    example_4.click(
        fn=lambda: "Show me the current Git status.",
        inputs=[],
        outputs=message
    )
    
if __name__ == "__main__":
    print()
    print("=" * 50)
    print("           DevIntel AI Assistant")
    print("=" * 50)
    print()

    demo.launch()
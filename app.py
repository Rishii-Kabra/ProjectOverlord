import sys
import os
import streamlit as st
import time

# Force Python to see the local 'core' and 'tools' folders
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.orchestrator import ProjectOrchestrator
from core.validator import CodeValidator
from tools.file_manager import FileManager
from tools.shell import ShellTool
from tools.browser import WebBrowser

# --- PAGE CONFIG ---
st.set_page_config(page_title="Project Overlord", page_icon="🤖", layout="wide")
st.title("🤖 Project Overlord: Autonomous Agent")
st.markdown("---")

# --- INITIALIZE CORE ---
@st.cache_resource
def init_system():
    return {
        "orchestrator": ProjectOrchestrator(),
        "files": FileManager(),
        "shell": ShellTool(),
        "browser": WebBrowser(),
        "validator": CodeValidator()
    }

sys = init_system()

# --- PRIVATE SESSION MEMORY ---
# This replaces TaskMemory for the web interface to ensure privacy
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("Session Control")
    if st.button("Clear Current Chat"):
        st.session_state.messages = []
        st.rerun()

    st.header("Workspace Files")
    files = [f for f in sys["files"].list_files()]
    st.write(files)

# --- DISPLAY CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- USER INPUT ---
if prompt := st.chat_input("What is your command, Architect?"):
    # 1. Save and display user prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- AGENT LOOP ---
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        thought_placeholder = st.expander("AI Thought Process", expanded=True)

        step = 0
        while step < 5:
            step += 1
            status_placeholder.info(f"Step {step}: Thinking...")

            try:
                # Use st.session_state.messages instead of sys["memory"]
                # We format it to match what the Gemini SDK expects
                history_for_api = []
                for m in st.session_state.messages:
                    role = "model" if m["role"] == "assistant" else "user"
                    history_for_api.append({"role": role, "parts": [{"text": m["content"]}]})

                action = sys["orchestrator"].get_next_action(history_for_api)

                if not action:
                    st.error("The AI failed to generate a plan.")
                    break

                thought_placeholder.write(f"**Step {step} Thought:** {action.thought}")

                # Handle Tools
                result = ""
                if action.tool == "SEARCH_WEB":
                    status_placeholder.info(f"Searching for: {action.content}...")
                    result = sys["browser"].search(action.content)
                elif action.tool == "WRITE_FILE":
                    status_placeholder.warning("Validating code...")
                    check = sys["validator"].validate_code(action.content)
                    if "UNSAFE" in check.upper():
                        result = f"Security Blocked: {check}"
                    else:
                        result = sys["files"].write_file(action.file_name, action.content)
                elif action.tool == "RUN_CODE":
                    status_placeholder.info(f"Running {action.file_name}...")
                    result = sys["shell"].execute_python(action.file_name)
                elif action.tool == "FINAL_ANSWER":
                    status_placeholder.empty()
                    st.success(action.content)
                    st.session_state.messages.append({"role": "assistant", "content": action.content})
                    break

                # Record the tool interaction in the private session history
                tool_memory = f"Thought: {action.thought}\nTool: {action.tool}\nResult: {result}"
                st.session_state.messages.append({"role": "assistant", "content": tool_memory})
                st.write(f"**Tool Output:** `{result}`")

            except Exception as e:
                if "QUOTA_LIMIT_REACHED" in str(e) or "429" in str(e):
                    status_placeholder.warning("⚠️ API Quota reached. Pausing for 60s...")
                    progress_bar = st.progress(0)
                    for i in range(60):
                        time.sleep(1)
                        progress_bar.progress((i + 1) / 60)
                    progress_bar.empty()
                    step -= 1
                    continue
                else:
                    st.error(f"Critical System Error: {e}")
                    break
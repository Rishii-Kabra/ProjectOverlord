import streamlit as st
from core.orchestrator import ProjectOrchestrator
from core.memory import TaskMemory
from core.validator import CodeValidator
from tools.file_manager import FileManager
from tools.shell import ShellTool
from tools.browser import WebBrowser
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Project Overlord", page_icon="🤖", layout="wide")
st.title("🤖 Project Overlord: Autonomous Agent")
st.markdown("---")


# --- INITIALIZE CORE ---
# We use @st.cache_resource so it doesn't reload everything on every click
@st.cache_resource
def init_system():
    return {
        "orchestrator": ProjectOrchestrator(),
        "memory": TaskMemory(),
        "files": FileManager(),
        "shell": ShellTool(),
        "browser": WebBrowser(),
        "validator": CodeValidator()
    }


sys = init_system()

# --- SIDEBAR (Memory Management) ---
with st.sidebar:
    st.header("Memory Control")
    if st.button("Clear Long-Term Memory"):
        sys["memory"].clear_memory()
        st.success("Memory Wiped!")

    st.header("Workspace Files")
    # Show files currently in the workspace
    files = [f for f in sys["files"].list_files()]  # You might need to add list_files to FileManager
    st.write(files)

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history from the database on load
for event in sys["memory"].get_history():
    with st.chat_message(event["role"]):
        st.markdown(event["parts"][0]["text"])

# User Input
if prompt := st.chat_input("What is your command, Architect?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    sys["memory"].add_event("user", prompt)

    # --- AGENT LOOP ---
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        thought_placeholder = st.expander("AI Thought Process", expanded=True)

        step = 0
        while step < 5:
            step += 1
            status_placeholder.info(f"Step {step}: Thinking...")

            try:
                # 1. Get history and call orchestrator
                history = sys["memory"].get_history()
                action = sys["orchestrator"].get_next_action(history)

                if not action:
                    st.error("The AI failed to generate a plan. Try a different prompt.")
                    break

                # 2. Add the thought to the UI
                thought_placeholder.write(f"**Step {step} Thought:** {action.thought}")

                # ... (rest of your tool handling logic: SEARCH_WEB, WRITE_FILE, etc.) ...

            except Exception as e:
                if "QUOTA_LIMIT_REACHED" in str(e):
                    # Show the warning in the UI
                    status_placeholder.warning("⚠️ API Quota Hit! Pausing for 30s...")

                    # Cool progress bar for the user
                    progress_bar = st.progress(0)
                    for i in range(30):
                        time.sleep(1)
                        progress_bar.progress((i + 1) / 30)
                    progress_bar.empty()

                    # Decrement step so this failed attempt doesn't count towards the 5-step limit
                    step -= 1
                    continue
                else:
                    st.error(f"Critical System Error: {e}")
                    break

            if not action:
                st.error("AI failed to respond.")
                break

            thought_placeholder.write(f"**Thought:** {action.thought}")

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
                st.success(action.content)
                sys["memory"].add_event("model", action.content)
                break

            # Update memory and UI with tool result
            sys["memory"].add_event("model", f"Thought: {action.thought}\nTool: {action.tool}\nResult: {result}")
            st.write(f"**Tool Output:** `{result}`")
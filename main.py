import os
from wsgiref.validate import validator

import dotenv
from dotenv import load_dotenv

from core.orchestrator import ProjectOrchestrator
from core.memory import TaskMemory
from core.validator import CodeValidator
from tools.file_manager import FileManager
from tools.shell import ShellTool
from rich.console import Console
from rich.panel import Panel
from tools.browser import WebBrowser

load_dotenv()

def main():
    #initialize our system
    console = Console()
    orchestrator = ProjectOrchestrator()
    memory = TaskMemory()
    files = FileManager()
    shell = ShellTool()
    browser = WebBrowser()

    console.print(Panel("[bold cyan] PROJECT OVERLORD ONLINE [/bold cyan] \n [base] Autonomous System Architech Initialized"))

    # Ask the user if they want to resume
    if memory.get_history():
        choice = input("Previous memory found. Resume session? (y/n): ").lower()
        if choice != 'y':
            memory.clear_memory()
            console.print("[yellow]Memory cleared. Starting fresh.[/yellow]")

    # get the users task
    user_task = input("\n[USER]: ")
    memory.add_event("user", user_task)

    running = True
    step_count = 0
    max_steps = 10 #safety limit to prevent infinite loop
    last_action = None

    while running and step_count < max_steps:
        step_count += 1
        console.print(f"\n[bold yellow]Step #{step_count}: AI is thinking...[/bold yellow]")

        #ask the brain what to do next
        summarized_context = memory.get_summarized_history()
        action = orchestrator.get_next_action(summarized_context)

        if not action:
            console.print("[bold red]ERROR: Brain failed to respond.[/bold red]")
            break

        if last_action and action.tool == last_action.tool and action.file_name == last_action.file_name:
            console.print("[bold red]SYSTEM INTERVENTION: Duplicate action detected.[/bold red]")
            memory.add_event("user", "You just attempted the exact same action. Do not repeat. Move to the next step.")
            continue

        last_action = action  # Update the tracker

        console.print(Panel(f"[italic]{action.thought}[/italic]", title="AI Thought Process", border_style="blue"))

        # execute the tool chosen by the AI
        result = ""
        if action.tool == "WRITE_FILE":
            validator = CodeValidator()
            check = validator.validate_code(action.content)

            if "UNSAFE" in check.upper():
                result = f"SECURITY REJECTION: {check}. Please rewrite the code safely."
                console.print(f"[bold red]{result}[/bold red]")
            else:
                result = files.write_file(action.file_name, action.content)

        elif action.tool == "RUN_CODE":
            result = shell.execute_python(action.file_name)

        elif action.tool == "INSTALL_PACKAGE":
            result = shell.install_package(action.content)

        elif action.tool == "SEARCH_WEB":
            console.print(f"[yellow]Searching the web for: {action.content}...[/yellow]")
            result = browser.search(action.content)


        elif action.tool == "FINAL_ANSWER":
            # Show the answer in the console
            console.print(Panel(f"[bold green]{action.content}[/bold green]", title="Task Complete"))

            # NEW: Generate a permanent report
            console.print("[dim italic]Generating final report...[/dim italic]")
            report_content = f"### Result\n{action.content}\n\n### Process\n"

            # Add the last few thoughts from memory to the report
            for event in memory.get_history()[-5:]:
                report_content += f"- {event['parts'][0]['text']}\n"
            files.save_report(user_task[:30], report_content)
            running = False
            continue

        #show the result of the tool and add it to memory
        console.print(f"[bold magenta]Tool Result:[/bold magenta] {result}")
        status_update = f"[SYSTEM NOTIFICATION]: {result}"
        memory.add_event("model", f"Thought: {action.thought}\nAction: {action.tool}\nStatus: {status_update}")

if __name__ == "__main__":
    main()
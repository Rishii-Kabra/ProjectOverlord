import os
from google import genai
from google.genai import types
import streamlit as st

class CodeValidator:
    def __init__(self):
        api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("No GEMINI_API_KEY found. Check Streamlit Secrets or .env file.")

        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.5-flash"
        self.system_prompt = (
            "You are a Security Auditor. Review the provided Python code. "
            "Review the code for: \n"
            "1. Deleting files (os.remove, shutil.rmtree)\n"
            "2. Infinite loops (while True without breaks)\n"
            "3. Accessing sensitive system info (os.environ, passwords)\n\n"
            "If the code is dangerous, respond with 'UNSAFE: [reason]'. "
            "If the code is clean, respond ONLY with the word 'SAFE'."
            "If it contains dangerous commands (deleting files, system shutdowns, "
            "accessing files outside the workspace) or infinite loops, respond with 'UNSAFE: [reason]'. "
            "Otherwise, respond with 'SAFE'."
        )

    def validate_code(self, code: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=f"Code to review:\n\n{code}",
            config=types.GenerateContentConfig(system_instruction=self.system_prompt)
        )
        return response.text.strip()
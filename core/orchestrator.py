import os
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from google import genai
from dotenv import load_dotenv
from google.genai import types
import time

load_dotenv()

# 1. Define the 'Action' structure the AI MUST follow
class AgentAction(BaseModel):
    thought: str = Field(description="The AI's reasoning for this step")
    tool: Literal["WRITE_FILE", "RUN_CODE", "INSTALL_PACKAGE","SEARCH_WEB", "FINAL_ANSWER"]
    file_name: Optional[str] = None
    content: Optional[str] = Field(None, description="The code or command to execute")

class ProjectOrchestrator:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = "gemini-2.5-flash" # High speed for iterative tasks
        self.system_prompt = (
            "You are Overlord, an autonomous engineer. "
            "Execute tasks efficiently. If you write a file, move immediately to the next step (like running it). "
            "Always provide the file_name when using WRITE_FILE or RUN_CODE tools. "
            "Once you have the final result, use the FINAL_ANSWER tool."
            "EFFICIENCY RULE: Never repeat an action that has already succeeded. "
            "If 'Tool Result' confirms a file was written, move IMMEDIATELY to execution. "
            "If 'Tool Result' provides a numeric output, move IMMEDIATELY to FINAL_ANSWER. "
            "Do not second-guess successful tool outputs."
            "You have access to a SEARCH_WEB tool. Use it if you need real-time information or "
            "if you are unsure about a specific library or fact."
            "You are Overlord. TOKEN EFFICIENCY IS CRITICAL. "
            "When you receive SEARCH_WEB results, extract the key data immediately and "
            "do not repeat the raw snippets in your future thoughts. "
            "If you hit a quota error, your next response must be extremely brief."
        )

    def get_next_action(self, task_history: List[dict]) -> Optional[AgentAction]:
        try:

            # 1. Properly construct the list using the SDK's internal types
            formatted_history: List[types.Content] = []
            for entry in task_history:
                formatted_history.append(
                    types.Content(
                        role=entry["role"],
                        parts=[types.Part(text=entry["parts"][0]["text"])]
                    )
                )

            config = types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                response_mime_type="application/json",
                response_schema=AgentAction,
            )

            # 2. Call the model
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=formatted_history,  # PyCharm should now see List[types.Content]
                config=config,
            )

            # If the response is empty, we still want to be safe
            if not response or not response.parsed:
                return None

            return response.parsed

        except Exception as e:
            if "429" in str(e):
                # JUST RAISE THE ERROR. DO NOT SLEEP. DO NOT RECURSE.
                raise Exception("QUOTA_LIMIT_REACHED")
            else:
                print(f"DEBUG: AI Generation failed: {e}")
                return None
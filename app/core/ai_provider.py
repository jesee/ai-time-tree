import os
import logging
import json
from abc import ABC, abstractmethod

# Conditional imports based on provider
import requests

try:
    import openai
except ImportError:
    openai = None

from app.core.config import (
    GEMINI_API_KEY, GEMINI_MODEL_ID,
    OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_MODEL_ID,
    AI_PROVIDER
)

class AIProvider(ABC):
    """Abstract Base Class for AI providers."""
    @abstractmethod
    def generate_structured_output(self, prompt: str):
        """Generates structured JSON output from a prompt."""
        pass

class GeminiClient(AIProvider):
    """AI Provider implementation for Google Gemini using direct REST API calls."""
    def __init__(self, api_key: str, model_id: str):
        self.api_key = api_key
        self.model_id = model_id
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_id}:generateContent?key={self.api_key}"
        logging.info(f"GeminiClient (REST) initialized for model '{model_id}'.")

    def generate_structured_output(self, prompt: str):
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "response_mime_type": "application/json",
            }
        }
        try:
            logging.info("Sending request to Gemini REST API...")
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status() # Raise an exception for bad status codes
            
            logging.info("Received response from Gemini REST API.")
            
            # Correctly parse the nested JSON structure from the response
            response_data = response.json()
            text_content = response_data['candidates'][0]['content']['parts'][0]['text']
            
            return json.loads(text_content)
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred with Gemini REST API: {e}")
            # Try to get more details from the response if available
            if e.response is not None:
                logging.error(f"Response body: {e.response.text}")
            return None
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logging.error(f"Failed to parse JSON from Gemini REST response: {e}")
            logging.error(f"Full response text: {response.text}")
            return None

class OpenAIClient(AIProvider):
    """AI Provider implementation for OpenAI-compatible APIs."""
    def __init__(self, api_key: str, model_id: str, base_url: str):
        if not openai:
            raise ImportError("The 'openai' library is required. Please install it.")
        try:
            self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
            self.model_id = model_id
            logging.info(f"OpenAIClient initialized for model '{model_id}' at '{base_url}'.")
        except Exception as e:
            logging.error(f"Failed to initialize OpenAIClient: {e}")
            raise

    def generate_structured_output(self, prompt: str):
        try:
            logging.info("Sending request to OpenAI-compatible API...")
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                timeout=60
            )
            logging.info("Received response from OpenAI-compatible API.")
            
            content = response.choices[0].message.content
            return json.loads(content)
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON from OpenAI response: {content}")
            return None
        except Exception as e:
            logging.error(f"An error occurred with OpenAI-compatible API: {e}")
            return None

def get_ai_client() -> AIProvider:
    """
    Factory function to get the configured AI client.
    """
    if AI_PROVIDER.lower() == "gemini":
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured in .env file.")
        return GeminiClient(api_key=GEMINI_API_KEY, model_id=GEMINI_MODEL_ID)
    elif AI_PROVIDER.lower() == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured in .env file.")
        return OpenAIClient(api_key=OPENAI_API_KEY, model_id=OPENAI_MODEL_ID, base_url=OPENAI_API_BASE)
    else:
        raise ValueError(f"Unsupported AI_PROVIDER specified in .env: {AI_PROVIDER}")

# Initialize a global client instance
try:
    ai_client = get_ai_client()
except (ValueError, ImportError) as e:
    logging.error(f"Could not initialize AI client: {e}")
    ai_client = None

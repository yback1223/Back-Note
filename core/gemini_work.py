from google import genai
from google.genai import types
import json
import time
import logging
import traceback
from typing import Optional

class GeminiWork:
    @staticmethod
    def call_gemini(api_key: str, prompt: str, model: str = "gemini-2.5-pro", retries: int = 3) -> str:
        try:
            # Input validation
            if not api_key or not api_key.strip():
                raise ValueError("API key cannot be empty")
            
            if not prompt or not prompt.strip():
                raise ValueError("Prompt cannot be empty")
            
            if not model or not model.strip():
                raise ValueError("Model cannot be empty")
            
            if not isinstance(retries, int) or retries < 0:
                raise ValueError("Retries must be a non-negative integer")
            
            result = ""
            
            # Initialize Gemini client
            try:
                client = genai.Client(api_key=api_key)
            except Exception as e:
                logging.error(f"Failed to initialize Gemini client: {traceback.format_exc()}")
                raise Exception(f"Failed to initialize Gemini client: {str(e)}")

            # Prepare content
            try:
                contents = [
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=prompt),
                        ],
                    ),
                ]
            except Exception as e:
                logging.error(f"Failed to create content: {traceback.format_exc()}")
                raise Exception(f"Failed to create content: {str(e)}")

            # Prepare tools
            try:
                tools = [
                    types.Tool(googleSearch=types.GoogleSearch()),
                ]
            except Exception as e:
                logging.error(f"Failed to create tools: {traceback.format_exc()}")
                raise Exception(f"Failed to create tools: {str(e)}")

            # Prepare configuration
            try:
                generate_content_config = types.GenerateContentConfig(
                    max_output_tokens=8192,
                    thinking_config=types.ThinkingConfig(
                        thinking_budget=-1,
                    ),
                    tools=tools,
                )
            except Exception as e:
                logging.error(f"Failed to create configuration: {traceback.format_exc()}")
                raise Exception(f"Failed to create configuration: {str(e)}")

            # Generate content
            try:
                for chunk in client.models.generate_content_stream(
                    model=model,
                    contents=contents,
                    config=generate_content_config,
                ):
                    if hasattr(chunk, 'text') and chunk.text:
                        result += chunk.text
            except Exception as e:
                logging.error(f"Failed to generate content: {traceback.format_exc()}")
                raise Exception(f"Failed to generate content: {str(e)}")
            
            # Validate result
            if not result or not result.strip():
                logging.warning("No result received from Gemini")
                raise Exception("No result from Gemini")
            
            # Clean up result
            cleaned_result = result.replace("```json", "").replace("```", "").replace("```json", "").replace("```", "")
            
            if not cleaned_result.strip():
                logging.warning("Result is empty after cleaning")
                raise Exception("Empty result after cleaning")
            
            return cleaned_result
            
        except Exception as e:
            # Log the error
            logging.error(f"Gemini API error occurred: {traceback.format_exc()}")
            
            # Retry logic
            if retries > 0:
                logging.info(f"Retrying Gemini API call... ({retries} attempts left)")
                time.sleep(2)  # Wait before retrying
                return GeminiWork.call_gemini(api_key, prompt, model, retries - 1)
            else:
                logging.error("All retries failed for Gemini API call")
                error_response = {
                    "error": f"The request failed after multiple retries. Last error: {str(e)}",
                    "retries_attempted": 3,
                    "original_error": str(e)
                }
                return json.dumps(error_response)
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key format"""
        try:
            if not api_key or not api_key.strip():
                return False
            
            # Basic validation for Gemini API key format
            if len(api_key) < 10:  # Minimum reasonable length
                return False
            
            return True
        except Exception as e:
            logging.error(f"API key validation error: {traceback.format_exc()}")
            return False
    
    @staticmethod
    def validate_prompt(prompt: str) -> bool:
        """Validate prompt content"""
        try:
            if not prompt or not prompt.strip():
                return False
            
            if len(prompt) < 10:  # Minimum reasonable length
                return False
            
            return True
        except Exception as e:
            logging.error(f"Prompt validation error: {traceback.format_exc()}")
            return False
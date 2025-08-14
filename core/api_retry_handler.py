import time
import logging
import traceback
from typing import Callable, Any, Tuple


class APIRetryHandler:
    @staticmethod
    def call_with_retry(api_call_func: Callable, max_retries: int = 5, 
                       retry_delay: float = 2.0, *args, **kwargs) -> Tuple[Any, Any]:
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                result = api_call_func(*args, **kwargs)
                return result
                
            except Exception as e:
                retry_count += 1
                logging.warning(f"API call attempt {retry_count} failed: {str(e)}")
                
                if retry_count >= max_retries:
                    logging.error(f"All {max_retries} attempts failed for API call")
                    raise Exception(f"Failed to process after {max_retries} attempts: {str(e)}")
                
                time.sleep(retry_delay)
    
    @staticmethod
    def call_gemini_with_retry(api_key: str, prompt: str, model: str, 
                              max_retries: int = 5, retry_delay: float = 2.0) -> str:
        from .gemini_work import GeminiWork
        
        def gemini_call():
            return GeminiWork.call_gemini(api_key=api_key, prompt=prompt, model=model)
        
        return APIRetryHandler.call_with_retry(
            gemini_call, 
            max_retries=max_retries, 
            retry_delay=retry_delay
        )

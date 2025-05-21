"""
Utility for communicating with the Box AI API.
"""
import requests
import json
from typing import Dict, Optional, Any

class BoxAIClient:
    """Client for interacting with the Box AI API."""
    
    def __init__(self, developer_token: str, base_url: str = "https://api.box.com"):
        """
        Initialize the Box AI client.
        
        Args:
            developer_token: Box API developer token
            base_url: Base URL for Box API
        """
        self.developer_token = developer_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {developer_token}",
            "Content-Type": "application/json"
        }
    
    def generate_text(self, prompt: str) -> Dict:
        """
        Generate text using the Box AI API.
        
        Args:
            prompt: Prompt text for the AI
            
        Returns:
            Dictionary with API response
        """
        try:
            url = f"{self.base_url}/2.0/ai/text_gen"
            
            payload = {
                "prompt": prompt,
                "temperature": 0.2,  # Lower temperature for more deterministic output
                "max_tokens": 1000
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error calling Box AI API: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nStatus code: {e.response.status_code}"
                error_msg += f"\nResponse: {e.response.text}"
            raise Exception(error_msg)
    
    def validate_token(self) -> bool:
        """
        Validate that the developer token is valid.
        
        Returns:
            Boolean indicating if token is valid
        """
        try:
            url = f"{self.base_url}/2.0/users/me"
            response = requests.get(url, headers=self.headers)
            return response.status_code == 200
        except:
            return False
    
    def handle_error(self, error: Exception) -> Dict:
        """
        Handle and format API errors.
        
        Args:
            error: Exception that occurred
            
        Returns:
            Dictionary with error information
        """
        error_str = str(error)
        
        # Try to extract status code and response body
        status_code = None
        response_body = None
        
        if "Status code:" in error_str:
            status_parts = error_str.split("Status code:")
            if len(status_parts) > 1:
                status_code_parts = status_parts[1].split("\n")
                if status_code_parts:
                    try:
                        status_code = int(status_code_parts[0].strip())
                    except:
                        pass
        
        if "Response:" in error_str:
            response_parts = error_str.split("Response:")
            if len(response_parts) > 1:
                response_body = response_parts[1].strip()
                try:
                    response_body = json.loads(response_body)
                except:
                    pass
        
        return {
            "error": True,
            "message": error_str,
            "status_code": status_code,
            "response_body": response_body
        }

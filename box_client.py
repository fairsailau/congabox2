"""
Utility for communicating with the Box API for file operations and AI text generation.
"""
import os
import requests
import json
from typing import Dict, List, Optional, Any, BinaryIO, Union

class BoxClient:
    """Client for interacting with the Box API for file operations and AI text generation."""
    
    def __init__(self, developer_token: str, base_url: str = "https://api.box.com"):
        """
        Initialize the Box client.
        
        Args:
            developer_token: Box API developer token
            base_url: Base URL for Box API
        """
        self.developer_token = developer_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {developer_token}"
        }
    
    def upload_file(self, file_obj: Union[str, BinaryIO], file_name: str, parent_folder_id: str = "0") -> Dict:
        """
        Upload a file to Box.
        
        Args:
            file_obj: File object or path to file
            file_name: Name for the file in Box
            parent_folder_id: ID of the parent folder (default: "0" for root)
            
        Returns:
            Dictionary with file information including ID
        """
        try:
            url = f"{self.base_url}/2.0/files/content"
            
            # Prepare file data
            if isinstance(file_obj, str):
                # It's a file path
                file_data = open(file_obj, 'rb')
            else:
                # It's already a file object
                file_data = file_obj
                
            # Prepare multipart form data
            files = {
                'file': (file_name, file_data)
            }
            
            data = {
                'attributes': json.dumps({
                    'name': file_name,
                    'parent': {'id': parent_folder_id}
                })
            }
            
            # Make request
            response = requests.post(
                url, 
                headers=self.headers, 
                files=files, 
                data=data
            )
            response.raise_for_status()
            
            # Close file if we opened it
            if isinstance(file_obj, str) and file_data:
                file_data.close()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error uploading file to Box: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nStatus code: {e.response.status_code}"
                error_msg += f"\nResponse: {e.response.text}"
            raise Exception(error_msg)
    
    def generate_text(self, prompt: str, file_ids: Optional[List[str]] = None) -> Dict:
        """
        Generate text using the Box AI API with file references.
        
        Args:
            prompt: Prompt text for the AI
            file_ids: Optional list of Box file IDs to reference
            
        Returns:
            Dictionary with API response
        """
        try:
            url = f"{self.base_url}/2.0/ai/text_gen"
            
            # Prepare payload
            payload = {
                "prompt": prompt,
                "temperature": 0.2,  # Lower temperature for more deterministic output
                "max_tokens": 1000,
                "ai_agent": {
                    "type": "ai_agent_text_gen",
                    "basic_gen": {
                        "model": "azure__openai__gpt_4o_mini"  # Default model
                    }
                }
            }
            
            # Add file references if provided
            if file_ids and len(file_ids) > 0:
                payload["items"] = [
                    {"id": file_id, "type": "file"} for file_id in file_ids
                ]
            
            # Set content type header for JSON
            headers = self.headers.copy()
            headers["Content-Type"] = "application/json"
            
            # Make request
            response = requests.post(url, headers=headers, json=payload)
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

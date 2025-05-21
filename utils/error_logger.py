"""
Utility for logging errors during conversion process.
"""
import os
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any

class ErrorLogger:
    """Logger for recording and displaying errors."""
    
    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize the error logger.
        
        Args:
            log_file: Path to the log file (optional)
        """
        self.errors = []
        self.log_file = log_file
        
        # Set up logging if log file is provided
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            logging.basicConfig(
                filename=log_file,
                level=logging.ERROR,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
    
    def log_error(self, error_type: str, message: str, context: Optional[Dict] = None) -> Dict:
        """
        Log an error with context information.
        
        Args:
            error_type: Type of error (e.g., 'parsing', 'api', 'conversion')
            message: Error message
            context: Additional context information (optional)
            
        Returns:
            Dictionary with error information
        """
        timestamp = datetime.now().isoformat()
        
        error_info = {
            "timestamp": timestamp,
            "type": error_type,
            "message": message,
            "context": context or {}
        }
        
        # Add stack trace if available
        if 'exception' in error_info.get('context', {}):
            exception = error_info['context']['exception']
            if isinstance(exception, Exception):
                error_info['context']['traceback'] = traceback.format_exc()
                # Remove the actual exception object to avoid serialization issues
                error_info['context']['exception'] = str(exception)
        
        # Add to in-memory list
        self.errors.append(error_info)
        
        # Log to file if available
        if self.log_file:
            logging.error(
                f"Error Type: {error_type}, Message: {message}, Context: {context}"
            )
        
        return error_info
    
    def get_errors(self, error_type: Optional[str] = None) -> List[Dict]:
        """
        Get all logged errors, optionally filtered by type.
        
        Args:
            error_type: Type of errors to filter (optional)
            
        Returns:
            List of error dictionaries
        """
        if error_type:
            return [e for e in self.errors if e.get('type') == error_type]
        return self.errors
    
    def format_errors_for_display(self) -> str:
        """
        Format errors as a string for display in the UI.
        
        Returns:
            Formatted string representation of errors
        """
        if not self.errors:
            return "No errors logged."
        
        result = ""
        for i, error in enumerate(self.errors, 1):
            timestamp = error.get('timestamp', '')
            error_type = error.get('type', 'unknown')
            message = error.get('message', '')
            
            result += f"**Error {i}** ({error_type}) - {timestamp}\n"
            result += f"{message}\n\n"
            
            # Add context details if available
            context = error.get('context', {})
            if context:
                result += "Context:\n"
                for key, value in context.items():
                    if key != 'traceback':  # Skip traceback for display
                        result += f"- {key}: {value}\n"
                result += "\n"
        
        return result
    
    def clear_errors(self) -> None:
        """Clear all logged errors."""
        self.errors = []

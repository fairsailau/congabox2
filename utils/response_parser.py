"""
Utility for parsing Box AI API responses.
"""
import re
import csv
from io import StringIO
from typing import Dict, List, Optional

class ResponseParser:
    """Parser for processing Box AI API responses."""
    
    def __init__(self):
        """Initialize the response parser."""
        pass
    
    def parse_mapping_response(self, response_text: str) -> List[Dict]:
        """
        Parse the Box AI API response for field mapping.
        
        Args:
            response_text: Response text from Box AI API
            
        Returns:
            List of dictionaries with field mapping information
        """
        try:
            # Clean up response text to ensure it's valid CSV
            # Remove any non-CSV content before or after the actual CSV data
            csv_lines = []
            in_csv = False
            
            for line in response_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Check if this line looks like CSV
                if ',' in line and (line.startswith('conga_field') or line.startswith('«')):
                    in_csv = True
                elif in_csv and not ',' in line:
                    in_csv = False
                
                if in_csv:
                    csv_lines.append(line)
            
            if not csv_lines:
                raise Exception("No valid CSV data found in response")
            
            # Parse CSV data
            csv_data = '\n'.join(csv_lines)
            reader = csv.DictReader(StringIO(csv_data))
            
            mappings = []
            for row in reader:
                # Ensure required fields are present
                if 'conga_field' not in row or 'box_field' not in row:
                    continue
                
                mapping = {
                    'conga_field': row['conga_field'].strip(),
                    'box_field': row['box_field'].strip(),
                    'notes': row.get('notes', '').strip()
                }
                mappings.append(mapping)
            
            return mappings
            
        except Exception as e:
            raise Exception(f"Error parsing mapping response: {str(e)}")
    
    def parse_error_analysis(self, response_text: str) -> Dict:
        """
        Parse the Box AI API response for error analysis.
        
        Args:
            response_text: Response text from Box AI API
            
        Returns:
            Dictionary with error analysis information
        """
        try:
            # Extract sections from the response
            cause_match = re.search(r'(?:Cause|CAUSE):(.*?)(?:Solutions|SOLUTIONS|$)', response_text, re.DOTALL)
            solutions_match = re.search(r'(?:Solutions|SOLUTIONS):(.*?)(?:Additional Information|ADDITIONAL INFORMATION|$)', response_text, re.DOTALL)
            additional_match = re.search(r'(?:Additional Information|ADDITIONAL INFORMATION):(.*?)$', response_text, re.DOTALL)
            
            cause = cause_match.group(1).strip() if cause_match else ""
            solutions = solutions_match.group(1).strip() if solutions_match else ""
            additional = additional_match.group(1).strip() if additional_match else ""
            
            return {
                "cause": cause,
                "solutions": solutions,
                "additional_information": additional
            }
            
        except Exception as e:
            return {
                "error": True,
                "message": f"Error parsing error analysis: {str(e)}",
                "raw_response": response_text
            }

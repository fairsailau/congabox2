"""
Utility for building prompts for the Box AI API.
"""
from typing import Dict, List, Optional

class PromptBuilder:
    """Builder for creating prompts for the Box AI API."""
    
    def __init__(self):
        """Initialize the prompt builder."""
        pass
    
    def build_conversion_prompt(self) -> str:
        """
        Build a prompt for the Box AI API to convert Conga template to Box Doc Gen format.
        
        Returns:
            Formatted prompt string for Box AI API
        """
        prompt = """
You are an expert in document template conversion. Your task is to convert a Conga template to Box Doc Gen format.

I have uploaded three files:
1. A Conga template DOCX file
2. A SOQL query text file
3. A Box-Salesforce JSON schema file

Please analyze these files and:
1. For each Conga merge field (format: «Field»), provide the equivalent Box Doc Gen merge field (format: {{Object.Field}}).
2. Use the SOQL query and schema information to determine the correct object and field names.
3. Return your answer as a CSV-compatible mapping with the following columns:
   - conga_field: The original Conga merge field including delimiters
   - box_field: The equivalent Box Doc Gen merge field
   - notes: Any notes or explanations about the mapping

RESPONSE FORMAT:
conga_field,box_field,notes
«Field1»,{{Object.Field1}},Direct mapping
«Field2»,{{RelatedObject.Field2}},Relationship field
...

Only include the CSV data in your response, no other text.
"""
        
        return prompt
    
    def build_error_analysis_prompt(self, error_context: str) -> str:
        """
        Build a prompt for the Box AI API to analyze conversion errors.
        
        Args:
            error_context: Context information about the error
            
        Returns:
            Formatted prompt string for Box AI API
        """
        prompt = f"""
You are an expert in document template conversion. Your task is to analyze an error that occurred during the conversion of a Conga template to Box Doc Gen format.

ERROR CONTEXT:
```
{error_context}
```

INSTRUCTIONS:
1. Analyze the error and identify the most likely cause.
2. Suggest possible solutions or workarounds.
3. Provide any additional information that might be helpful for debugging.

RESPONSE FORMAT:
Please provide your analysis in a structured format with sections for Cause, Solutions, and Additional Information.
"""
        
        return prompt

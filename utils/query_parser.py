"""
Utility for parsing SOQL queries to understand data structure.
"""
import re
from typing import Dict, List, Optional

class QueryParser:
    """Parser for extracting information from Conga SOQL queries."""
    
    def __init__(self):
        """Initialize the SOQL query parser."""
        # Regex patterns for SOQL query components
        self.select_pattern = re.compile(r'SELECT\s+(.*?)\s+FROM', re.IGNORECASE | re.DOTALL)
        self.from_pattern = re.compile(r'FROM\s+(\w+)', re.IGNORECASE)
        self.where_pattern = re.compile(r'WHERE\s+(.*?)(?:ORDER BY|GROUP BY|LIMIT|$)', re.IGNORECASE | re.DOTALL)
        self.relationship_pattern = re.compile(r'(\w+)\.(\w+)', re.IGNORECASE)
    
    def parse_query(self, query_text: str) -> Dict:
        """
        Parse a SOQL query to extract fields, objects, and relationships.
        
        Args:
            query_text: The SOQL query text
            
        Returns:
            Dictionary with query information
        """
        try:
            query_text = query_text.strip()
            
            # Extract SELECT fields
            select_match = self.select_pattern.search(query_text)
            fields = []
            if select_match:
                fields_text = select_match.group(1)
                fields = [f.strip() for f in fields_text.split(',')]
            
            # Extract FROM object
            from_match = self.from_pattern.search(query_text)
            main_object = from_match.group(1) if from_match else None
            
            # Extract WHERE conditions
            where_match = self.where_pattern.search(query_text)
            conditions = where_match.group(1).strip() if where_match else None
            
            # Extract relationships
            relationships = {}
            for field in fields:
                rel_match = self.relationship_pattern.match(field)
                if rel_match:
                    rel_object, rel_field = rel_match.groups()
                    if rel_object not in relationships:
                        relationships[rel_object] = []
                    relationships[rel_object].append(rel_field)
            
            return {
                "main_object": main_object,
                "fields": fields,
                "conditions": conditions,
                "relationships": relationships
            }
            
        except Exception as e:
            raise Exception(f"Error parsing SOQL query: {str(e)}")
    
    def get_field_paths(self, query_info: Dict) -> List[str]:
        """
        Generate field paths from parsed query information.
        
        Args:
            query_info: Dictionary with parsed query information
            
        Returns:
            List of field paths in format "Object.Field"
        """
        field_paths = []
        main_object = query_info.get("main_object")
        
        if not main_object:
            return field_paths
        
        for field in query_info.get("fields", []):
            if "." in field:
                # Field is already in relationship format
                field_paths.append(field)
            else:
                # Add main object prefix
                field_paths.append(f"{main_object}.{field}")
        
        return field_paths

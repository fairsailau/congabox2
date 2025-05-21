"""
Utility for parsing JSON schema to identify field mappings.
"""
import json
from typing import Dict, List, Optional, Any

class SchemaParser:
    """Parser for processing Box-Salesforce JSON schema."""
    
    def __init__(self):
        """Initialize the schema parser."""
        pass
    
    def parse_schema(self, schema_file) -> Dict:
        """
        Parse a JSON schema file to extract object and field information.
        
        Args:
            schema_file: Path to the JSON schema file or file-like object
            
        Returns:
            Dictionary with parsed schema information
        """
        try:
            if isinstance(schema_file, str):
                with open(schema_file, 'r') as f:
                    schema_data = json.load(f)
            else:
                schema_data = json.load(schema_file)
            
            # Extract objects and their fields
            objects = {}
            self._extract_objects_and_fields(schema_data, objects)
            
            return {
                "objects": objects,
                "raw_schema": schema_data
            }
            
        except Exception as e:
            raise Exception(f"Error parsing JSON schema: {str(e)}")
    
    def _extract_objects_and_fields(self, schema_data: Dict, objects: Dict, parent_path: str = "") -> None:
        """
        Recursively extract objects and fields from schema data.
        
        Args:
            schema_data: Schema data dictionary or sub-dictionary
            objects: Dictionary to populate with objects and fields
            parent_path: Path to current position in schema
        """
        if not isinstance(schema_data, dict):
            return
        
        # Check if this is an object definition
        if "properties" in schema_data and isinstance(schema_data["properties"], dict):
            object_name = self._get_object_name(schema_data, parent_path)
            if object_name:
                if object_name not in objects:
                    objects[object_name] = {
                        "fields": {},
                        "relationships": {}
                    }
                
                # Process fields
                for field_name, field_def in schema_data["properties"].items():
                    field_type = field_def.get("type", "string")
                    
                    if field_type == "object" and "properties" in field_def:
                        # This is a relationship
                        rel_object_name = self._get_object_name(field_def, f"{parent_path}.{field_name}")
                        if rel_object_name:
                            objects[object_name]["relationships"][field_name] = rel_object_name
                            # Recursively process the related object
                            self._extract_objects_and_fields(field_def, objects, f"{parent_path}.{field_name}")
                    else:
                        # This is a regular field
                        objects[object_name]["fields"][field_name] = {
                            "type": field_type,
                            "description": field_def.get("description", ""),
                            "required": field_name in schema_data.get("required", [])
                        }
        
        # Continue recursion for other properties
        for key, value in schema_data.items():
            if isinstance(value, dict):
                self._extract_objects_and_fields(value, objects, f"{parent_path}.{key}" if parent_path else key)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._extract_objects_and_fields(item, objects, f"{parent_path}.{key}[{i}]" if parent_path else f"{key}[{i}]")
    
    def _get_object_name(self, obj_def: Dict, path: str) -> Optional[str]:
        """
        Extract object name from object definition.
        
        Args:
            obj_def: Object definition dictionary
            path: Path to current position in schema
            
        Returns:
            Object name or None if not found
        """
        # Try to get object name from title
        if "title" in obj_def:
            return obj_def["title"]
        
        # Try to get from path
        if path:
            parts = path.split(".")
            return parts[-1]
        
        return None
    
    def find_field_mapping(self, schema_info: Dict, field_path: str) -> Optional[Dict]:
        """
        Find field information in schema based on field path.
        
        Args:
            schema_info: Parsed schema information
            field_path: Field path in format "Object.Field" or "Object.Relationship.Field"
            
        Returns:
            Dictionary with field mapping information or None if not found
        """
        parts = field_path.split(".")
        if len(parts) < 2:
            return None
        
        object_name = parts[0]
        objects = schema_info.get("objects", {})
        
        if object_name not in objects:
            return None
        
        if len(parts) == 2:
            # Direct field
            field_name = parts[1]
            if field_name in objects[object_name]["fields"]:
                return {
                    "object": object_name,
                    "field": field_name,
                    "path": field_path,
                    "info": objects[object_name]["fields"][field_name]
                }
        else:
            # Relationship field
            current_obj = object_name
            for i in range(1, len(parts) - 1):
                rel_name = parts[i]
                if rel_name in objects.get(current_obj, {}).get("relationships", {}):
                    current_obj = objects[current_obj]["relationships"][rel_name]
                else:
                    return None
            
            field_name = parts[-1]
            if current_obj in objects and field_name in objects[current_obj]["fields"]:
                return {
                    "object": current_obj,
                    "field": field_name,
                    "path": field_path,
                    "info": objects[current_obj]["fields"][field_name]
                }
        
        return None

"""
Utility for generating CSV mapping between Conga and Box formats.
"""
import csv
import os
from typing import Dict, List, Optional

class MappingGenerator:
    """Generator for creating CSV mapping files."""
    
    def __init__(self):
        """Initialize the mapping generator."""
        pass
    
    def generate_csv_mapping(self, mappings: List[Dict], output_file: str) -> str:
        """
        Generate a CSV file with field mappings.
        
        Args:
            mappings: List of dictionaries with field mapping information
            output_file: Path to the output CSV file
            
        Returns:
            Path to the generated CSV file
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Write mappings to CSV file
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['conga_field', 'box_field', 'notes'])
                writer.writeheader()
                for mapping in mappings:
                    writer.writerow(mapping)
            
            return output_file
            
        except Exception as e:
            raise Exception(f"Error generating CSV mapping: {str(e)}")
    
    def format_mappings_for_display(self, mappings: List[Dict]) -> str:
        """
        Format mappings as a string for display in the UI.
        
        Args:
            mappings: List of dictionaries with field mapping information
            
        Returns:
            Formatted string representation of mappings
        """
        if not mappings:
            return "No mappings found."
        
        result = "| Conga Field | Box Field | Notes |\n"
        result += "|------------|-----------|-------|\n"
        
        for mapping in mappings:
            conga_field = mapping.get('conga_field', '')
            box_field = mapping.get('box_field', '')
            notes = mapping.get('notes', '')
            
            result += f"| {conga_field} | {box_field} | {notes} |\n"
        
        return result

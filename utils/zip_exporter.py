"""
Utility for creating ZIP files with conversion results.
"""
import os
import zipfile
from typing import Dict, List, Optional

class ZipExporter:
    """Exporter for creating ZIP files with conversion results."""
    
    def __init__(self):
        """Initialize the ZIP exporter."""
        pass
    
    def create_zip(self, files_to_zip: Dict[str, str], output_file: str) -> str:
        """
        Create a ZIP file with conversion results.
        
        Args:
            files_to_zip: Dictionary mapping file names in ZIP to local file paths
            output_file: Path to the output ZIP file
            
        Returns:
            Path to the generated ZIP file
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Create ZIP file
            with zipfile.ZipFile(output_file, 'w') as zipf:
                for zip_path, local_path in files_to_zip.items():
                    if os.path.exists(local_path):
                        zipf.write(local_path, zip_path)
            
            return output_file
            
        except Exception as e:
            raise Exception(f"Error creating ZIP file: {str(e)}")
    
    def add_readme_to_zip(self, zip_file: str, readme_content: str) -> str:
        """
        Add a README file to an existing ZIP file.
        
        Args:
            zip_file: Path to the ZIP file
            readme_content: Content for the README file
            
        Returns:
            Path to the updated ZIP file
        """
        try:
            # Create temporary README file
            readme_path = os.path.join(os.path.dirname(zip_file), "README.txt")
            with open(readme_path, 'w') as f:
                f.write(readme_content)
            
            # Add README to ZIP
            with zipfile.ZipFile(zip_file, 'a') as zipf:
                zipf.write(readme_path, "README.txt")
            
            # Clean up temporary file
            os.remove(readme_path)
            
            return zip_file
            
        except Exception as e:
            raise Exception(f"Error adding README to ZIP: {str(e)}")

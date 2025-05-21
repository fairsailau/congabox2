# Conga to Box Doc Gen Converter

## Overview
This Streamlit application converts Conga templates to Box Doc Gen format using the Box AI API. The application uploads files to Box and uses file references with the Box AI API for processing, which better leverages Box AI's capabilities to understand document structure.

## Features
- Upload Conga templates (DOCX files)
- Upload or paste SOQL queries
- Upload Box-Salesforce JSON schemas
- Process files using Box AI API with file references
- Generate CSV mapping between Conga and Box Doc Gen formats
- Export all results and original files as a ZIP archive
- Detailed error logging

## Project Structure
```
conga_to_box_converter/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Dependencies
├── .streamlit/             # Streamlit configuration
│   └── secrets.toml.example # Example secrets configuration
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── box_client.py       # Box API client for file operations and AI
│   ├── docx_parser.py      # DOCX parsing utilities
│   ├── query_parser.py     # SOQL query parsing utilities
│   ├── schema_parser.py    # JSON schema parsing utilities
│   ├── prompt_builder.py   # Box AI prompt construction
│   ├── response_parser.py  # AI response processing
│   ├── mapping_generator.py # CSV mapping generation
│   ├── zip_exporter.py     # ZIP file creation
│   └── error_logger.py     # Error logging utilities
└── sample_data/            # Sample files for testing
    ├── create_sample_template.py # Script to generate sample template
    ├── sample_template.docx # Sample Conga template
    ├── sample_query.txt    # Sample SOQL query
    └── sample_schema.json  # Sample JSON schema
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure Box API credentials:
   - Create a `.streamlit/secrets.toml` file based on the provided example
   - Add your Box developer token

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```
2. Upload your Conga template, SOQL query, and JSON schema
3. Click "Convert Template" to process the files
4. Download the CSV mapping or ZIP file with all results

## Deployment to Streamlit Cloud

1. Push the code to a GitHub repository
2. Create a new app in Streamlit Cloud pointing to your repository
3. Configure Box API credentials in Streamlit Cloud secrets
4. Deploy the app

## Limitations

- This is a proof of concept and may not handle complex templates
- The conversion is based on AI analysis and may require manual verification
- Only simple templates are supported in this version

## Future Enhancements

- Batch processing for multiple templates
- Advanced template handling for complex structures
- Interactive field mapping interface
- Template validation and preview
- Enhanced error recovery mechanisms

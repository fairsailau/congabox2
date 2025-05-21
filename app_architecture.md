# Conga to Box Doc Gen Converter - App Architecture

## Overview
This Streamlit application will convert Conga templates to Box Doc Gen format using the Box AI API. The application will be a simple POC that allows users to upload Conga templates and related files, process them through the Box AI API, and download the results as a CSV mapping file and a zip archive.

## Components

### 1. User Interface (UI)
- **File Upload Section**
  - Upload Conga template (DOCX file)
  - Upload Conga SOQL query (text file)
  - Upload Box-Salesforce JSON schema (JSON file)
- **Processing Controls**
  - Convert button
  - Status indicators
- **Results Section**
  - Preview of conversion mapping
  - Download buttons for CSV and ZIP outputs

### 2. Backend Components
- **File Processors**
  - `DocxParser`: Extracts text and merge fields from Conga templates
  - `QueryParser`: Parses SOQL queries to understand data structure
  - `SchemaParser`: Processes JSON schema to identify field mappings
- **Conversion Engine**
  - `PromptBuilder`: Creates prompts for Box AI API
  - `BoxAIClient`: Handles communication with Box AI API
  - `ResponseParser`: Processes AI responses
- **Output Generators**
  - `MappingGenerator`: Creates CSV mapping between Conga and Box formats
  - `ZipExporter`: Packages all outputs into a downloadable ZIP file
- **Error Handling**
  - `ErrorLogger`: Records and displays detailed error information

## Data Flow
1. User uploads Conga template, SOQL query, and JSON schema
2. System parses the uploaded files to extract relevant information
3. System builds a prompt for the Box AI API
4. System sends the prompt to Box AI API
5. System processes the API response
6. System generates a CSV mapping file
7. System packages all outputs into a ZIP file
8. User downloads the results

## File Structure
```
conga_to_box_converter/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Dependencies
├── .streamlit/             # Streamlit configuration
│   └── secrets.toml        # Box API credentials (not in repo)
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── docx_parser.py      # DOCX parsing utilities
│   ├── query_parser.py     # SOQL query parsing utilities
│   ├── schema_parser.py    # JSON schema parsing utilities
│   ├── prompt_builder.py   # Box AI prompt construction
│   ├── box_ai_client.py    # Box AI API client
│   ├── response_parser.py  # AI response processing
│   ├── mapping_generator.py # CSV mapping generation
│   ├── zip_exporter.py     # ZIP file creation
│   └── error_logger.py     # Error logging utilities
└── sample_data/            # Sample files for testing (not in repo)
    ├── sample_template.docx
    ├── sample_query.txt
    └── sample_schema.json
```

## Authentication
- Box API credentials will be stored in Streamlit secrets
- The application will use a developer token for authentication
- Secrets will be configured in the Streamlit Cloud dashboard

## Error Handling
- Detailed error logs will be displayed in the UI
- Errors will be categorized by type (parsing, API, conversion)
- Each error will include context information for debugging

## Limitations for POC
- Handles only simple templates
- Processes one template at a time
- Limited error recovery
- Basic UI without advanced features

## Future Enhancements (Post-POC)
- Batch processing
- Advanced template handling
- Interactive field mapping
- Template validation
- Enhanced UI/UX

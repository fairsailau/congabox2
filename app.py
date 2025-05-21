"""
Streamlit app for converting Conga templates to Box Doc Gen format.
"""
import os
import tempfile
import streamlit as st
import pandas as pd
from datetime import datetime

# Import utility modules with relative imports
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.docx_parser import DocxParser
from utils.query_parser import QueryParser
from utils.schema_parser import SchemaParser
from utils.prompt_builder import PromptBuilder
from utils.box_client import BoxClient
from utils.response_parser import ResponseParser
from utils.mapping_generator import MappingGenerator
from utils.zip_exporter import ZipExporter
from utils.error_logger import ErrorLogger

# Set page configuration
st.set_page_config(
    page_title="Conga to Box Doc Gen Converter",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.conversion_complete = False
    st.session_state.mappings = []
    st.session_state.errors = []
    st.session_state.temp_dir = tempfile.mkdtemp()
    st.session_state.output_files = {}
    st.session_state.box_file_ids = []

# Initialize error logger
error_logger = ErrorLogger()

# Create temp directory for output files
os.makedirs(st.session_state.temp_dir, exist_ok=True)

# App title and description
st.title("Conga to Box Doc Gen Converter")
st.markdown("""
This application converts Conga templates to Box Doc Gen format using the Box AI API.
Upload your Conga template, SOQL query, and JSON schema to get started.
""")

# Sidebar for Box API credentials
st.sidebar.header("Box API Configuration")

# Use Streamlit secrets for Box API credentials
if 'box' in st.secrets:
    developer_token = st.secrets['box']['developer_token']
    st.sidebar.success("✅ Box API credentials loaded from secrets")
else:
    developer_token = st.sidebar.text_input("Box Developer Token", type="password")
    st.sidebar.warning("⚠️ Box API credentials not found in secrets")

# Validate Box API token
if developer_token:
    try:
        box_client = BoxClient(developer_token)
        if box_client.validate_token():
            st.sidebar.success("✅ Box API token validated")
        else:
            st.sidebar.error("❌ Invalid Box API token")
    except Exception as e:
        st.sidebar.error(f"❌ Error validating Box API token: {str(e)}")

# File upload section
st.header("Upload Files")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Conga Template")
    template_file = st.file_uploader("Upload Conga template (DOCX)", type=["docx"])

with col2:
    st.subheader("SOQL Query")
    query_file = st.file_uploader("Upload SOQL query (TXT)", type=["txt"])
    query_text = st.text_area("Or paste SOQL query here", height=100)

with col3:
    st.subheader("JSON Schema")
    schema_file = st.file_uploader("Upload Box-Salesforce JSON schema", type=["json"])

# Conversion section
st.header("Conversion")

if st.button("Convert Template", disabled=not (template_file and (query_file or query_text) and schema_file)):
    with st.spinner("Converting template..."):
        try:
            # Reset previous results
            st.session_state.conversion_complete = False
            st.session_state.mappings = []
            st.session_state.errors = []
            st.session_state.output_files = {}
            st.session_state.box_file_ids = []
            
            # Initialize Box client
            box_client = BoxClient(developer_token)
            
            # Step 1: Upload files to Box
            st.info("Uploading files to Box...")
            
            # Upload template file
            template_file.seek(0)
            template_response = box_client.upload_file(
                template_file, 
                f"conga_template_{datetime.now().strftime('%Y%m%d%H%M%S')}.docx"
            )
            template_file_id = template_response.get('entries', [{}])[0].get('id')
            st.session_state.box_file_ids.append(template_file_id)
            
            # Upload or create query file
            if query_file:
                query_file.seek(0)
                query_response = box_client.upload_file(
                    query_file,
                    f"soql_query_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
                )
                query_file_id = query_response.get('entries', [{}])[0].get('id')
            else:
                # Create temporary file for query text
                query_path = os.path.join(st.session_state.temp_dir, "query.txt")
                with open(query_path, "w") as f:
                    f.write(query_text)
                query_response = box_client.upload_file(
                    query_path,
                    f"soql_query_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
                )
                query_file_id = query_response.get('entries', [{}])[0].get('id')
            st.session_state.box_file_ids.append(query_file_id)
            
            # Upload schema file
            schema_file.seek(0)
            schema_response = box_client.upload_file(
                schema_file,
                f"schema_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            )
            schema_file_id = schema_response.get('entries', [{}])[0].get('id')
            st.session_state.box_file_ids.append(schema_file_id)
            
            # Step 2: Build prompt
            st.info("Building prompt for Box AI...")
            prompt_builder = PromptBuilder()
            prompt = prompt_builder.build_conversion_prompt()
            
            # Step 3: Call Box AI API with file references
            st.info("Calling Box AI API with file references...")
            response = box_client.generate_text(
                prompt=prompt,
                file_ids=[template_file_id, query_file_id, schema_file_id]
            )
            
            # Step 4: Parse response
            st.info("Parsing AI response...")
            response_parser = ResponseParser()
            mappings = response_parser.parse_mapping_response(response.get('text', ''))
            
            # Step 5: Generate CSV mapping
            st.info("Generating CSV mapping...")
            mapping_generator = MappingGenerator()
            csv_path = os.path.join(st.session_state.temp_dir, "conga_to_box_mapping.csv")
            mapping_generator.generate_csv_mapping(mappings, csv_path)
            
            # Step 6: Create ZIP file with original files and mapping
            st.info("Creating ZIP file...")
            zip_exporter = ZipExporter()
            zip_path = os.path.join(st.session_state.temp_dir, "conga_to_box_conversion.zip")
            
            files_to_zip = {
                "conga_to_box_mapping.csv": csv_path
            }
            
            # Save original files to include in ZIP
            template_path = os.path.join(st.session_state.temp_dir, "original_template.docx")
            with open(template_path, "wb") as f:
                template_file.seek(0)
                f.write(template_file.read())
            files_to_zip["original_template.docx"] = template_path
            
            if query_file:
                query_path = os.path.join(st.session_state.temp_dir, "original_query.txt")
                with open(query_path, "wb") as f:
                    query_file.seek(0)
                    f.write(query_file.read())
            else:
                query_path = os.path.join(st.session_state.temp_dir, "original_query.txt")
                with open(query_path, "w") as f:
                    f.write(query_text)
            files_to_zip["original_query.txt"] = query_path
            
            schema_path = os.path.join(st.session_state.temp_dir, "original_schema.json")
            with open(schema_path, "wb") as f:
                schema_file.seek(0)
                f.write(schema_file.read())
            files_to_zip["original_schema.json"] = schema_path
            
            # Create README
            readme_content = f"""
Conga to Box Doc Gen Conversion
===============================
Conversion Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This ZIP file contains the following:
- conga_to_box_mapping.csv: Mapping between Conga merge fields and Box Doc Gen fields
- original_template.docx: Original Conga template
- original_query.txt: Original SOQL query
- original_schema.json: Original Box-Salesforce JSON schema

The mapping CSV file can be used as a reference for manually converting your Conga template to Box Doc Gen format.
"""
            
            zip_exporter.create_zip(files_to_zip, zip_path)
            zip_exporter.add_readme_to_zip(zip_path, readme_content)
            
            # Store results in session state
            st.session_state.conversion_complete = True
            st.session_state.mappings = mappings
            st.session_state.output_files = {
                "csv": csv_path,
                "zip": zip_path
            }
            
            st.success("Conversion complete!")
            
        except Exception as e:
            error_info = error_logger.log_error(
                "conversion", 
                f"Error during conversion: {str(e)}", 
                {"exception": e}
            )
            st.session_state.errors.append(error_info)
            st.error(f"Error during conversion: {str(e)}")

# Results section
if st.session_state.conversion_complete:
    st.header("Conversion Results")
    
    # Display mapping table
    st.subheader("Field Mappings")
    if st.session_state.mappings:
        mapping_df = pd.DataFrame(st.session_state.mappings)
        st.dataframe(mapping_df)
    else:
        st.warning("No mappings generated.")
    
    # Download buttons
    st.subheader("Download Results")
    col1, col2 = st.columns(2)
    
    with col1:
        if "csv" in st.session_state.output_files:
            with open(st.session_state.output_files["csv"], "rb") as f:
                csv_data = f.read()
            st.download_button(
                label="Download CSV Mapping",
                data=csv_data,
                file_name="conga_to_box_mapping.csv",
                mime="text/csv"
            )
    
    with col2:
        if "zip" in st.session_state.output_files:
            with open(st.session_state.output_files["zip"], "rb") as f:
                zip_data = f.read()
            st.download_button(
                label="Download All Files (ZIP)",
                data=zip_data,
                file_name="conga_to_box_conversion.zip",
                mime="application/zip"
            )

# Error log section
if st.session_state.errors:
    st.header("Error Log")
    for i, error in enumerate(st.session_state.errors, 1):
        with st.expander(f"Error {i}: {error.get('message', 'Unknown error')}"):
            st.write(f"**Type:** {error.get('type', 'unknown')}")
            st.write(f"**Timestamp:** {error.get('timestamp', '')}")
            
            context = error.get('context', {})
            if context:
                st.subheader("Context")
                for key, value in context.items():
                    if key != 'traceback' and key != 'exception':
                        st.write(f"**{key}:** {value}")
                
                if 'traceback' in context:
                    with st.expander("Show Traceback"):
                        st.code(context['traceback'])

# Help section
with st.sidebar.expander("Help & Information"):
    st.markdown("""
    ### How to Use This App
    
    1. **Upload Files**:
       - Upload your Conga template (DOCX file)
       - Upload or paste your SOQL query
       - Upload your Box-Salesforce JSON schema
    
    2. **Convert**:
       - Click the "Convert Template" button
       - Wait for the conversion process to complete
    
    3. **Download Results**:
       - Download the CSV mapping file
       - Or download all files as a ZIP archive
    
    ### About
    
    This app uses Box AI API to convert Conga templates to Box Doc Gen format.
    It uploads your files to Box and uses file references with the Box AI API for processing.
    
    ### Limitations
    
    - This is a proof of concept and may not handle complex templates
    - The conversion is based on AI analysis and may require manual verification
    - Only simple templates are supported in this version
    """)

# Footer
st.markdown("---")
st.markdown("Conga to Box Doc Gen Converter | Proof of Concept")

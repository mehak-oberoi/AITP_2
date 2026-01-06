import streamlit as st
import os
import tempfile
from markitdown import MarkItDown

# --- Page Configuration ---
st.set_page_config(
    page_title="Universal Document Reader",
    page_icon="📄",
    layout="wide"
)

# --- Logic & Helper Functions ---
def get_converted_filename(original_filename):
    """
    Generates the output filename.
    Example: Project_Notes.docx -> Project_Notes_converted.md
    """
    name, _ = os.path.splitext(original_filename)
    return f"{name}_converted.md"

def process_file(uploaded_file):
    """
    Handles the saving of the uploaded file to a temp path, 
    processing it with MarkItDown, and cleaning up.
    """
    # Create a temporary file to save the uploaded content
    # We use delete=False to close the file so MarkItDown can open it safely
    # suffix is added so the library detects extension correctly
    suffix = os.path.splitext(uploaded_file.name)[1]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    text_content = None
    error_message = None

    try:
        # Initialize the Engine
        # Note: MarkItDown handles file reading natively.
        # For internal web requests (e.g. if parsing a URL or HTML with links),
        # standard libraries often use default headers. 
        # Here we rely on the library's internal handling but wrap in robust error catching.
        md = MarkItDown()
        
        # Convert
        result = md.convert(tmp_file_path)
        
        # Extract text content
        if result and result.text_content:
            text_content = result.text_content
        else:
            # Fallback if text_content is empty but no error raised
            text_content = ""

    except Exception as e:
        # Generic catch-all for resilience
        # This handles timeouts, format errors, or corruption
        error_message = f"⚠️ Could not read {uploaded_file.name}. Please check the format."
        # Optional: Print actual error to console for developer debugging
        print(f"Error processing {uploaded_file.name}: {e}")

    finally:
        # Cleanup: Remove the temp file from disk
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

    return text_content, error_message

# --- User Interface ---

st.title("📄 Universal Document Reader")
st.markdown("""
**Convert your documents into clean, readable Markdown instantly.** *Supported Formats: Word, Excel, PowerPoint, PDF, HTML.*
""")

st.divider()

# [2] Upload Area
uploaded_files = st.file_uploader(
    "Drag and drop your files here", 
    accept_multiple_files=True,
    type=['docx', 'xlsx', 'pptx', 'pdf', 'html', 'htm']
)

# Process files if uploaded
if uploaded_files:
    st.write(f"### Processing {len(uploaded_files)} file(s)...")
    
    for uploaded_file in uploaded_files:
        with st.expander(f"📄 {uploaded_file.name}", expanded=True):
            
            # Processing with a spinner for feedback
            with st.spinner(f"Reading {uploaded_file.name}..."):
                content, error = process_file(uploaded_file)

            # [3] Error Handling / Resilience
            if error:
                st.error(error)
            else:
                # Calculate new filename
                new_filename = get_converted_filename(uploaded_file.name)
                
                # [2] Download Options
                col1, col2 = st.columns([1, 1])
                
                # Prepare data for download
                # We encode to utf-8 to ensure special characters (emojis, accents) works
                file_data = content.encode('utf-8')

                with col1:
                    st.download_button(
                        label="⬇️ Download as Markdown (.md)",
                        data=file_data,
                        file_name=new_filename,
                        mime="text/markdown"
                    )
                with col2:
                    st.download_button(
                        label="⬇️ Download as Text (.txt)",
                        data=file_data,
                        file_name=new_filename.replace(".md", ".txt"),
                        mime="text/plain"
                    )

                # [2] Instant Preview (Scrollable)
                st.markdown("#### Preview")
                st.text_area(
                    label="Content Preview",
                    value=content,
                    height=300,
                    key=f"preview_{uploaded_file.name}"
                )

st.divider()
st.caption("Powered by Streamlit and MarkItDown.")

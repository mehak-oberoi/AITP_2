import streamlit as st
import os
import tempfile
import pandas as pd
from markitdown import MarkItDown

# ---------------------------------------------------------
# [1] Configuration & Setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="Universal Document Reader",
    page_icon="📄",
    layout="wide"
)

# Initialize the Engine
md = MarkItDown()

# ---------------------------------------------------------
# [2] Helper Functions
# ---------------------------------------------------------
def save_uploaded_file(uploaded_file):
    """
    Saves the uploaded Streamlit object to a temporary file on disk.
    """
    try:
        file_extension = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        return None

def convert_file(file_path):
    """
    Uses MarkItDown to convert the file at the given path to Markdown text.
    """
    try:
        result = md.convert(file_path)
        return result.text_content
    except Exception as e:
        raise e

def format_size(size_in_bytes):
    """
    Converts bytes to a readable string (e.g., 1024 -> 1.00 KB).
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} TB"

# ---------------------------------------------------------
# [3] UI & Main Application Logic
# ---------------------------------------------------------
st.title("📄 Universal Document Reader")
st.markdown("Convert **Word, Excel, PowerPoint, PDF, and HTML** files into clean Markdown text instantly.")

# -- Upload Area --
uploaded_files = st.file_uploader(
    "Drag and drop your files here", 
    accept_multiple_files=True,
    type=['docx', 'xlsx', 'pptx', 'pdf', 'html', 'htm']
)

if uploaded_files:
    st.divider()
    
    for uploaded_file in uploaded_files:
        st.subheader(f"📂 {uploaded_file.name}")
        
        # 1. Save to temp file
        temp_path = save_uploaded_file(uploaded_file)
        
        if temp_path:
            try:
                # 2. Process the file
                with st.spinner(f"Reading {uploaded_file.name}..."):
                    converted_text = convert_file(temp_path)

                # 3. Create Tabs for Preview and Analysis
                tab_preview, tab_stats = st.tabs(["📄 Content Preview", "📊 File Size Comparison"])

                # --- Tab 1: Content Preview ---
                with tab_preview:
                    st.text_area(
                        label="Markdown Output:",
                        value=converted_text,
                        height=300,
                        key=f"preview_{uploaded_file.name}"
                    )

                # --- Tab 2: File Size Comparison ---
                with tab_stats:
                    # Calculate sizes
                    original_size = uploaded_file.size
                    # len() gives characters; encode to utf-8 to get actual byte size
                    converted_size = len(converted_text.encode('utf-8'))
                    
                    # Avoid division by zero
                    if original_size > 0:
                        reduction = ((original_size - converted_size) / original_size) * 100
                    else:
                        reduction = 0

                    # Create Data for the Table
                    data = {
                        "Metric": ["Original File Size", "Converted (.txt) Size"],
                        "Value": [format_size(original_size), format_size(converted_size)]
                    }
                    df = pd.DataFrame(data)

                    # Display Table
                    st.table(df)

                    # Display Percentage Message
                    if reduction > 0:
                        st.success(f"**Optimization:** Text version is **{reduction:.1f}%

import streamlit as st
import requests
from datetime import datetime

streamlit = "cool"
theming = "fantastic"
both = "💥"

# Backend API URL
backend_url = 'http://127.0.0.1:8000'

st.set_page_config(page_title='Churn prediction', page_icon=':file_folder:', layout='centered')

# CSS for gradient background
bg_css = """
<style>
a.link-button {
    display: block;
    padding: 10px;
    margin: 5px 0;
    color: black;
    text-align: center;
    border: 2px solid #F11111;
    border-radius: 5px;
    text-decoration: none;
    background-color: transparent;
}
a.link-button:hover {
    background-color: #F11111;
}
</style>
"""

# Apply CSS
st.markdown(bg_css, unsafe_allow_html=True)

st.title('Churn prediction')
st.write('Upload a CSV file to process it with the model and download the results')

# File upload
uploaded_file = st.file_uploader('Choose a CSV file below', type='csv')

if uploaded_file is not None:
    # Save uploaded file to a temporary location
    with open(uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.getbuffer())

    st.write('File uploaded successfully!')

    # Send file to backend for processing
    files = {'file': (uploaded_file.name, open(uploaded_file.name, 'rb'), 'text/csv')}
    response = requests.post(f'{backend_url}/upload', files=files)

    if response.status_code == 200:
        st.success('File processed successfully!')
    else:
        st.error('Error processing file')

# File download
st.write('## Available files for download')
response = requests.get(f'{backend_url}/download')

if response.status_code == 200:
    files = response.json().get('files', [])
    # Group files by date
    files_by_date = {}
    for file in files:
        # Extract date from filename
        date_str = file.split('_')[2].replace('.csv', '')
        date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        date_key = date_obj.date()
        
        if date_key not in files_by_date:
            files_by_date[date_key] = []
        files_by_date[date_key].append(file)
    
    if files_by_date:
        # Create a selectbox for dates
        selected_date = st.selectbox('Select a date', list(files_by_date.keys()))

        if selected_date:
            st.write(f'### Files for {selected_date}:')
            with st.expander(f"Files for {selected_date}", expanded=True):
                for file in files_by_date[selected_date]:
                    file_url = f'{backend_url}/download/{file}'
                    st.markdown(f'<a href="{file_url}" download class="link-button">{file}</a>', unsafe_allow_html=True)
    else:
        st.write('No files available')
else:
    st.error('Error fetching files')

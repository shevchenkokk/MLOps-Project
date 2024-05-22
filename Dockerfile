# Select base image for the project
FROM python:3.12

# Choose what directory should be a working directory
# If the directory does not exist then Docker will create it
WORKDIR /app

# Copy project files into working directory
COPY /app /app

# Copy our local file with requirements into Docker Image
COPY requirements.txt ./

# Install all the requirements
RUN pip install --no-cache-dir -r requirements.txt

# Open port for Streamlit
EXPOSE 8501

# Open port for FastAPI
EXPOSE 8000

# Run Uvicorn & StreamLit
CMD uvicorn app:app --host 0.0.0.0 --port 8000 & streamlit run frontend/frontend.py --server.port 8501 --server.address 0.0.0.0
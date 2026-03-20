import os
from azure.storage.blob import BlobServiceClient
import pandas as pd
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

@st.cache_data(ttl=60)
def load_csv_from_blob():
    """Descarga CSV desde Azure Blob Storage"""
    
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    container_name = os.getenv('CONTAINER_NAME')
    blob_name = os.getenv('BLOB_NAME')
    
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        
        blob_data = blob_client.download_blob()
        csv_string = blob_data.readall().decode('utf-8')
        
        from io import StringIO
        df = pd.read_csv(StringIO(csv_string))
        
        df['fecha_procesamiento'] = pd.to_datetime(df['fecha_procesamiento'])
        
        return df
        
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return None
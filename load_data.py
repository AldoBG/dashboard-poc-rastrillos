import streamlit as st
from azure.storage.blob import BlobServiceClient
import pandas as pd
from io import StringIO

@st.cache_data(ttl=60)
def load_csv_from_blob():
    """Descarga CSV desde Azure Blob Storage"""
    
    try:
        # En Streamlit Cloud usar st.secrets
        connection_string = st.secrets["AZURE_STORAGE_CONNECTION_STRING"]
        container_name = st.secrets["CONTAINER_NAME"]
        blob_name = st.secrets["BLOB_NAME"]
        
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        
        blob_data = blob_client.download_blob()
        csv_string = blob_data.readall().decode('utf-8')
        
        df = pd.read_csv(StringIO(csv_string))
        df['fecha_procesamiento'] = pd.to_datetime(df['fecha_procesamiento'])
        
        return df
        
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return None
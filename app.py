import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from load_data import load_csv_from_blob

st.set_page_config(
    page_title="PoC Rastrillos - Dashboard",
    page_icon="🪒",
    layout="wide"
)

st.title("🪒 PoC Análisis de Exhibidores - Rastrillos")
st.markdown("**Detección automática de marcas en punto de venta**")
st.markdown("---")

# Cargar datos
df = load_csv_from_blob()

if df is None or df.empty:
    st.warning("⚠️ No hay datos disponibles. Sube imágenes para comenzar el análisis.")
    st.stop()

# Métricas generales
col1, col2 = st.columns(2)
with col1:
    st.metric("📸 Imágenes Procesadas", len(df))
with col2:
    total_detecciones = df[['prestobarba_2h', 'prestobarba_3h', 'bic', 'schick', 'generico']].sum().sum()
    st.metric("🪒 Total Detecciones", int(total_detecciones))

st.markdown("---")

# KPI 1: PRESENCIA POR MARCA
st.header("📊 KPI 1: Presencia de Marcas")

marcas_data = {
    'Prestobarba 2 hojas': df['prestobarba_2h'].sum(),
    'Prestobarba 3 hojas': df['prestobarba_3h'].sum(),
    'BIC': df['bic'].sum(),
    'Schick': df['schick'].sum(),
    'Genérico': df['generico'].sum()
}

df_presencia = pd.DataFrame({
    'Marca': list(marcas_data.keys()),
    'Exhibidores': list(marcas_data.values())
})

df_presencia['% Presencia'] = (df_presencia['Exhibidores'] / len(df) * 100).round(1)

col1, col2 = st.columns([2, 1])

with col1:
    fig_presencia = px.bar(
        df_presencia,
        x='Marca',
        y='Exhibidores',
        title='Presencia de Marcas en Exhibidores Analizados',
        text='% Presencia',
        color='Marca',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_presencia.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_presencia.update_layout(showlegend=False, yaxis_title="Número de Exhibidores")
    st.plotly_chart(fig_presencia, use_container_width=True)

with col2:
    st.subheader("Resumen")
    st.dataframe(
        df_presencia[['Marca', 'Exhibidores', '% Presencia']], 
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")

# KPI 2: SHARE OF SHELF
st.header("📈 KPI 2: Share of Shelf")

total_presencias = df_presencia['Exhibidores'].sum()

if total_presencias > 0:
    df_share = df_presencia.copy()
    df_share['% Share'] = (df_share['Exhibidores'] / total_presencias * 100).round(1)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_share = px.pie(
            df_share,
            values='Exhibidores',
            names='Marca',
            title='Distribución de Presencia en Exhibidores',
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.4
        )
        fig_share.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_share, use_container_width=True)
    
    with col2:
        st.subheader("Share of Shelf")
        st.dataframe(
            df_share[['Marca', '% Share']],
            use_container_width=True,
            hide_index=True
        )
else:
    st.info("No hay detecciones para calcular share of shelf")

st.markdown("---")

# TIMELINE
st.header("📅 Análisis Temporal")

df_timeline = df.copy()
df_timeline['Fecha'] = df_timeline['fecha_procesamiento'].dt.date

detecciones_por_dia = df_timeline.groupby('Fecha').size().reset_index(name='Imágenes')

fig_timeline = px.line(
    detecciones_por_dia,
    x='Fecha',
    y='Imágenes',
    title='Imágenes Procesadas por Día',
    markers=True
)
st.plotly_chart(fig_timeline, use_container_width=True)

st.markdown("---")

# TABLA DE DATOS
st.header("📋 Detalle de Análisis")

# Seleccionar solo columnas relevantes
cols_display = ['nombre_imagen', 'fecha_procesamiento', 'prestobarba_2h', 'prestobarba_3h', 
                'bic', 'schick', 'generico']

df_display = df[cols_display].copy()
df_display['fecha_procesamiento'] = df_display['fecha_procesamiento'].dt.strftime('%Y-%m-%d %H:%M')

# Renombrar columnas para mejor visualización
df_display.columns = ['Imagen', 'Fecha', 'Prestobarba 2h', 'Prestobarba 3h', 'BIC', 'Schick', 'Genérico']

st.dataframe(df_display, use_container_width=True, hide_index=True)

# Botón de recarga
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🔄 Recargar Datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Footer
st.markdown("---")
st.caption("PoC - Detección de Marcas en Exhibidores | Custom Vision + Logic Apps + Azure Functions")
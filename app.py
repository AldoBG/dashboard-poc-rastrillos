from load_data import load_csv_from_blob
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 

st.set_page_config(
    page_title="PoC Rastrillos - Dashboard",
    page_icon="🪒",
    layout="wide"
)

st.title("🪒 PoC Análisis de Exhibidores - Rastrillos")
st.markdown("---")

# Cargar datos
df = load_csv_from_blob()

if df is None or df.empty:
    st.warning("No hay datos disponibles. Procesa algunas imágenes primero.")
    st.stop()

# Métricas generales
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📸 Imágenes procesadas", len(df))
with col2:
    avg_price = df[df['precio_promedio'] > 0]['precio_promedio'].mean()
    st.metric("💰 Precio promedio", f"${avg_price:.2f}" if not pd.isna(avg_price) else "N/A")
with col3:
    if len(df) > 0:
        promo_pct = (df['tiene_promocion'].sum() / len(df)) * 100
        st.metric("🎁 % con promociones", f"{promo_pct:.1f}%")

st.markdown("---")

# KPI 1: PRESENCIA POR MARCA
st.header("📊 KPI 1: Presencia por Marca")

marcas_data = {
    'Prestobarba 2h': df['prestobarba_2h'].sum(),
    'Prestobarba 3h': df['prestobarba_3h'].sum(),
    'BIC': df['bic'].sum(),
    'Schick': df['schick'].sum(),
    'Genérico': df['generico'].sum()
}

df_presencia = pd.DataFrame({
    'Marca': list(marcas_data.keys()),
    'Presencia': list(marcas_data.values())
})

df_presencia['%'] = (df_presencia['Presencia'] / len(df) * 100).round(1)

fig_presencia = px.bar(
    df_presencia,
    x='Marca',
    y='Presencia',
    title='Presencia de Marcas en Exhibidores',
    text='%',
    color='Marca'
)
fig_presencia.update_traces(texttemplate='%{text}%', textposition='outside')
st.plotly_chart(fig_presencia, use_container_width=True)

st.markdown("---")

# KPI 2: PROMOCIONES
st.header("🎁 KPI 2: Presencia de Promociones")

col1, col2 = st.columns([1, 2])

with col1:
    promo_counts = df['tiene_promocion'].value_counts()
    fig_promo = go.Figure(data=[go.Pie(
        labels=['Con promoción', 'Sin promoción'],
        values=[
            promo_counts.get(True, 0),
            promo_counts.get(False, 0)
        ],
        hole=.3
    )])
    fig_promo.update_layout(title='% de Exhibidores con Promociones')
    st.plotly_chart(fig_promo, use_container_width=True)

with col2:
    df_promo = df[df['tiene_promocion'] == True][
        ['nombre_imagen', 'texto_promocion']
    ]
    st.subheader("Promociones Detectadas")
    if not df_promo.empty:
        st.dataframe(df_promo, use_container_width=True)
    else:
        st.info("No se detectaron promociones")

st.markdown("---")

# KPI 3: PRECIOS (si existen)
if df['precio_promedio'].sum() > 0:
    st.header("💰 KPI 3: Análisis de Precios")
    
    df_precios = df[df['precio_promedio'] > 0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Precio Promedio", f"${df_precios['precio_promedio'].mean():.2f}")
    with col2:
        st.metric("Precio Mínimo", f"${df_precios['precio_minimo'].min():.2f}")
    with col3:
        st.metric("Precio Máximo", f"${df_precios['precio_maximo'].max():.2f}")
    
    st.markdown("---")

# TABLA DE DATOS
st.header("📋 Datos Completos")
st.dataframe(df, use_container_width=True)

# Botón de recarga
if st.button("🔄 Recargar datos"):
    st.cache_data.clear()
    st.rerun()
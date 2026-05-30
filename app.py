import streamlit as st
import pandas as pd

st.set_page_config(page_title="Analytics de Potencia Critica", layout="wide")

@st.cache_data
def cargar_datos_ejemplo():
    # Aquí cambiamos los nombres reales por etiquetas anónimas (A, B, C, D)
    data = {
        'athlete_id': ['USR-001', 'USR-002', 'USR-003', 'USR-004'],
        'nombre': ['Atleta A (Perfil Fondista)', 'Atleta B (Perfil Sprinter)', 'Atleta C (Perfil Potencia Alta)', 'Atleta D (Perfil Amateur)'],
        'CP_W': [360, 280, 410, 210],
        'W_prime_J': [18000, 25000, 15000, 12000]
    }
    return pd.DataFrame(data)

resultados_df = cargar_datos_ejemplo()

st.sidebar.header("Panel de Control")
if 'athlete_id' in resultados_df.columns:
    lista_atletas = resultados_df['athlete_id'].unique()
    atleta_seleccionado = st.sidebar.selectbox("Selecciona el ID del Atleta:", lista_atletas)
else:
    atleta_seleccionado = None

st.title("Simulador de Perfil Metabolico y Potencia Critica")

if atleta_seleccionado:
    filtro_atleta = resultados_df[resultados_df['athlete_id'] == atleta_seleccionado]
    if not filtro_atleta.empty:
        atleta_data = filtro_atleta.iloc[0]
        cp_atleta = atleta_data['CP_W']
        w_prime_atleta = atleta_data['W_prime_J']
        nombre_atleta = atleta_data.get('nombre', 'Desconocido')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Sujeto de Prueba", value=str(atleta_seleccionado), delta=nombre_atleta)
        with col2:
            st.metric(label="Potencia Critica (CP)", value=f"{cp_atleta} W")
        with col3:
            st.metric(label="Capacidad Anaerobica (W')", value=f"{w_prime_atleta} J")
            
        st.markdown("---")
        st.subheader("Reporte e Interpretacion Fisiologica")
        
        interpretacion_texto = f"""
Los parametros obtenidos mediante el analisis de datos nos permiten cuantificar la capacidad bioenergetica del atleta basandonos en el modelo de Potencia Critica. Este modelo divide el rendimiento en dos componentes diferenciados: la **Potencia Critica ($CP$)**, establecida en **{cp_atleta} W**, y la **Capacidad de Trabajo Anaerobico ($W'$)**, cuantificada en **{w_prime_atleta} J**.

La **Potencia Critica ($CP$)** representa el umbral metabolico superior en estado estable. Fisiologicamente, delimita la transicion entre el dominio de intensidad alta y el dominio de intensidad severa. Una $CP$ de {cp_atleta} W es el reflejo directo de la eficiencia de su sistema aerobico.

Por otro lado, la **Capacidad de Trabajo Anaerobico ($W'$)** de {w_prime_atleta} J representa la cantidad finita de energia disponible para realizar trabajo por encima de la $CP$. Cuando el sujeto supera la barrera de sus {cp_atleta} W, entra en el dominio de intensidad severa, iniciando una cuenta atras metabólica donde el almacenamiento de {w_prime_atleta} J comienza a vaciarse.
"""
        st.info(interpretacion_texto)

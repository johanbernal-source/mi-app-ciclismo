import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Analytics de Potencia Critica", layout="wide")

@st.cache_data
def cargar_datos_ejemplo():
    data = {
        'athlete_id': ['USR-001', 'USR-002', 'USR-003', 'USR-004'],
        'nombre': ['Atleta A (Perfil Fondista)', 'Atleta B (Perfil Sprinter)', 
                   'Atleta C (Perfil Potencia Alta)', 'Atleta D (Perfil Amateur)'],
        'CP_W': [360, 280, 410, 210],
        'W_prime_J': [18000, 25000, 15000, 12000]
    }
    return pd.DataFrame(data)

resultados_df = cargar_datos_ejemplo()

# --- CÁLCULOS DE PORCENTAJES INICIALES ---
cp_maximo = resultados_df['CP_W'].max()
resultados_df['Porcentaje_Respecto_Max'] = (resultados_df['CP_W'] / cp_maximo) * 100

st.sidebar.header("Panel de Control")
if 'athlete_id' in resultados_df.columns:
    lista_atletas = resultados_df['athlete_id'].unique()
    atleta_seleccionado = st.sidebar.selectbox("Selecciona el ID del Atleta:", lista_atletas)
else:
    atleta_seleccionado = None

st.title("Simulador de Perfil Metabolico y Potencia Critica")

# --- GRÁFICA COMPARATIVA GENERAL DE LA CLASE ---
st.subheader("📊 Comparativa General de los Sujetos de Prueba")
df_grafica = resultados_df.set_index('nombre')[['CP_W']]
st.bar_chart(df_grafica)

if atleta_seleccionado:
    filtro_atleta = resultados_df[resultados_df['athlete_id'] == atleta_seleccionado]
    if not filtro_atleta.empty:
        atleta_data = filtro_atleta.iloc[0]
        cp_atleta = atleta_data['CP_W']
        w_prime_atleta = atleta_data['W_prime_J']
        nombre_atleta = atleta_data.get('nombre', 'Desconocido')
        porcentaje = atleta_data['Porcentaje_Respecto_Max']
        
        # Fila de Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Sujeto de Prueba", value=str(atleta_seleccionado), delta=nombre_atleta)
        with col2:
            st.metric(label="Potencia Critica (CP)", value=f"{cp_atleta} W")
        with col3:
            st.metric(label="Capacidad Anaerobica (W')", value=f"{w_prime_atleta} J")
        with col4:
            st.metric(label="Nivel de Rendimiento", value=f"{porcentaje:.1f}%", delta="vs Máximo del Grupo")
            
        st.markdown("---")
        st.subheader("📈 Bloque de Gráficas de Rendimiento Avanzado")
        
        # Crear pestañas para organizar las múltiples gráficas por persona
        tab1, tab2, tab3 = st.tabs(["1. Curva Potencia-Tiempo", "2. Vaciamiento de Reserva W'", "3. Rebalance Intermitente"])
        
        with tab1:
            st.write("**Curva Hipérbola de Potencia vs Tiempo Límite (Tlim)**")
            st.write("Esta gráfica muestra cuántos segundos puede sostener el atleta una potencia determinada antes de llegar al fallo metabólico.")
            t_rango = np.arange(10, 301, 5) 
            potencias = [cp_atleta + (w_prime_atleta / t) for t in t_rango]
            df_curva = pd.DataFrame({'Tiempo (s)': t_rango, 'Potencia Soportada (W)': potencias})
            df_curva = df_curva.set_index('Tiempo (s)')
            st.line_chart(df_curva)
            
        with tab2:
            st.write("**Simulación de Vaciamiento Lineal de W'**")
            st.write("Disminución continua de los Julios de reserva energética al sostener un esfuerzo de intensidad severa (+100W sobre la CP).")
            tiempo = np.arange(0, 61, 1)
            energia_restante = [max(0, w_prime_atleta - (100 * t)) for t in tiempo]
            df_simulacion = pd.DataFrame({'Tiempo (s)': tiempo, 'Energía Disponible (J)': energia_restante})
            df_simulacion = df_simulacion.set_index('Tiempo (s)')
            st.line_chart(df_simulacion)
            
        with tab3:
            st.write("**Modelo Intermitente W'bal (Vaciamiento y Recuperación)**")
            st.write("Simulación dinámica: El atleta aprieta 20s sobre su CP (gasta energía), luego recupera 20s pedaleando suave por debajo de su CP (el tanque se vuelve a llenar).")
            tiempo_int = np.arange(0, 81, 1)
            reserva_dinamica = []
            actual = w_prime_atleta
            
            for t in tiempo_int:
                if t < 20 or (t >= 40 and t < 60): 
                    actual = max(0, actual - 150)
                else: 
                    actual = min(w_prime_atleta, actual + 70)
                reserva_dinamica.append(actual)
                
            # Aquí corregimos el corte separando la creación del DataFrame de la asignación del índice
            df_intermitente = pd.DataFrame({'Tiempo (s)': tiempo_int, 'Reserva W\' (J)': reserva_dinamica})
            df_intermitente = df_intermitente.set_index('Tiempo (s)')
            st.line_chart(df_intermitente)
        
        st.markdown("---")
        st.subheader("Reporte e Interpretacion Fisiologica")
        
        interpretacion_texto = f"""
Los parametros obtenidos mediante el analisis de datos nos permiten cuantificar la capacidad bioenergetica del atleta basandonos en el modelo de Potencia Critica. Este modelo divide el rendimiento en dos componentes diferenciados: la **Potencia Critica ($CP$)**, establecida en **{cp_atleta} W**, y la **Capacidad de Trabajo Anaerobico ($W'$)**, cuantificada en **{w_prime_atleta} J**.

El sujeto se encuentra al **{porcentaje:.1f}%** de la potencia aeróbica máxima registrada en el grupo de control. Cuando el sujeto supera la barrera de sus {cp_atleta} W, entra en el dominio de intensidad severa, iniciando la cuenta atrás metabólica reflejada en las gráficas superiores.
"""
        st.info(interpretacion_texto)

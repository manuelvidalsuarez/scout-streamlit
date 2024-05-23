import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os


# Nombres de los archivos Excel
files = {
    ('Posición específica', 'Posición específica'): 'Seleccion_especifica_Evaluacion_especifica.xlsx',
    ('Posición específica', 'Posición asociada'): 'Seleccion_especifica_Evaluacion_asociada.xlsx',
    ('Posición asociada', 'Posición específica'): 'Seleccion_asociada_Evaluacion_especifica.xlsx',
    ('Posición asociada', 'Posición asociada'): 'Seleccion_asociada_Evaluacion_asociada.xlsx'
}


text_files = {
    ('Posición específica', 'Posición específica'): 'Seleccion_especifica_Evaluacion_especifica.txt',
    ('Posición específica', 'Posición asociada'): 'Seleccion_especifica_Evaluacion_asociada.txt',
    ('Posición asociada', 'Posición específica'): 'Seleccion_asociada_Evaluacion_especifica.txt',
    ('Posición asociada', 'Posición asociada'): 'Seleccion_asociada_Evaluacion_asociada.txt'
}

# Define el diccionario jugadores_posiciones aquí
jugadores_posiciones = {
    'Laterales': {
        'posicion': 'Lateral',
        'jugadores': ['Alejandro Grimaldo García','Kyle Walker','Daniel Carvajal Ramos', 'Achraf Hakimi Mouh','Trent Alexander-Arnold','Alphonso Davies'],
        'nombre_hoja': 'Lateral'
    },
    'Centrales_Salida': {
        'posicion': 'Central',
        'jugadores': ['Micky van de Ven','Rúben Santos Gato Alves Dias','Gabriel dos Santos Magalhães','Alessandro Bastoni', 'Joško Gvardiol','Mats Hummels'],
        'nombre_hoja': 'Central Salida Balon-Ofensivo'
    },
    'Centrales_Def': {
        'posicion': 'Central',
        'jugadores': ['Virgil van Dijk','William Saliba','Min Jae Kim','Dayotchanculle Upamecano','Ronald Federico Araújo da Silva','Antonio Rüdiger'],
        'nombre_hoja': 'Central Duelos-Seguridad'
    },
    'Pivote': {
        'posicion': 'Pivote',
        'jugadores': ['Declan Rice','Rodrigo Hernández Cascante','Frenkie de Jong','Toni Kroos','Alexis Mac Allister','Vitor Machado Ferreira'],
        'nombre_hoja': 'Pivote'
    },
    'BoxToBox': {
        'posicion': 'BoxToBox',
        'jugadores': ['Federico Santiago Valverde Dipetta','Kevin De Bruyne','Nicolò Barella','Eduardo Camavinga','Bruno Miguel Borges Fernandes','Rodrigo Javier De Paul'],
        'nombre_hoja': 'BoxToBox'
    },
    'MediaPunta': {
        'posicion': 'Mediapunta',
        'jugadores':['Martin Ødegaard','Jude Bellingham','James Maddison','Jamal Musiala','Cole Palmer','Florian Wirtz'],
        'nombre_hoja': 'Mediapunta'
    },
    'Extremos_1vs1_profundos': {
        'posicion': 'Extremo',
        'jugadores':['Ousmane Dembélé','Bukayo Saka','Nicholas Williams Arthuer','Vinícius José Paixão de Oliveira Júnior','Lamine Yamal Nasraoui Ebana','Kaoru Mitoma'],
        'nombre_hoja': 'Extremo Profundo'
    },
    'Extremos_asociativos': {
        'posicion': 'Extremo',
        'jugadores':['Heung-Min Son','Kylian Mbappé Lottin','Phil Foden','Bernardo Mota Veiga de Carvalho e Silva','Takefusa Kubo','Rodrygo Silva de Goes'],
        'nombre_hoja': 'Extremo Asociativo'
    },
    'Delantero_Referencia': {
        'posicion': 'Delantero',
        'jugadores':['Erling Håland','Victor James Osimhen','Dušan Vlahović','Robert Lewandowski','Artem Dovbyk','Viktor Gyökeres'],
        'nombre_hoja': 'Delantero Referencia'
    },
    'Delantero_Asociativo': {
        'posicion': 'Delantero',
        'jugadores':['Harry Kane','Ollie Watkins','Julián Álvarez','Lautaro Javier Martínez','Kai Havertz','Antoine Griezmann'],
        'nombre_hoja': 'Delantero Asociativo'
    },


}

# Function to load data and highlight players
def load_data_with_highlight(file_path, jugadores_posiciones):
    data_frames = {}
    for perfil, info in jugadores_posiciones.items():
        sheet_name = info['nombre_hoja']
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
        df['highlight'] = df['player_name'].apply(lambda x: 'green' if x in info['jugadores'] else 'none')
        df['player_season_minutes'] = pd.to_numeric(df['player_season_minutes'], errors='coerce').round().astype('Int64')
        df['Nota'] = pd.to_numeric(df['Nota'], errors='coerce').round(2)
        df['birth_date'] = pd.to_datetime(df['birth_date'], errors='coerce')
        df['birth_year'] = df['birth_date'].dt.year
        data_frames[sheet_name] = df
    return data_frames

# Carga inicial de datos
@st.cache_data
def load_data(metricas, comparacion):
    file_name = files[(metricas, comparacion)]
    data_frames = load_data_with_highlight(file_name, jugadores_posiciones)
    resumen_general_df = pd.read_excel(file_name, sheet_name='Resumen General', engine='openpyxl')
    if 'birth_date' in resumen_general_df.columns:
        resumen_general_df['birth_date'] = pd.to_datetime(resumen_general_df['birth_date'], errors='coerce')
        resumen_general_df['birth_year'] = resumen_general_df['birth_date'].dt.year
    return data_frames, resumen_general_df

# Function to load technical information from the text file
def load_technical_info(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as file:
            content = file.read()
    return content

# Layout de la aplicación
st.title("Análisis de Jugadores")

# Selección de métricas y comparación
metricas = st.selectbox('Método de selección de métricas relevantes:', ['Posición específica', 'Posición asociada'], index=0)
comparacion = st.selectbox('Tipo de comparación:', ['Posición específica', 'Posición asociada'], index=0)

# Mostrar advertencia si se selecciona "Posición asociada"
if metricas == 'Posición asociada' or comparacion == 'Posición asociada':
    st.warning(
        "Al seleccionar el método de evaluación asociado, ten en cuenta que las notas pueden variar. "
        "Este método compara las métricas destacadas de los jugadores no solo con aquellos de su posición específica, "
        "sino también con jugadores de posiciones asociadas. Esto puede resultar en modificaciones en las notas debido a la comparación más amplia."
    )

# Carga de datos
data_frames, resumen_general_df = load_data(metricas, comparacion)

# Selección de perfil
perfiles_options = list(data_frames.keys())
selected_perfil = st.selectbox('Selecciona el perfil:', perfiles_options)

# Filtro de competición
competition_options = resumen_general_df['competition_name'].unique().tolist()
selected_competitions = st.multiselect('Filtrar por competición:', competition_options, default=competition_options)

# Filtro de minutos jugados
max_minutes = resumen_general_df['player_season_minutes'].max()
minutos_range = st.slider('Filtrar por minutos jugados:', 0, int(max_minutes), (0, int(max_minutes)), step=100)

# Filtro de año de nacimiento (solo si está disponible)
if 'birth_year' in resumen_general_df.columns:
    min_birth_year = int(resumen_general_df['birth_year'].min())
    max_birth_year = int(resumen_general_df['birth_year'].max())
    birth_year_range = st.slider('Filtrar por año de nacimiento:', min_birth_year, max_birth_year, (min_birth_year, max_birth_year), step=1)
else:
    birth_year_range = (None, None)

# Reseteo de filtros
if st.button('Resetear filtros'):
    selected_perfil = perfiles_options[0]
    selected_competitions = competition_options
    minutos_range = (0, int(max_minutes))
    if birth_year_range != (None, None):
        birth_year_range = (min_birth_year, max_birth_year)

# Filtrado de datos
df = data_frames[selected_perfil]
df_filtered = df[(df['player_season_minutes'] >= minutos_range[0]) & (df['player_season_minutes'] <= minutos_range[1])]
if birth_year_range != (None, None):
    df_filtered = df_filtered[(df_filtered['birth_year'] >= birth_year_range[0]) & (df_filtered['birth_year'] <= birth_year_range[1])]
if selected_competitions:
    df_filtered = df_filtered[df_filtered['competition_name'].isin(selected_competitions)]
df_filtered = df_filtered.sort_values(by='Nota', ascending=False)

# Ajustar estilo de tabla para hacerla más ancha
st.markdown(
    """
    <style>
    .css-1l269bu .css-1offfwp {
        width: 100% !important;
    }
    .dataframe {
        width: 100% !important;
        max-width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Tabla de jugadores
st.dataframe(df_filtered[['player_name', 'team', 'competition_name', 'Posicion_algoritmo', 'player_season_minutes', 'Nota']], width=1200)

# Selección de jugador para estudio
selected_player = st.selectbox('Seleccionar jugador a estudiar:', df_filtered['player_name'].unique())

if selected_player:
    player_data = df_filtered[df_filtered['player_name'] == selected_player].iloc[0]
    st.write(f"**Nota del jugador seleccionado:** {player_data['Nota']}")

    # Gráfico de dispersión
    df_filtered['color'] = df_filtered['player_name'].apply(lambda x: x if x == selected_player else 'Otros')
    scatter_fig = px.scatter(
        df_filtered,
        x='Nota',
        y='player_season_minutes',
        color='color',
        title='Distribución de jugadores y equipos',
        labels={'Nota': 'Nota', 'player_season_minutes': 'Minutos Jugados'},
        template='plotly_white',
        hover_name='player_name',
    )
    scatter_fig.update_layout(width=800, height=500, margin=dict(l=10, r=10, t=40, b=20))
    st.plotly_chart(scatter_fig)

    # Gráfico de barras
    highlighted_players = df_filtered[df_filtered['highlight'] == 'green']
    metrics = player_data.index[player_data.index.get_loc('Nota') + 1:]
    
    # Excluir columnas no deseadas, como 'highlight' y 'birth_date'
    excluded_columns = ['highlight', 'birth_date', 'birth_year', 'player_season_minutes']
    metrics = [metric for metric in metrics if metric not in excluded_columns]

    player_metrics = player_data[metrics].astype(float)
    highlighted_metrics_mean = highlighted_players[metrics].mean().astype(float)
    metrics = [metric.replace('percentil_zscore_', '') for metric in metrics]
    
    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(
        x=metrics,
        y=player_metrics,
        name=selected_player,
        marker_color='blue'
    ))
    bar_fig.add_trace(go.Bar(
        x=metrics,
        y=highlighted_metrics_mean,
        name='Top Players Average',
        marker_color='green'
    ))
    bar_fig.update_layout(
        title=f'Comparación de Métricas para {selected_player}',
        xaxis_title='Métricas',
        yaxis_title='Percentil',
        barmode='group',
        height=500,
        width=800
    )
    st.plotly_chart(bar_fig)

# Botón para mostrar información técnica
if st.button('Mostrar información técnica'):
    text_file_name = text_files[(metricas, comparacion)]
    text_file_path = f'{text_file_name}'
    technical_info = load_technical_info(text_file_path)
    
    st.markdown("## Información Técnica")
    st.text(technical_info)

    # Mostrar jugadores top
    st.markdown("### Jugadores Top")
    st.write(df_filtered[['player_name', 'Nota']].head(10))
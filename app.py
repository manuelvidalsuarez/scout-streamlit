# -*- coding: utf-8 -*-

import dash
from dash import dcc, html, Input, Output, dash_table, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Nombres de los archivos Excel
files = {
    ('Posición específica', 'Posición específica'): 'Seleccion_especifica_Evaluacion_especifica.xlsx',
    ('Posición específica', 'Posición asociada'): 'Seleccion_especifica_Evaluacion_asociada.xlsx',
    ('Posición asociada', 'Posición específica'): 'Seleccion_asociada_Evaluacion_especifica.xlsx',
    ('Posición asociada', 'Posición asociada'): 'Seleccion_asociada_Evaluacion_asociada.xlsx'
}

# Define the jugadores_posiciones dictionary here
jugadores_posiciones = {
    'Lateral': {
        'posicion': 'Lateral',
        'jugadores': ['Alejandro Grimaldo García', 'Kyle Walker', 'Daniel Carvajal Ramos', 'Achraf Hakimi Mouh', 'Trent Alexander-Arnold', 'Alphonso Davies'],
        'nombre_hoja': 'Lateral'
    },
    # Include the rest of the players and their positions as shown previously
    'Central Salida Balon-Ofensivo': {
        'posicion': 'Central',
        'jugadores': ['Micky van de Ven', 'Rúben Santos Gato Alves Dias', 'Gabriel dos Santos Magalhães', 'Alessandro Bastoni', 'Joško Gvardiol', 'Mats Hummels'],
        'nombre_hoja': 'Central Salida Balon-Ofensivo'
    },
    'Central Duelos-Seguridad': {
        'posicion': 'Central',
        'jugadores': ['Virgil van Dijk', 'William Saliba', 'Min Jae Kim', 'Dayotchanculle Upamecano', 'Ronald Federico Araújo da Silva', 'Antonio Rüdiger'],
        'nombre_hoja': 'Central Duelos-Seguridad'
    },
    'Pivote': {
        'posicion': 'Pivote',
        'jugadores': ['Declan Rice', 'Rodrigo Hernández Cascante', 'Frenkie de Jong', 'Toni Kroos', 'Alexis Mac Allister', 'Vitor Machado Ferreira'],
        'nombre_hoja': 'Pivote'
    },
    'BoxToBox': {
        'posicion': 'BoxToBox',
        'jugadores': ['Federico Santiago Valverde Dipetta', 'Kevin De Bruyne', 'Nicolò Barella', 'Eduardo Camavinga', 'Bruno Miguel Borges Fernandes', 'Rodrigo Javier De Paul'],
        'nombre_hoja': 'BoxToBox'
    },
    'Mediapunta': {
        'posicion': 'Mediapunta',
        'jugadores': ['Martin Ødegaard', 'Jude Bellingham', 'James Maddison', 'Jamal Musiala', 'Cole Palmer', 'Florian Wirtz'],
        'nombre_hoja': 'Mediapunta'
    },
    'Extremo Profundo': {
        'posicion': 'Extremo',
        'jugadores': ['Ousmane Dembélé', 'Bukayo Saka', 'Nicholas Williams Arthuer', 'Vinícius José Paixão de Oliveira Júnior', 'Lamine Yamal Nasraoui Ebana', 'Kaoru Mitoma'],
        'nombre_hoja': 'Extremo Profundo'
    },
    'Extremo Asociativo': {
        'posicion': 'Extremo',
        'jugadores': ['Heung-Min Son', 'Kylian Mbappé Lottin', 'Phil Foden', 'Bernardo Mota Veiga de Carvalho e Silva', 'Takefusa Kubo', 'Rodrygo Silva de Goes'],
        'nombre_hoja': 'Extremo Asociativo'
    },
    'Delantero Referencia': {
        'posicion': 'Delantero',
        'jugadores': ['Erling Håland', 'Victor James Osimhen', 'Dušan Vlahović', 'Robert Lewandowski', 'Artem Dovbyk', 'Viktor Gyökeres'],
        'nombre_hoja': 'Delantero Referencia'
    },
    'Delantero Asociativo': {
        'posicion': 'Delantero',
        'jugadores': ['Harry Kane', 'Ollie Watkins', 'Julián Álvarez', 'Lautaro Javier Martínez', 'Kai Havertz', 'Antoine Griezmann'],
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
        data_frames[sheet_name] = df
    return data_frames

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Exponer el servidor de Flask para Gunicorn

app.layout = html.Div([
    html.Div([
        html.Label('Método de selección de métricas relevantes:', style={'fontFamily': 'Arial', 'fontSize': '20px'}),
        dcc.Dropdown(
            id='metricas-dropdown',
            options=[
                {'label': 'Posición específica', 'value': 'Posición específica'},
                {'label': 'Posición asociada', 'value': 'Posición asociada'}
            ],
            value='Posición específica',
            style={'width': '100%', 'fontFamily': 'Arial'}
        ),
        html.Label('Tipo de comparación:', style={'fontFamily': 'Arial', 'fontSize': '20px'}),
        dcc.Dropdown(
            id='comparacion-dropdown',
            options=[
                {'label': 'Posición específica', 'value': 'Posición específica'},
                {'label': 'Posición asociada', 'value': 'Posición asociada'}
            ],
            value='Posición específica',
            style={'width': '100%', 'fontFamily': 'Arial'}
        ),
        html.Label('Selecciona el perfil:', style={'fontFamily': 'Arial', 'fontSize': '20px'}),
        dcc.Dropdown(
            id='perfil-selector',
            options=[],
            style={'width': '100%', 'fontFamily': 'Arial'}
        ),
        html.Label('Filtrar por competición:', style={'fontFamily': 'Arial', 'fontSize': '20px'}),
        dcc.Dropdown(
            id='competition-filter',
            options=[],
            multi=True,
            placeholder='Buscar competiciones...',
            style={'width': '100%', 'fontFamily': 'Arial'}
        ),
        html.Label('Filtrar por minutos jugados:', style={'fontFamily': 'Arial', 'fontSize': '20px'}),
        dcc.RangeSlider(
            id='minutos-slider',
            min=0,
            max=1000,  # Placeholder value
            step=100,
            value=[0, 1000],  # Placeholder values
            marks={i: str(i) for i in range(0, 1100, 100)},
            tooltip={"placement": "bottom", "always_visible": True}
        ),
        html.Label('Buscar y añadir jugadores:', style={'fontFamily': 'Arial', 'fontSize': '20px'}),
        dcc.Dropdown(
            id='player-search',
            options=[],
            multi=True,
            placeholder='Buscar jugadores...',
            style={'width': '100%', 'fontFamily': 'Arial'}
        ),
        html.Button('Resetear filtros', id='reset-button', n_clicks=0, style={'fontFamily': 'Arial', 'fontSize': '16px', 'padding': '10px', 'marginTop': '20px'})
    ], style={'width': '20%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),

    html.Div([
    html.Div(id='output-container', style={'marginTop': '20px', 'fontFamily': 'Arial', 'display': 'flex', 'justifyContent': 'flex-start'}),
    html.Div(id='scatter-container', style={'width': '35%', 'height': '500px', 'display': 'inline-block', 'verticalAlign': 'top', 'marginTop': '20px'}),
    html.Div(id='bar-chart-container', style={'width': '25%', 'height': '500px', 'display': 'inline-block', 'verticalAlign': 'top', 'marginTop': '20px', 'marginLeft': '100px'})
], style={'width': '75%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'})

], style={'backgroundColor': '#E8F0F2', 'padding': '20px', 'fontFamily': 'Arial'})

@app.callback(
    Output('output-container', 'children'),
    Output('player-search', 'options'),
    Output('perfil-selector', 'options'),
    Output('perfil-selector', 'value'),
    Output('competition-filter', 'options'),
    Output('minutos-slider', 'max'),
    Output('minutos-slider', 'marks'),
    Output('minutos-slider', 'value'),
    Input('metricas-dropdown', 'value'),
    Input('comparacion-dropdown', 'value'),
    Input('perfil-selector', 'value'),
    Input('competition-filter', 'value'),
    Input('minutos-slider', 'value'),
    Input('player-search', 'value'),
    Input('reset-button', 'n_clicks')
)
def update_outputs(metricas, comparacion, selected_perfil, selected_competitions, minutos_range, selected_players, reset_n_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Determine the appropriate file based on the selected metric and comparison
    file_name = files[(metricas, comparacion)]
    data_frames = load_data_with_highlight(file_name, jugadores_posiciones)
    resumen_general_df = pd.read_excel(file_name, sheet_name='Resumen General', engine='openpyxl')

    perfiles_options = [{'label': perfil, 'value': perfil} for perfil in data_frames.keys()]
    competition_options = [{'label': comp, 'value': comp} for comp in resumen_general_df['competition_name'].unique()]
    max_minutes = resumen_general_df['player_season_minutes'].max()
    slider_marks = {i: str(i) for i in range(0, int(max_minutes) + 1, 500)}

    if triggered_id == 'reset-button':
        selected_perfil = perfiles_options[0]['value']
        selected_competitions = [comp['value'] for comp in competition_options]
        minutos_range = [0, max_minutes]
        selected_players = []

    if not selected_perfil:
        selected_perfil = perfiles_options[0]['value']

    df = data_frames[selected_perfil]
    df_filtered = df[(df['player_season_minutes'] >= minutos_range[0]) & (df['player_season_minutes'] <= minutos_range[1])]
    if selected_competitions:
        df_filtered = df_filtered[df_filtered['competition_name'].isin(selected_competitions)]

    df_filtered = df_filtered.sort_values(by='Nota', ascending=False)

    table = dash_table.DataTable(
        id='player-table',
        columns=[
            {'name': ['Filtro', 'Nombre'], 'id': 'player_name', 'type': 'text'},
            {'name': ['Filtro', 'Equipo'], 'id': 'team', 'type': 'text'},
            {'name': ['Filtro', 'Competición'], 'id': 'competition_name', 'type': 'text'},
            {'name': ['Filtro', 'Posición'], 'id': 'Posicion_algoritmo', 'type': 'text'},
            {'name': ['Filtro', 'Minutos'], 'id': 'player_season_minutes', 'type': 'numeric'},
            {'name': ['Filtro', 'Nota'], 'id': 'Nota', 'type': 'numeric'}
        ],
        data=df_filtered.to_dict('records'),
        style_table={'overflowX': 'auto', 'width': '100%', 'display': 'inline-block', 'verticalAlign': 'top'},
        style_header={
            'backgroundColor': '#1E90FF',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'fontFamily': 'Arial'
        },
        style_cell={
            'backgroundColor': '#E8F0F2',
            'color': 'black',
            'textAlign': 'center',
            'fontFamily': 'Arial',
            'whiteSpace': 'normal',
            'height': 'auto'
        },
        style_data_conditional=[
            {
                'if': {'column_id': 'Nota'},
                'textAlign': 'center'
            },
            {
                'if': {'filter_query': '{highlight} = "green"'},
                'backgroundColor': 'green',
                'color': 'white'
            }
        ],
        filter_action='native',
        sort_action='native',
        sort_mode='multi',
        page_size=20,
        row_selectable='multi',
        selected_rows=[]
    )

    player_options = [{'label': player, 'value': player} for player in df_filtered['player_name'].unique()]

    return [table, player_options, perfiles_options, selected_perfil, competition_options, max_minutes, slider_marks, minutos_range]

@app.callback(
    Output('scatter-container', 'children'),
    Output('bar-chart-container', 'children'),
    Input('player-table', 'selected_rows'),
    Input('player-search', 'value'),
    State('perfil-selector', 'value'),
    State('competition-filter', 'value'),
    State('minutos-slider', 'value'),
    State('metricas-dropdown', 'value'),
    State('comparacion-dropdown', 'value')
)
def update_scatter_and_bar_chart(selected_rows, selected_players, selected_perfil, selected_competitions, minutos_range, metricas, comparacion):
    if not selected_rows and not selected_players:
        print("No players selected.")
        return dash.no_update, dash.no_update

    file_name = files[(metricas, comparacion)]
    data_frames = load_data_with_highlight(file_name, jugadores_posiciones)
    df = data_frames[selected_perfil]
    df_filtered = df[(df['player_season_minutes'] >= minutos_range[0]) & (df['player_season_minutes'] <= minutos_range[1])]
    if selected_competitions:
        df_filtered = df_filtered[df_filtered['competition_name'].isin(selected_competitions)]

    selected_player_names = df_filtered.iloc[selected_rows]['player_name'].tolist() if selected_rows else []
    selected_player_names.extend(selected_players or [])

    if not selected_player_names:
        print("No selected player names after combining.")
        return dash.no_update, dash.no_update

    df_filtered['color'] = df_filtered['player_name'].apply(lambda x: x if x in selected_player_names else 'Otros')

    # Debugging output
    print(f"Selected players: {selected_player_names}")
    print(f"Filtered DataFrame: {df_filtered.head()}")

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

    scatter_fig.update_layout(
        width=400,
        height=300,
        margin=dict(l=10, r=0, t=40, b=20),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.6,
            xanchor='center',
            x=0.5
        )
    )

    scatter_fig.update_traces(marker=dict(size=12, opacity=0.5), selector=dict(mode='markers'))
    scatter_fig.update_traces(marker=dict(size=20, opacity=1), selector=dict(marker_color='color'))

    # Bar chart
    selected_player = df_filtered[df_filtered['player_name'].isin(selected_player_names)]
    if selected_player.empty:
        return dcc.Graph(id='scatter-plot', figure=scatter_fig), html.Div()

    highlighted_players = df_filtered[df_filtered['highlight'] == 'green']

    metrics = selected_player.columns[selected_player.columns.get_loc('Nota') + 1:]
    player_metrics = selected_player[metrics].iloc[0]
    highlighted_metrics_mean = highlighted_players[metrics].mean()

    # Remove 'percentil_zscore_' prefix
    metrics = [metric.replace('percentil_zscore_', '') for metric in metrics]

    bar_fig = go.Figure()

    bar_fig.add_trace(go.Bar(
        x=metrics,
        y=player_metrics,
        name=selected_player_names[0],
        marker_color='blue'
    ))

    bar_fig.add_trace(go.Bar(
        x=metrics,
        y=highlighted_metrics_mean,
        name='Top Players Average',
        marker_color='green'
    ))

    bar_fig.update_layout(
        title=f'Comparación de Métricas para {selected_player_names[0]}',
        xaxis_title='Métricas',
        yaxis_title='Percentil',
        barmode='group',
        height=500,
        width=600,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=+0.95,
            xanchor='center',
            x=0.5
        )
    )

    return dcc.Graph(id='scatter-plot', figure=scatter_fig), dcc.Graph(id='bar-chart', figure=bar_fig)

if __name__ == '__main__':
    app.run_server(debug=True)

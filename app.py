from dash import Dash, html, dcc, dash_table, Input, Output
import pandas as pd
import plotly.express as px

df = pd.read_csv(r'42_Dash\autoscout24 (1).csv')
df = df.dropna()
df['year'] = df['year'].astype(int)

makes = sorted(df['make'].unique())
fuels = sorted(df['fuel'].unique())
years = sorted(df['year'].unique())

app = Dash(__name__, assets_folder='assets')

BG = '#0b1220'
CARD = '#111827'
CYAN = '#00d4ff'

app.layout = html.Div(
    style={
        'fontFamily': 'Arial',
        'backgroundColor': BG,
        'color': 'white',
        'padding': '24px'
    },
    children=[

        html.Img(
            src='/assets/auto.png',
            style={
                'width': '100%',
                'height': '600px',
                'objectFit': 'cover',
                'borderRadius': '16px',
                'display': 'block'
            }
        ),

        html.Img(
            src='/assets/logo1.png',
            style={
                'width': '700px',
                'display': 'block',
                'margin': '-120px auto 10px auto',
                'position': 'relative',
                'zIndex': '10'
            }
        ),

        html.P(
            'Interaktive Analyse von Gebrauchtwagenpreisen',
            style={
                'textAlign': 'center',
                'fontSize': '18px',
                'fontWeight': 'bold',
                'marginBottom': '25px'
            }
        ),

        html.Div(
            style={
                'backgroundColor': CARD,
                'padding': '18px',
                'borderRadius': '14px',
                'marginBottom': '18px'
            },
            children=[
                html.Div([
                    html.Label('Marke auswählen:'),
                    dcc.Dropdown(
                        options=makes,
                        value=makes[0],
                        id='make-dropdown',
                        style={'color': 'black'}
                    )
                ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

                html.Div([
                    html.Label('Kraftstoff auswählen:'),
                    dcc.Dropdown(
                        options=fuels,
                        value=fuels[0],
                        id='fuel-dropdown',
                        style={'color': 'black'}
                    )
                ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

                html.Div([
                    html.Label('Baujahr auswählen:'),
                    dcc.Slider(
                        min=int(min(years)),
                        max=int(max(years)),
                        value=int(max(years)),
                        marks={
                            int(year): {
                                'label': str(year),
                                'style': {'color': 'cyan'}
                            }
                            for year in years[::2]
                        },
                        step=1,
                        id='year-slider'
                    )
                ], style={'width': '35%', 'display': 'inline-block', 'padding': '10px'})
            ]
        ),

        html.Div(id='kennzahlen'),

        html.Div([
            html.Div(dcc.Graph(id='scatter-graph'), style={'width': '50%', 'display': 'inline-block'}),
            html.Div(dcc.Graph(id='price-histogram'), style={'width': '50%', 'display': 'inline-block'}),
        ]),

        html.Div([
            html.Div(dcc.Graph(id='fuel-pie'), style={'width': '50%', 'display': 'inline-block'}),
            html.Div(dcc.Graph(id='avg-price-bar'), style={'width': '50%', 'display': 'inline-block'}),
        ]),

        html.H2('Gefilterte Fahrzeugdaten'),

        dash_table.DataTable(
            id='car-table',
            page_size=10,
            style_cell={
                'textAlign': 'center',
                'color': 'white',
                'backgroundColor': CARD
            },
            style_header={
                'fontWeight': 'bold',
                'backgroundColor': '#1f2937',
                'color': CYAN
            }
        )
    ]
)


@app.callback(
    Output('scatter-graph', 'figure'),
    Output('price-histogram', 'figure'),
    Output('fuel-pie', 'figure'),
    Output('avg-price-bar', 'figure'),
    Output('car-table', 'data'),
    Output('car-table', 'columns'),
    Output('kennzahlen', 'children'),
    Input('make-dropdown', 'value'),
    Input('fuel-dropdown', 'value'),
    Input('year-slider', 'value')
)
def update_dashboard(selected_make, selected_fuel, selected_year):
    filtered_df = df[
        (df['make'] == selected_make) &
        (df['fuel'] == selected_fuel) &
        (df['year'] <= selected_year)
    ]

    scatter = px.scatter(
        filtered_df,
        x='mileage',
        y='price',
        color='gear',
        hover_data=['make', 'model', 'year', 'hp'],
        title='Preis vs. Kilometerstand'
    )

    histogram = px.histogram(
        filtered_df,
        x='price',
        nbins=40,
        title='Preisverteilung'
    )

    pie = px.pie(
        filtered_df,
        names='gear',
        title='Anteil Schaltung / Automatik'
    )

    avg_price = (
        df.groupby('make', as_index=False)['price']
        .mean()
        .sort_values('price', ascending=False)
        .head(15)
    )

    bar = px.bar(
        avg_price,
        x='make',
        y='price',
        title='Top 15 Marken nach Durchschnittspreis'
    )

    for fig in [scatter, histogram, pie, bar]:
        fig.update_layout(
            paper_bgcolor=CARD,
            plot_bgcolor=CARD,
            font_color='white',
            title_font_color='white'
        )

    table_data = filtered_df.head(100).to_dict('records')
    table_columns = [{'name': col, 'id': col} for col in filtered_df.columns]

    if len(filtered_df) > 0:
        kennzahlen = html.Div(
            style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(4, 1fr)',
                'gap': '15px',
                'marginBottom': '18px'
            },
            children=[
                kpi('Anzahl Fahrzeuge', f'{len(filtered_df)}'),
                kpi('Durchschnittspreis', f'{filtered_df["price"].mean():.0f} €'),
                kpi('Durchschnittliche Kilometer', f'{filtered_df["mileage"].mean():.0f} km'),
                kpi('Durchschnittliche PS', f'{filtered_df["hp"].mean():.0f} PS')
            ]
        )
    else:
        kennzahlen = html.H3('Keine passenden Fahrzeuge gefunden.')

    return scatter, histogram, pie, bar, table_data, table_columns, kennzahlen


def kpi(title, value):
    return html.Div(
        style={
            'backgroundColor': CARD,
            'padding': '20px',
            'borderRadius': '14px',
            'border': '1px solid #1f2937'
        },
        children=[
            html.P(title, style={'margin': '0', 'color': 'white'}),
            html.H2(value, style={'margin': '5px 0 0 0', 'color': CYAN})
        ]
    )


if __name__ == '__main__':
    app.run(debug=True)
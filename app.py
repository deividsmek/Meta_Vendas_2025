import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from google.colab import drive

# Montar o Google Drive
drive.mount('/content/drive')

# Nome do arquivo CSV onde os dados serão armazenados
csv_file = '/content/drive/My Drive/vendas_diarias.csv'

# Meta de vendas para o ano
meta_vendas = 50000  # Meta final de vendas é 50.000 reais

# Inicialização dos dados
dias_do_ano = pd.date_range(start='2025-01-01', end='2025-12-31')

# Função para carregar dados do CSV
def carregar_dados():
    try:
        df = pd.read_csv(csv_file, parse_dates=['Data'])
    except FileNotFoundError:
        df = pd.DataFrame({'Data': dias_do_ano, 'Vendas': [0] * len(dias_do_ano)})
        salvar_dados(df)  # Salvar o arquivo se não existir
    return df

# Função para salvar dados no CSV
def salvar_dados(df):
    df.to_csv(csv_file, index=False)

# Função para inserir vendas diárias
def inserir_vendas(valor):
    df = carregar_dados()
    hoje = datetime.now().date()
    if hoje in df['Data'].dt.date.values:
        df.loc[df['Data'].dt.date == hoje, 'Vendas'] = valor
        salvar_dados(df)
        print(f"Valor de {valor} inserido para o dia {hoje}.")
    else:
        print("Erro: Data fora do intervalo definido.")

# Função para atualizar vendas de um dia específico
def atualizar_vendas(dia, valor):
    df = carregar_dados()
    if dia in df['Data'].dt.dayofyear.values:
        df.loc[df['Data'].dt.dayofyear == dia, 'Vendas'] = valor
        salvar_dados(df)
        print(f"Valor de {valor} inserido para o dia {dia}.")
    else:
        print("Erro: Dia fora do intervalo definido.")

# Função para calcular a meta diária restante
def calcular_meta_diaria_restante(df):
    hoje = datetime.now().date()
    dias_restantes = (dias_do_ano[-1].date() - hoje).days + 1
    progresso_acumulado = df['Vendas'].sum()
    meta_restante = meta_vendas - progresso_acumulado
    if dias_restantes > 0:
        return meta_restante / dias_restantes
    return 0

# Função para obter a data atual e o dia da semana em português
def obter_data_atual():
    hoje = datetime.now()
    dias_semana = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
    meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
    dia_semana = dias_semana[hoje.weekday()]
    data_formatada = f"{dia_semana}, {hoje.day} de {meses[hoje.month - 1]} de {hoje.year}"
    return f"Data: {data_formatada}"

# Inicializa a aplicação Dash
app = dash.Dash(__name__)
app.title = "Meta de Vendas 2025"

app.layout = html.Div([
    html.H1("Dashboard de Vendas 2025", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.H3(obter_data_atual(), style={'margin-bottom': '20px'}),
            html.Label('Valor de venda de hoje:'),
            dcc.Input(id='input-vendas', type='number', placeholder='Insira o valor de vendas', value=0, style={'margin-right': '10px'}),
            html.Button(id='submit-button', n_clicks=0, children='Inserir Vendas')
        ], style={'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label('Dia do ano que deseja alterar:'),
            dcc.Input(id='dia', type='number', placeholder='Número do dia (1-365)', value=1, style={'margin-right': '10px'}),
            html.Label('Valor a ser alterado:'),
            dcc.Input(id='valor-dia', type='number', placeholder='Valor para o dia específico', value=0, style={'margin-right': '10px'}),
            html.Button(id='update-button', n_clicks=0, children='Atualizar Vendas de Dia Específico')
        ], style={'display': 'inline-block', 'padding': '10px'})
    ], style={'textAlign': 'center'}),

    html.Div(id='mensagem-sucesso', style={'textAlign': 'center', 'color': 'green'}),

    dcc.Graph(id='progresso-diario'),

    html.Div([
        html.Div([
            dcc.Graph(id='progresso-anual'),
        ], style={'width': '50%', 'display': 'inline-block'}),

        html.Div([
            html.H2(id='valor-acumulado', style={'fontSize': '32px', 'fontWeight': 'bold'}),
            html.H2(id='meta-diaria-atual', style={'fontSize': '16px', 'fontWeight': 'bold', 'color': 'blue'})
        ], style={'width': '50%', 'display': 'inline-block', 'textAlign': 'center', 'verticalAlign': 'middle'})
    ], style={'display': 'flex'}),

    dcc.Graph(id='meta-diaria')
], style={'fontFamily': 'Arial, sans-serif'})

@app.callback(
    [Output('progresso-diario', 'figure'),
     Output('progresso-anual', 'figure'),
     Output('meta-diaria', 'figure'),
     Output('valor-acumulado', 'children'),
     Output('meta-diaria-atual', 'children'),
     Output('input-vendas', 'value'),
     Output('mensagem-sucesso', 'children')],
    [Input('submit-button', 'n_clicks'),
     Input('update-button', 'n_clicks')],
    [State('input-vendas', 'value'),
     State('dia', 'value'),
     State('valor-dia', 'value')]
)
def update_graphs(n_clicks_insert, n_clicks_update, valor_vendas, dia, valor_dia):
    mensagem_sucesso = ""
    if n_clicks_insert > 0 and valor_vendas is not None:
        inserir_vendas(valor_vendas)
        mensagem_sucesso = "Vendas inseridas com sucesso!"

    if n_clicks_update > 0 and dia is not None and valor_dia is not None:
        atualizar_vendas(dia, valor_dia)
        mensagem_sucesso = "Vendas atualizadas com sucesso!"

    # Recarregar os dados do CSV
    df = carregar_dados()

    # Calcular a meta diária restante
    meta_diaria_restante = calcular_meta_diaria_restante(df)

    # Gráfico de barras das vendas diárias
    fig_diario = px.bar(df, x='Data', y='Vendas',
                        labels={'Data': 'Dias do Ano', 'Vendas': 'Vendas Diárias'},
                        title='Progresso Diário das Vendas')

    # Gráfico de pizza do progresso anual
    progresso_acumulado = df['Vendas'].sum()
    progresso_percentual = progresso_acumulado / meta_vendas * 100
    fig_anual = px.pie(values=[progresso_percentual, 100 - progresso_percentual],
                       names=['Progresso', 'Restante'],
                       title='Progresso Anual para Atingir a Meta de Vendas (50.000 Reais)')

    # Gráfico de barras da meta diária (últimos 7 dias)
    hoje = datetime.now().date()
    sete_dias_atras = hoje - timedelta(days=6)
    ultimos_7_dias = df[(df['Data'].dt.date >= sete_dias_atras) & (df['Data'].dt.date <= hoje)]

    fig_meta_diaria = go.Figure()
    fig_meta_diaria.add_trace(go.Bar(
        x=ultimos_7_dias['Data'],
        y=[meta_diaria_restante] * len(ultimos_7_dias),
        name='Meta Diária Restante',
        marker_color='lightgray'
    ))
    fig_meta_diaria.add_trace(go.Bar(
        x=ultimos_7_dias['Data'],
        y=ultimos_7_dias['Vendas'],
        name='Vendas',
        marker_color='blue'
    ))
    fig_meta_diaria.update_layout(
        title='Meta Diária de Vendas (Últimos 7 Dias)',
        barmode='group',
        xaxis_title='Dias do Ano',
        yaxis_title='Valor em Reais'
    )

    # Valor acumulado em reais
    valor_acumulado_text = f"Valor Acumulado: R$ {progresso_acumulado:,.2f}"
    meta_diaria_atual_text = f"Meta Diária Atual: R$ {meta_diaria_restante:,.2f}"

    return fig_diario, fig_anual, fig_meta_diaria, valor_acumulado_text, meta_diaria_atual_text, 0, mensagem_sucesso

if __name__ == '__main__':
    app.run_server(debug=True)
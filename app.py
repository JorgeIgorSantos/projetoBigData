import os
import streamlit as st
import plotly.express as px
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Configurações da API do Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1z-_muqWFLJFEtnRGc5UdrFpzNIvLQ7JlcuyIODJ88yI"  # ID da planilha
RANGE_NAME = "A:G"  # Ajuste para o intervalo que contém seus dados

# Função para buscar dados do Google Sheets
def get_data_from_sheets():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get("values", [])
        
        # Converte para DataFrame
        if values:
            headers = values[0]
            data = pd.DataFrame(values[1:], columns=headers)
            return data
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Erro ao acessar o Google Sheets: {e}")
        return pd.DataFrame()

# Mapeamento de cores para as respostas numéricas
color_map = {
    '1': '#FF0000',  # Vermelho
    '2': '#FF7F00',  # Laranja
    '3': '#FFFF00',  # Amarelo
    '4': '#00FF00',  # Verde
    '5': '#0000FF',  # Azul
}

# Carrega os dados
df = get_data_from_sheets()

# Converte as respostas para strings para garantir que as cores sejam mapeadas corretamente
for col in df.columns[1:]:  # Ignora a coluna de identificação
    df[col] = df[col].astype(str)

# Título da aplicação
st.title("Dashboard de Satisfação dos Clientes - Academia")

# Widget para selecionar a pergunta
selected_question = st.selectbox(
    'Selecione a Pergunta para Visualizar',
    df.columns[1:]  # Exclui a coluna de identificação
)

# Gráfico da pergunta selecionada
fig = px.pie(
    df, names=selected_question, title=f'Respostas para {selected_question}',
    hole=0.3,  # Gráfico de pizza com "furo" opcional
    color=df[selected_question],
    color_discrete_map=color_map  # Mapeamento de cores
)
fig.update_traces(textinfo='percent+label')  # Exibe percentuais e rótulos
st.plotly_chart(fig)

# Gráficos de todas as perguntas
st.subheader("Distribuição das Respostas por Pergunta")
for col in df.columns[1:]:
    fig = px.pie(
        df, names=col, title=f'Distribuição para {col}',
        hole=0.3,  # Gráfico de pizza com um pequeno "furo"
        color=df[col],
        color_discrete_map=color_map  # Mapeamento de cores
    )
    fig.update_traces(textinfo='percent+label')  # Exibe percentuais e rótulos
    st.plotly_chart(fig)

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# --- Configurações da Página ---
st.set_page_config(page_title="Diversidade em Companhias Abertas", page_icon="📊", layout="wide")

# --- Funções Auxiliares ---
def connect_db():
    """Conecta ao banco de dados SQLite."""
    conn = sqlite3.connect('database.db')
    return conn

def load_data(table_name):
    """Carrega os dados de uma tabela do banco de dados."""
    conn = connect_db()
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

def update_data(table_name, df):
    """Atualiza os dados no banco de dados."""
    conn = connect_db()
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

# --- Carregamento de Dados ---
try:
    df_cia_aberta = load_data("companhias_abertas")
    df_empregados_faixa_etaria = load_data("faixa_etaria_2024")
    df_empregados_raca = load_data("declaracao_raca_2024")
    df_empregados_genero = load_data("declaracao_genero_2024")
except Exception as e:
    st.error(f"Erro ao carregar dados. Certifique-se de executar o script de importação primeiro. Erro: {e}")
    st.stop()


# --- Barra Lateral ---
st.sidebar.title("Navegação")
page = st.sidebar.radio("Selecione uma página:", ["Dados", "Estatísticas"])

# --- Página dos Dados ---
if page == "Dados":
     # Seleção da Tabela
    selected_table = st.selectbox("Selecione a tabela:", [
        "Companhias Abertas (B3)",
        "Funcionários por Faixa Etária",
        "Funcionários por Raça",
        "Funcionários por Gênero"
    ])

    # Mapeamento do nome da tabela para o DataFrame correspondente
    table_to_df = {
        "Companhias Abertas (B3)": df_cia_aberta,
        "Funcionários por Faixa Etária": df_empregados_faixa_etaria,
        "Funcionários por Raça": df_empregados_raca,
        "Funcionários por Gênero": df_empregados_genero
    }
    # Mapeamento do nome da tabela para o nome real no banco de dados
    table_name_mapping = {
        "Companhias Abertas (B3)": "companhias_abertas",
        "Funcionários por Faixa Etária": "faixa_etaria_2024",
        "Funcionários por Raça": "declaracao_raca_2024",
        "Funcionários por Gênero": "declaracao_genero_2024"
    }

    # Visualização e Edição de Dados
    if selected_table:
        df = table_to_df[selected_table]
        st.title(f"Dados: {selected_table}")
        st.subheader(f"Dados: {selected_table}")
        edited_df = st.data_editor(df, num_rows="dynamic")

        if st.button(f"Salvar Alterações em {selected_table}"):
            real_table_name = table_name_mapping[selected_table]
            update_data(real_table_name, edited_df)
            st.success(f"Dados da tabela '{selected_table}' atualizados com sucesso!")


# --- Página de Estatísticas ---
elif page == "Estatísticas":
    st.title("Estatísticas de Diversidade")

       # --- Preparação dos Dados (Lógica similar ao `dashboard` do Django) ---

    # Distribuição por Gênero
    genero_data = {
        'Feminino': df_empregados_genero['Quantidade_Feminino'].sum(),
        'Masculino': df_empregados_genero['Quantidade_Masculino'].sum(),
        'Nao_Binario': df_empregados_genero['Quantidade_Nao_Binario'].sum(),
        'Outros': df_empregados_genero['Quantidade_Outros'].sum(),
        'Sem_Resposta': df_empregados_genero['Quantidade_Sem_Resposta'].sum()
    }

    # Distribuição por Raça
    raca_data = {
        'Amarelo': df_empregados_raca['Quantidade_Amarelo'].sum(),
        'Branco': df_empregados_raca['Quantidade_Branco'].sum(),
        'Preto': df_empregados_raca['Quantidade_Preto'].sum(),
        'Pardo': df_empregados_raca['Quantidade_Pardo'].sum(),
        'Indigena': df_empregados_raca['Quantidade_Indigena'].sum(),
        'Outros': df_empregados_raca['Quantidade_Outros'].sum(),
        'Sem_Resposta': df_empregados_raca['Quantidade_Sem_Resposta'].sum()
        }

    # Distribuição por Faixa Etária
    faixa_etaria_data = {
        'Ate_30': df_empregados_faixa_etaria['Quantidade_Ate30Anos'].sum(),
        'Entre_30_50': df_empregados_faixa_etaria['Quantidade_30a50Anos'].sum(),
        'Acima_50': df_empregados_faixa_etaria['Quantidade_Acima50Anos'].sum()
        }

    # --- Visualização das Estatísticas ---

    # Distribuição por Gênero
    st.subheader("Distribuição de Funcionários por Gênero")
    fig_genero = px.pie(names=list(genero_data.keys()), values=list(genero_data.values()), title='Gênero')
    st.plotly_chart(fig_genero, use_container_width=True)

    # Distribuição por Raça
    st.subheader("Distribuição de Funcionários por Raça")
    fig_raca = px.pie(names=list(raca_data.keys()), values=list(raca_data.values()), title='Raça')
    st.plotly_chart(fig_raca, use_container_width=True)

    # Distribuição por Faixa Etária
    st.subheader("Distribuição de Funcionários por Faixa Etária")
    fig_faixa_etaria = px.pie(names=list(faixa_etaria_data.keys()), values=list(faixa_etaria_data.values()), title='Faixa Etária')
    st.plotly_chart(fig_faixa_etaria, use_container_width=True)
# --- Rodapé ---
st.sidebar.markdown("---")
st.sidebar.markdown("**Desenvolvido por: Caio Riet Barbosa**")
st.sidebar.markdown("**Linkedin: https://www.linkedin.com/in/caio-riet-70564b223/**")
st.sidebar.markdown("**Github: [Caio Riet]**")
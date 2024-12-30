import requests
import pandas as pd
import sqlite3
from pathlib import Path
import zipfile
import os  # Importe o módulo os para remover arquivos


# URLs dos arquivos de dados a serem baixados
URL_CIA_ABERTA = "https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv"
URL_FRE_ZIP = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/fre_cia_aberta_2024.zip"

# Cria um diretório chamado "data" para armazenar os arquivos baixados, caso ele não exista
DATA_DIR = Path("C:/Users/caio.barbosa/Documents/Caio/Pessoal/projeto_streamlit")
DATA_DIR.mkdir(exist_ok=True)

# Dicionário que mapeia nomes de arquivos a seus respectivos caminhos no diretório "data"
CSV_FILES = {
    "companhias_abertas": DATA_DIR / "cad_cia_aberta.csv",
    "fre_zip": DATA_DIR / "fre_cia_aberta_2024.zip"
}

# Caminho para o arquivo do banco de dados SQLite
DB_FILE = DATA_DIR / "database.db"

# Lista de nomes de arquivos CSV específicos a serem extraídos do arquivo ZIP do FRE
FRE_CSV_FILES = [
    "fre_cia_aberta_empregado_local_faixa_etaria_2024.csv",
    "fre_cia_aberta_empregado_local_declaracao_raca_2024.csv",
    "fre_cia_aberta_empregado_local_declaracao_genero_2024.csv"
]

# Função para baixar dados de uma URL e salvar em um arquivo
def baixar_dados(url, destino):
    """Baixa os dados da URL especificada e salva no destino."""
    print(f"Baixando dados de {url}...")
    response = requests.get(url)
    response.raise_for_status()
    with open(destino, "wb") as f:
        f.write(response.content)
    print(f"Dados salvos em {destino}.")


# Função para extrair arquivos específicos de um arquivo ZIP
def extrair_arquivos_zip(arquivo_zip, destino, arquivos_desejados):
    """Extrai os arquivos específicos de um ZIP para o diretório especificado."""
    print(f"Extraindo arquivos desejados de {arquivo_zip} para {destino}...")
    with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
        for file_name in arquivos_desejados:
            if file_name in zip_ref.namelist():
                zip_ref.extract(file_name, destino)
                print(f"Extraído: {file_name}")
    print(f"Arquivos desejados extraídos para {destino}.")


# Função para ler um arquivo CSV e salvar os dados em uma tabela de um banco de dados SQLite
def processar_csv_para_sqlite(arquivo_csv, banco_dados, tabela):
    """Lê o CSV e salva os dados no banco de dados SQLite."""
    print(f"Processando {arquivo_csv} e salvando na tabela '{tabela}' no banco {banco_dados}...")
    df = pd.read_csv(arquivo_csv, sep=";", encoding="latin1", low_memory=False)
    df.insert(0, "id", range(1, len(df) + 1))
    with sqlite3.connect(banco_dados) as conn:
        df.to_sql(tabela, conn, if_exists="replace", index=False)

    print(f"Dados salvos na tabela '{tabela}' no banco {banco_dados}.")


# Função principal que executa o script
def main():
    # Baixa os dados se os arquivos ainda não existirem
    if not CSV_FILES["companhias_abertas"].exists():
        baixar_dados(URL_CIA_ABERTA, CSV_FILES["companhias_abertas"])
    else:
        print(f"Arquivo {CSV_FILES['companhias_abertas']} já existe. Pulando download.")

    if not CSV_FILES["fre_zip"].exists():
        baixar_dados(URL_FRE_ZIP, CSV_FILES["fre_zip"])
        extrair_arquivos_zip(CSV_FILES["fre_zip"], DATA_DIR, FRE_CSV_FILES)
    else:
        print(f"Arquivo {CSV_FILES['fre_zip']} já existe. Pulando download.")

    # Processa os arquivos CSV e salva os dados no banco de dados SQLite
    processar_csv_para_sqlite(CSV_FILES["companhias_abertas"], DB_FILE, "companhias_abertas")

    # Processa os arquivos CSV extraídos do ZIP do FRE
    for csv_file in FRE_CSV_FILES:
        arquivo_path = DATA_DIR / csv_file
        if arquivo_path.exists():
            tabela_nome = csv_file.replace(".csv", "").replace("fre_cia_aberta_empregado_local_", "")
            processar_csv_para_sqlite(arquivo_path, DB_FILE, tabela_nome)
        else:
            print(f"Aviso: Arquivo {csv_file} não encontrado no diretório {DATA_DIR}.")

    # Apaga os arquivos baixados
    print("Apagando arquivos baixados...")
    for arquivo in CSV_FILES.values():
        if arquivo.exists():
            os.remove(arquivo)
            print(f"Arquivo {arquivo} apagado.")

    for csv_file in FRE_CSV_FILES:
        arquivo_path = DATA_DIR / csv_file
        if arquivo_path.exists():
            os.remove(arquivo_path)
            print(f"Arquivo {arquivo_path} apagado.")

    print("Arquivos baixados apagados. Dados salvos no banco de dados.")

# Executa a função main() se o script for executado diretamente
if __name__ == "__main__":
    main()
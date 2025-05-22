import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv


# Carrega variáveis de ambiente do .env
load_dotenv()

# Parâmetros do banco vindos do .env
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")

# Conexão com MySQL
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")

# Caminho para a pasta com os CSVs
pasta_dimensoes = "data/dimensoes"

# Mapeamento de arquivos -> tabelas
arquivos_para_tabelas = {
    "dim_cliente.csv": "dim_cliente",
    "dim_produto.csv": "dim_produto",
    "dim_vendedor.csv": "dim_vendedor",
    "dim_tempo.csv": "dim_tempo"
}

# Loop para leitura e envio
for arquivo_csv, nome_tabela in arquivos_para_tabelas.items():
    caminho_csv = os.path.join(pasta_dimensoes, arquivo_csv)
    print(f"📤 Importando '{arquivo_csv}' para a tabela '{nome_tabela}'...")
    
        # Ler o arquivo CSV
    df = pd.read_csv(caminho_csv)
    
        # Enviar para a tabela no banco
    df.to_sql(name=nome_tabela, con=engine, if_exists="append", index=False)
    
print(f"✅ Tabela '{nome_tabela}' populada com sucesso!\n")

print("🏁 Todas as dimensões foram importadas para o banco.")
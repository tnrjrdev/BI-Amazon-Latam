import streamlit as st
import pandas as pd

# Carregar os dados
df_vendas = pd.read_csv("dados_tratados/fato_vendas.csv")
df_cliente = pd.read_csv("dimensoes/dim_cliente.csv")

# Verificar se o 'customer_id' está no df_vendas
if 'customer_id' not in df_vendas.columns:
    st.warning("⚠️ O arquivo 'fato_vendas.csv' não contém a coluna 'customer_id'. Fazendo merge com o 'olist_orders_dataset.csv'...")

    # Agora sim, carrega o df_orders apenas se precisar
    df_orders = pd.read_csv("data/dados_auxiliares/olist_orders_dataset.csv")  # Ajuste o caminho
    df_vendas = df_vendas.merge(df_orders[['order_id', 'customer_id']], on='order_id', how='left')

# Merge com dim_cliente para pegar o estado
df_final = df_vendas.merge(df_cliente, on='customer_id', how='left')

# Sidebar - filtro por estado
estado = st.sidebar.selectbox("Selecione o estado", df_final['customer_state'].dropna().unique())

# Filtrar os dados
df_filtrado = df_final[df_final['customer_state'] == estado]

# Mostrar a tabela e o gráfico
st.title("Vendas por Estado")
st.write(df_filtrado.head())

# Gráfico de barras
vendas_estado = df_final.groupby('customer_state')['price'].sum().sort_values(ascending=False)
st.bar_chart(vendas_estado)

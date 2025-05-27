import streamlit as st
import pandas as pd

# ========= Carregar os dados =========
df_vendas = pd.read_csv("dados_tratados/fato_vendas.csv")
df_cliente = pd.read_csv("dimensoes/dim_cliente.csv")
df_produto = pd.read_csv("dimensoes/dim_produto.csv")
df_vendedor = pd.read_csv("dimensoes/dim_vendedor.csv")

# Verificar se o 'customer_id' está no df_vendas
if 'customer_id' not in df_vendas.columns:
    st.warning("⚠️ O arquivo 'fato_vendas.csv' não contém a coluna 'customer_id'. Fazendo merge com o 'olist_orders_dataset.csv'...")
    df_orders = pd.read_csv("data/dados_auxiliares/olist_orders_dataset.csv")  # Ajuste o caminho
    df_vendas = df_vendas.merge(df_orders[['order_id', 'customer_id']], on='order_id', how='left')

# Juntar tudo
df = df_vendas.merge(df_cliente, on='customer_id', how='left') \
              .merge(df_produto, on='product_id', how='left') \
              .merge(df_vendedor, on='seller_id', how='left')

# Conversões de datas e cálculo do prazo de entrega
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])
df['prazo_entrega'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days

# ========= Layout =========
st.title("📊 Dashboard de Vendas - BI Amazon LATAM")

aba = st.sidebar.radio("Escolha a Análise:", [
    "Vendas por Estado",
    "Categorias de Produto",
    "Tipos de Pagamento",
    "Vendedores - Prazo e Avaliação",
    "Satisfação do Cliente"
])

# ========= Análises =========

if aba == "Vendas por Estado":
    st.subheader("💰 Vendas por Estado")
    vendas_estado = df.groupby('customer_state')['price'].sum().sort_values(ascending=False)
    st.bar_chart(vendas_estado)

elif aba == "Categorias de Produto":
    st.subheader("🏷️ Vendas por Categoria de Produto")
    vendas_categoria = df.groupby('product_category_name_english')['price'].sum().sort_values(ascending=False).head(10)
    st.bar_chart(vendas_categoria)

elif aba == "Tipos de Pagamento":
    st.subheader("💳 Tipos de Pagamento Mais Usados")
    pagamento = df['payment_type'].value_counts()
    st.bar_chart(pagamento)

elif aba == "Vendedores - Prazo e Avaliação":
    st.subheader("⏱️ Vendedores com Entregas Mais Rápidas")
    entrega_vendedor = df.groupby('seller_id')['prazo_entrega'].mean().sort_values().head(10)
    st.write(entrega_vendedor)

    st.subheader("⭐ Vendedores com Melhores Avaliações")
    avaliacao_vendedor = df.groupby('seller_id')['review_score'].mean().sort_values(ascending=False).head(10)
    st.write(avaliacao_vendedor)

elif aba == "Satisfação do Cliente":
    st.subheader("😍 Satisfação por Categoria de Produto")
    satisfacao_categoria = df.groupby('product_category_name_english')['review_score'].mean().sort_values(ascending=False).head(10)
    st.write(satisfacao_categoria)

    st.subheader("🌎 Satisfação por Estado")
    satisfacao_estado = df.groupby('customer_state')['review_score'].mean().sort_values(ascending=False)
    st.write(satisfacao_estado)

    st.subheader("⏳ Satisfação por Prazo de Entrega")
    satisfacao_prazo = df.groupby('prazo_entrega')['review_score'].mean().sort_values(ascending=False).head(10)
    st.line_chart(satisfacao_prazo)

st.caption("🔎 Análises construídas com dados Olist - BI Amazon LATAM 🚀")

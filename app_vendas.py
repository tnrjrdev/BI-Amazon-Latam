import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

# ========= Configurações =========
st.set_page_config(page_title="BI Amazon LATAM", layout="wide", page_icon="📦")

# ========= Carregar os dados =========
df_vendas = pd.read_csv("dados_tratados/fato_vendas.csv")
df_cliente = pd.read_csv("dimensoes/dim_cliente.csv")
df_produto = pd.read_csv("dimensoes/dim_produto.csv")
df_vendedor = pd.read_csv("dimensoes/dim_vendedor.csv")

if 'customer_id' not in df_vendas.columns:
    df_orders = pd.read_csv("data/dados_auxiliares/olist_orders_dataset.csv")
    df_vendas = df_vendas.merge(df_orders[['order_id', 'customer_id']], on='order_id', how='left')

# Merge final
df = df_vendas.merge(df_cliente, on='customer_id', how='left') \
              .merge(df_produto, on='product_id', how='left') \
              .merge(df_vendedor, on='seller_id', how='left')

# Conversão de datas e cálculo de prazo
for col in ['order_purchase_timestamp', 'order_delivered_customer_date']:
    df[col] = pd.to_datetime(df[col], errors='coerce')
df['prazo_entrega'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days

# ========= Sidebar com Menu =========
with st.sidebar:
    st.image("assets/logo.png", width=160)
    aba = option_menu("Menu", [
        "Visão Geral", "Vendas por Estado", "Categorias", "Tipos de Pagamento",
        "Vendedores - Prazo e Avaliação", "Satisfação do Cliente"
    ], icons=["house", "bar-chart-line", "tags", "credit-card", "truck", "emoji-smile"],
    menu_icon="grid", default_index=0)

# ========= Título =========
st.markdown("""
    <h1 style='color:#232F3E;'> Dashboard de Vendas - BI Amazon LATAM</h1>
""", unsafe_allow_html=True)

# ========= Visões =========
if aba == "Visão Geral":
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Vendas", f"R$ {df['price'].sum():,.2f}")
    col2.metric("Pedidos", df['order_id'].nunique())
    col3.metric("Clientes", df['customer_unique_id'].nunique())
    st.plotly_chart(px.histogram(df, x='review_score', title='Distribuição das Avaliações'), use_container_width=True)

elif aba == "Vendas por Estado":
    vendas_estado = df.groupby('customer_state')['price'].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(vendas_estado, x='customer_state', y='price', title='💰 Vendas por Estado', color='price')
    st.plotly_chart(fig, use_container_width=True)

elif aba == "Categorias":
    vendas_categoria = df.groupby('product_category_name_english')['price'].sum().nlargest(10).reset_index()
    fig = px.bar(vendas_categoria, x='product_category_name_english', y='price', title='🏷️ Top 10 Categorias', color='price')
    st.plotly_chart(fig, use_container_width=True)

elif aba == "Tipos de Pagamento":
    pagamento = df['payment_type'].value_counts().reset_index()
    pagamento.columns = ['payment_type', 'count']
    fig = px.pie(pagamento, names='payment_type', values='count', title='💳 Distribuição de Pagamentos')
    st.plotly_chart(fig, use_container_width=True)

elif aba == "Vendedores - Prazo e Avaliação":
    st.subheader("⏱️ Vendedores com Entregas Mais Rápidas")
    entrega_vendedor = df.groupby('seller_id')['prazo_entrega'].mean().nsmallest(10).reset_index()
    st.plotly_chart(px.bar(entrega_vendedor, x='seller_id', y='prazo_entrega', title='Top 10 - Prazo de Entrega', color='prazo_entrega'))

    st.subheader("⭐ Vendedores com Melhores Avaliações")
    avaliacao_vendedor = df.groupby('seller_id')['review_score'].mean().nlargest(10).reset_index()
    st.plotly_chart(px.bar(avaliacao_vendedor, x='seller_id', y='review_score', title='Top 10 - Avaliação', color='review_score'))

elif aba == "Satisfação do Cliente":
    st.subheader("😍 Satisfação por Categoria")
    cat = df.groupby('product_category_name_english')['review_score'].mean().nlargest(10).reset_index()
    st.plotly_chart(px.bar(cat, x='product_category_name_english', y='review_score', title='Categorias Melhor Avaliadas', color='review_score'))

    st.subheader("🌎 Satisfação por Estado")
    uf = df.groupby('customer_state')['review_score'].mean().reset_index()
    st.plotly_chart(px.bar(uf, x='customer_state', y='review_score', title='Satisfação Média por UF', color='review_score'))

    st.subheader("⏳ Satisfação por Prazo de Entrega")
    prazo = df.groupby('prazo_entrega')['review_score'].mean().reset_index().sort_values(by='prazo_entrega')
    st.plotly_chart(px.line(prazo, x='prazo_entrega', y='review_score', title='Satisfação x Prazo de Entrega'))

# ========= Rodapé =========
st.markdown("""
<hr style='margin-top: 50px;'>
<center><small>Feito por Tary | Projeto BI Amazon LATAM • © 2025</small></center>
""", unsafe_allow_html=True)

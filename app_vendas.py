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

# Ajuste para colunas renomeadas
if 'id_cliente' not in df_vendas.columns:
    df_orders = pd.read_csv("data/dados_auxiliares/olist_orders_dataset.csv")
    df_vendas = df_vendas.merge(df_orders[['order_id', 'customer_id']], on='order_id', how='left')
    df_vendas = df_vendas.rename(columns={"order_id": "id_pedido", "customer_id": "id_cliente"})

# Merge final
df = df_vendas.merge(df_cliente, on='id_cliente', how='left') \
              .merge(df_produto, on='id_produto', how='left') \
              .merge(df_vendedor, on='id_vendedor', how='left')

# Conversão de datas e cálculo de prazo
for col in ['data_compra', 'data_entrega']:
    df[col] = pd.to_datetime(df[col], errors='coerce')
df['prazo_entrega'] = (df['data_entrega'] - df['data_compra']).dt.days

# ========= Sidebar com Menu =========
with st.sidebar:
    st.image("assets/logo.png", width=160)
    
    aba = option_menu(
        "Menu", 
        [
            "Visão Geral", 
            "Vendas por Estado", 
            "Categorias", 
            "Tipos de Pagamento",
            "Vendedores - Prazo e Avaliação", 
            "Satisfação do Cliente"
        ],
        icons=[
            "house", 
            "bar-chart-line", 
            "tags", 
            "credit-card", 
            "truck", 
            "emoji-smile"
        ],
        menu_icon="grid", 
        default_index=0,
        styles={
            "container": {"padding": "5px", "background-color": "#f8f9fa"},
            "icon": {"color": "black", "font-size": "18px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#e0f0ff",
            },
            "nav-link-selected": {
                "background-color": "#007bff",  # azul
                "font-weight": "bold",
                "color": "white",
            },
        }
    )

# ========= Título =========
st.markdown("""
    <h1 style='color:#232F3E;'> Dashboard de Vendas - BI Amazon LATAM</h1>
""", unsafe_allow_html=True)

# ========= Visões =========
if aba == "Visão Geral":
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Vendas", f"R$ {df['preco'].sum():,.2f}")
    col2.metric("Pedidos", df['id_pedido'].nunique())
    col3.metric("Clientes", df['id_cliente'].nunique())
    st.plotly_chart(px.histogram(df, x='nota_avaliacao', title='Distribuição das Avaliações'), use_container_width=True)

elif aba == "Vendas por Estado":
    vendas_estado = df.groupby('estado_cliente')['preco'].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(vendas_estado, x='estado_cliente', y='preco', title='💰 Vendas por Estado', color='preco')
    st.plotly_chart(fig, use_container_width=True)

elif aba == "Categorias":
    vendas_categoria = df.groupby('nome_categoria')['preco'].sum().nlargest(10).reset_index()
    fig = px.bar(vendas_categoria, x='nome_categoria', y='preco', title='🏷️ Top 10 Categorias', color='preco')
    st.plotly_chart(fig, use_container_width=True)

elif aba == "Tipos de Pagamento":
    pagamento = df['tipo_pagamento'].value_counts().reset_index()
    pagamento.columns = ['tipo_pagamento', 'quantidade']
    fig = px.pie(pagamento, names='tipo_pagamento', values='quantidade', title='💳 Distribuição de Pagamentos')
    st.plotly_chart(fig, use_container_width=True)

elif aba == "Vendedores - Prazo e Avaliação":
    st.subheader("⏱️ Vendedores com Entregas Mais Rápidas")
    entrega_vendedor = df.groupby('id_vendedor')['prazo_entrega'].mean().nsmallest(10).reset_index()
    st.plotly_chart(px.bar(entrega_vendedor, x='id_vendedor', y='prazo_entrega', title='Top 10 - Prazo de Entrega', color='prazo_entrega'))

    st.subheader("⭐ Vendedores com Melhores Avaliações")
    avaliacao_vendedor = df.groupby('id_vendedor')['nota_avaliacao'].mean().nlargest(10).reset_index()
    st.plotly_chart(px.bar(avaliacao_vendedor, x='id_vendedor', y='nota_avaliacao', title='Top 10 - Avaliação', color='nota_avaliacao'))

elif aba == "Satisfação do Cliente":
    st.subheader("Satisfação por Categoria")
    cat = df.groupby('nome_categoria_ingles')['nota_avaliacao'].mean().nlargest(10).reset_index()
    st.plotly_chart(px.bar(cat, x='nome_categoria_ingles', y='nota_avaliacao', title='Categorias Melhor Avaliadas', color='nota_avaliacao'))

    st.subheader("🌎 Satisfação por Estado")
    uf = df.groupby('estado_cliente')['nota_avaliacao'].mean().reset_index()
    st.plotly_chart(px.bar(uf, x='estado_cliente', y='nota_avaliacao', title='Satisfação Média por UF', color='nota_avaliacao'))

    st.subheader("⏳ Satisfação por Prazo de Entrega")
    prazo = df.groupby('prazo_entrega')['nota_avaliacao'].mean().reset_index().sort_values(by='prazo_entrega')
    st.plotly_chart(px.line(prazo, x='prazo_entrega', y='nota_avaliacao', title='Satisfação x Prazo de Entrega'))

# ========= Rodapé =========
st.markdown("""
<hr style='margin-top: 50px;'>
<center><small>Feito por Tary | Projeto BI Amazon LATAM • © 2025</small></center>
""", unsafe_allow_html=True)

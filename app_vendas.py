import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

# ========= Configurações =========
st.set_page_config(page_title="BI Amazon LATAM", layout="wide", page_icon="📦")

# ========= Estilo Global =========
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
        padding-top: 1rem;
        border: none !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        background-color: transparent !important;
        padding: 0 !important;
        border-radius: 0 !important;
        box-shadow: none !important;
    }
    h1, h2, h3, h4 {
        color: #232F3E;
        font-family: 'Segoe UI', sans-serif;
    }
    .stMetric {
        font-family: 'Segoe UI', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# ========= Função de formatação de gráfico =========
def formatar_grafico(fig, titulo_x=0.02):
    fig.update_layout(
        template='plotly_white',
        title_font_size=22,
        title_font_color='#232F3E',
        title_x=titulo_x,
        font=dict(family="Segoe UI", color="#232F3E"),
        xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
        yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
        margin=dict(t=60, l=40, r=30, b=40),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig

# ========= Carregar os dados =========
df_vendas = pd.read_csv("dados_tratados/fato_vendas.csv")
df_cliente = pd.read_csv("dimensoes/dim_cliente.csv")
df_produto = pd.read_csv("dimensoes/dim_produto.csv")
df_vendedor = pd.read_csv("dimensoes/dim_vendedor.csv")

# Ajuste de colunas e merge
if 'id_cliente' not in df_vendas.columns:
    df_orders = pd.read_csv("data/dados_auxiliares/olist_orders_dataset.csv")
    df_vendas = df_vendas.merge(df_orders[['order_id', 'customer_id']], on='order_id', how='left')
    df_vendas = df_vendas.rename(columns={"order_id": "id_pedido", "customer_id": "id_cliente"})

df = df_vendas.merge(df_cliente, on='id_cliente', how='left') \
              .merge(df_produto, on='id_produto', how='left') \
              .merge(df_vendedor, on='id_vendedor', how='left')

for col in ['data_compra', 'data_entrega']:
    df[col] = pd.to_datetime(df[col], errors='coerce')
df['prazo_entrega'] = (df['data_entrega'] - df['data_compra']).dt.days

# ========= Sidebar com Menu =========
with st.sidebar:
    st.image("assets/logo.png", width=160)
    aba = option_menu(
        "",
        ["Visão Geral", "Vendas por Estado", "Categorias", "Tipos de Pagamento", "Vendedores - Prazo e Avaliação", "Satisfação do Cliente"],
        icons=["house", "bar-chart-line", "tags", "credit-card", "truck", "emoji-smile"],
        default_index=0,
        styles={
            "container": {"padding": "0px", "background-color": "#f8f9fa", "border": "none", "box-shadow": "none"},
            "icon": {"color": "#1a73e8", "font-size": "18px"},
            "nav-link": {"font-size": "15px", "font-weight": "500", "color": "#212529", "text-align": "left",
                         "padding": "10px 16px", "margin": "4px 0", "border-radius": "4px",
                         "--hover-color": "#e0efff", "transition": "all 0.2s ease"},
            "nav-link-selected": {"background-color": "#e5f1fb", "color": "#1a73e8", "font-weight": "600",
                                  "border-left": "4px solid #1a73e8", "padding-left": "12px"}
        }
    )

# ========= Título =========
st.markdown("<h1>Dashboard de Vendas - BI Amazon LATAM</h1>", unsafe_allow_html=True)

# ========= Visões =========
if aba == "Visão Geral":
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Vendas", f"R$ {df['preco'].sum():,.2f}")
    col2.metric("Pedidos", df['id_pedido'].nunique())
    col3.metric("Clientes", df['id_cliente'].nunique())

    fig = px.histogram(df, x='nota_avaliacao', title='Distribuição das Avaliações')
    st.plotly_chart(formatar_grafico(fig), use_container_width=True)

elif aba == "Vendas por Estado":
    vendas_estado = df.groupby('estado_cliente')['preco'].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(vendas_estado, x='estado_cliente', y='preco', title='💰 Vendas por Estado', color='preco', color_continuous_scale='blues')
    st.plotly_chart(formatar_grafico(fig), use_container_width=True)

elif aba == "Categorias":
    vendas_categoria = df.groupby('nome_categoria')['preco'].sum().nlargest(10).reset_index()
    fig = px.bar(vendas_categoria, x='nome_categoria', y='preco', title='🏷️ Top 10 Categorias', color='preco', color_continuous_scale='blues')
    st.plotly_chart(formatar_grafico(fig), use_container_width=True)

elif aba == "Tipos de Pagamento":
    pagamento = df['tipo_pagamento'].value_counts().reset_index()
    pagamento.columns = ['tipo_pagamento', 'quantidade']
    fig = px.pie(pagamento, names='tipo_pagamento', values='quantidade', title='💳 Distribuição de Pagamentos',
                 color_discrete_sequence=px.colors.qualitative.Set1)
    fig.update_traces(textinfo='percent+label', pull=[0.05 if i == 0 else 0 for i in range(len(pagamento))])
    st.plotly_chart(formatar_grafico(fig), use_container_width=True)

elif aba == "Vendedores - Prazo e Avaliação":
    st.subheader("⏱️ Vendedores com Entregas Mais Rápidas")
    entrega_vendedor = df.groupby('id_vendedor')['prazo_entrega'].mean().nsmallest(10).reset_index()
    fig = px.bar(entrega_vendedor, x='id_vendedor', y='prazo_entrega', title='Top 10 - Prazo de Entrega',
                 color='prazo_entrega', color_continuous_scale='blues')
    st.plotly_chart(formatar_grafico(fig), use_container_width=True)

    st.subheader("⭐ Vendedores com Melhores Avaliações")
    avaliacao_vendedor = df.groupby('id_vendedor')['nota_avaliacao'].mean().nlargest(10).reset_index()
    fig = px.bar(avaliacao_vendedor, x='id_vendedor', y='nota_avaliacao', title='Top 10 - Avaliação',
                 color='nota_avaliacao', color_continuous_scale='blues')
    st.plotly_chart(formatar_grafico(fig), use_container_width=True)

elif aba == "Satisfação do Cliente":
    st.subheader("🏆 Satisfação por Categoria")
    cat = df.groupby('nome_categoria_ingles')['nota_avaliacao'].mean().nlargest(10).reset_index()
    fig = px.bar(cat, x='nome_categoria_ingles', y='nota_avaliacao', title='Categorias Melhor Avaliadas',
                 color='nota_avaliacao', color_continuous_scale='blues')
    st.plotly_chart(formatar_grafico(fig), use_container_width=True)

    st.subheader("🌎 Satisfação por Estado")
    uf = df.groupby('estado_cliente')['nota_avaliacao'].mean().reset_index()
    fig = px.bar(uf, x='estado_cliente', y='nota_avaliacao', title='Satisfação Média por UF',
                 color='nota_avaliacao', color_continuous_scale='blues')
    st.plotly_chart(formatar_grafico(fig), use_container_width=True)

    st.subheader("⏳ Satisfação por Prazo de Entrega")
    prazo = df.groupby('prazo_entrega')['nota_avaliacao'].mean().reset_index().sort_values(by='prazo_entrega')
    fig = px.line(prazo, x='prazo_entrega', y='nota_avaliacao', title='Satisfação x Prazo de Entrega')
    st.plotly_chart(formatar_grafico(fig), use_container_width=True)

# ========= Rodapé =========
st.markdown("""
<hr style='margin-top: 50px;'>
<center><small>Feito por Tary | Projeto BI Amazon LATAM • © 2025</small></center>
""", unsafe_allow_html=True)

# -*- coding: utf-8 -*-
import pandas as pd
import os

# Tratamento olist_orders_dataset
df = pd.read_csv('olist_orders_dataset.csv')
df = df.dropna(subset=['order_id', 'customer_id', 'order_status'])
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

os.makedirs('dados_tratados', exist_ok=True)
df.to_csv('dados_tratados/olist_orders_tratado.csv', index=False)
print("✅ Arquivo tratado salvo com sucesso!")

# Tratamento olist_customers_dataset
df_clientes = pd.read_csv("olist_customers_dataset.csv")

dim_cliente = df_clientes[[
    "customer_id",
    "customer_unique_id",
    "customer_city",
    "customer_state"
]].drop_duplicates()

# Renomear colunas
dim_cliente = dim_cliente.rename(columns={
    "customer_id": "id_cliente",
    "customer_unique_id": "id_cliente_unico",
    "customer_city": "cidade_cliente",
    "customer_state": "estado_cliente"
})

os.makedirs("dimensoes", exist_ok=True)
dim_cliente.to_csv("dimensoes/dim_cliente.csv", index=False)

# Tratamento olist_products_dataset
df_prod = pd.read_csv("olist_products_dataset.csv")
df_cat = pd.read_csv("product_category_name_translation.csv")

dim_produto = df_prod.merge(df_cat, how="left", on="product_category_name")
dim_produto = dim_produto[[
    "product_id",
    "product_category_name",
    "product_category_name_english",
    "product_name_lenght",
    "product_description_lenght",
    "product_weight_g"
]].drop_duplicates()

# Renomear colunas
dim_produto = dim_produto.rename(columns={
    "product_id": "id_produto",
    "product_category_name": "nome_categoria",
    "product_category_name_english": "nome_categoria_ingles",
    "product_name_lenght": "tamanho_nome",
    "product_description_lenght": "tamanho_descricao",
    "product_weight_g": "peso_gramas"
})

os.makedirs("dimensoes", exist_ok=True)
dim_produto.to_csv("dimensoes/dim_produto.csv", index=False)

# Tratamento olist_sellers_dataset
df_sellers = pd.read_csv("olist_sellers_dataset.csv")

dim_vendedor = df_sellers[[
    "seller_id",
    "seller_city",
    "seller_state"
]].drop_duplicates()

dim_vendedor = dim_vendedor.rename(columns={
    "seller_id": "id_vendedor",
    "seller_city": "cidade_vendedor",
    "seller_state": "estado_vendedor"
})

os.makedirs("dimensoes", exist_ok=True)
dim_vendedor.to_csv("dimensoes/dim_vendedor.csv", index=False)

# Tratamento olist_orders_dataset para tabela de tempo
df_orders = pd.read_csv("olist_orders_dataset.csv")

dim_tempo = df_orders[["order_purchase_timestamp"]].dropna().drop_duplicates()
dim_tempo["data"] = pd.to_datetime(dim_tempo["order_purchase_timestamp"]).dt.date
dim_tempo["ano"] = pd.to_datetime(dim_tempo["order_purchase_timestamp"]).dt.year
dim_tempo["mes"] = pd.to_datetime(dim_tempo["order_purchase_timestamp"]).dt.month
dim_tempo["dia"] = pd.to_datetime(dim_tempo["order_purchase_timestamp"]).dt.day
dim_tempo["dia_semana"] = pd.to_datetime(dim_tempo["order_purchase_timestamp"]).dt.day_name()
dim_tempo["trimestre"] = pd.to_datetime(dim_tempo["order_purchase_timestamp"]).dt.quarter

dim_tempo = dim_tempo.drop(columns=["order_purchase_timestamp"]).drop_duplicates()

dim_tempo = dim_tempo.rename(columns={
    "data": "data",
    "ano": "ano",
    "mes": "mes",
    "dia": "dia",
    "dia_semana": "dia_da_semana",
    "trimestre": "trimestre"
})

os.makedirs("dimensoes", exist_ok=True)
dim_tempo.to_csv("dimensoes/dim_tempo.csv", index=False)

# ETL fato_vendas
df_items = pd.read_csv("olist_order_items_dataset.csv")
df_orders = pd.read_csv("olist_orders_dataset.csv")
df_payments = pd.read_csv("olist_order_payments_dataset.csv")
df_reviews = pd.read_csv("olist_order_reviews_dataset.csv")

# Join principal
fato_vendas = df_items.merge(df_orders[['order_id', 'customer_id', 'order_purchase_timestamp', 'order_delivered_customer_date']], 
                             on="order_id", how="left")

df_pagamentos_unicos = df_payments.drop_duplicates(subset=["order_id"])
fato_vendas = fato_vendas.merge(df_pagamentos_unicos, on="order_id", how="left")

df_reviews_simples = df_reviews[["order_id", "review_score"]].drop_duplicates()
fato_vendas = fato_vendas.merge(df_reviews_simples, on="order_id", how="left")

# Renomear colunas da fato
fato_vendas = fato_vendas.rename(columns={
    "order_id": "id_pedido",
    "customer_id": "id_cliente",
    "order_item_id": "id_item_pedido",
    "product_id": "id_produto",
    "seller_id": "id_vendedor",
    "price": "preco",
    "freight_value": "valor_frete",
    "payment_type": "tipo_pagamento",
    "payment_value": "valor_pagamento",
    "review_score": "nota_avaliacao",
    "order_purchase_timestamp": "data_compra",
    "order_delivered_customer_date": "data_entrega"
})

# Salvar fato
fato_vendas.to_csv("fato_vendas.csv", index=False)

# Download
from google.colab import files
files.download("fato_vendas.csv")

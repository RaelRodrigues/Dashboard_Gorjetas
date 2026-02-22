# -*- coding: utf-8 -*-
"""
Projeto 02

"""

# carregando os pacotes
import streamlit as st
import seaborn as sns
import pandas as pd
import altair as alt



# configuração da página
st.set_page_config(page_title = "Dashboard de Gorjetas", layout = "wide")




# carregando o dataset tips
tips = sns.load_dataset("tips")


# título do dashboard
st.title("Análise das Gorjetas")

# sidebar para filtros
st.sidebar.header("Filtros")


############ criando os filtros

# filtro por gênero
sex_options = ["Todos"] + list(tips["sex"].unique())
selected_sex = st.sidebar.selectbox("Filtrar por Gênero", sex_options)

# filtro por fumante
smoker_options = ["Todos"] + list(tips["smoker"].unique())
selected_smoker = st.sidebar.selectbox("Filtrar por Fumante", smoker_options)

# filtro por dia da semana
day_options = ["Todos"] + list(tips["day"].unique())
selected_day = st.sidebar.selectbox("Filtrar por Dia", day_options)

# filtro por horário
time_options = ["Todos"] + list(tips["time"].unique())
selected_time = st.sidebar.selectbox("Filtrar por Horário", time_options)


########## Aplicar os filtros
df_filtered = tips.copy()


if selected_sex != "Todos":
    df_filtered = df_filtered[df_filtered["sex"] == selected_sex]

if selected_smoker != "Todos":
    df_filtered = df_filtered[df_filtered["smoker"] == selected_smoker]

if selected_day != "Todos":
    df_filtered = df_filtered[df_filtered["day"] == selected_day]

if selected_time != "Todos":
    df_filtered = df_filtered[df_filtered["time"] == selected_time]
    
    
########## Exibindo os KPI's
st.subheader("Resumo das Gorjetas")

col1, col2, col3 = st.columns(3)

col1.metric("Valor Médio da Conta", f"$ {df_filtered['total_bill'].mean():.2f}")
col2.metric("Gorjeta Média", f"$ {df_filtered['tip'].mean():.2f}")
col3.metric("Tamanho Médio da Mesa", f"{df_filtered['size'].mean():.2f} pessoas")

# adicinando uma linha horizontal
st.markdown("---")


############# Criando os gráficos

# criano as duas primeiras colunas
coluna1, coluna2 = st.columns(2)

with coluna1:
    # gráfico da relação entre total da conta e da gorjeta
    st.markdown("Relação entre total da Conta e Gorjeta")
    
    scatter = alt.Chart(df_filtered).mark_circle(size = 80).encode(
        x = alt.X("total_bill:Q", title = "Total da Conta (USD"),
        y = alt.Y("tip:Q", title = "Gorjeta (USD)"),
        color = "sex:N",
        tooltip = ["total_bill", "tip", "sex", "day", "size"]
        ).properties(width = 700, height = 400)
    
    st.altair_chart(scatter, use_container_width=True)
    
    
with coluna2:
    # gráfico de distribuição do total da conta
    
    st.markdown("Distribuição do Total da Conta")
    
    hist = alt.Chart(df_filtered).mark_bar().encode(
        x = alt.X("total_bill:Q", bin = True, title = "Total da Conta (USD)"),
        y = alt.Y("count()", title = "Frequência"),
        color = alt.value("blue"),
        tooltip = ["count()"]
        ).properties(width = 700, height = 400)
    
    st.altair_chart(hist, use_container_width=True)



# criando o segundo conjunto de colunas
colunab1, colunab2 = st.columns(2)

# criar uma nova coluna com a porcentagem da gorjeta sobre o total da conta
df_filtered["tip_percent"] = (df_filtered["tip"] / df_filtered["total_bill"]) * 100

with colunab1:
    #criando um gráfico de dispersão
    chart = alt.Chart(df_filtered).mark_circle(size = 60).encode(
        x = alt.X("total_bill:Q", title = "Valor da Conta (USD)"),
        y = alt.Y("tip_percent:Q", title = "Gorjeta (%)"),
        color = "smoker:N", # diferença entre fumantes e não fumantes
        tooltip = ["total_bill", "tip", "tip_percent", "smoker"]
        ).properties(title = "Relação entre Valor da Conta e Percentual da Gorjeta",
                     width = 500, height = 350)
                     
    st.altair_chart(chart, use_container_width=True)


with colunab2:
    chart2 = alt.Chart(df_filtered).transform_density(
        density = "tip",
        groupby = ["time"],
        as_ = ["tip", "density"]
        ).mark_area(orient = "vertical", opacity = 0.5).encode(
            x = alt.X("tip:Q", title = "Valor da Gorjeta (USD)"),
            y = alt.Y("density:Q", title = "Densidade"),
            color = "time:N",
            tooltip = ["time", "tip"]
            ).properties(title = "Distribuição das Gorjetas por Horário",
                         width = 500, height = 350
                         )
                         
    st.altair_chart(chart2, use_container_width=True)


# calculando a média das gorjetas por status de fumante
df_grouped = df_filtered.groupby("smoker", as_index = False)["tip"].mean()

# criando um gráfico de barras
chart3 = alt.Chart(df_grouped).mark_bar().encode(
    x = alt.X("smoker:N", title = "Fumante", axis = alt.Axis(labelAngle = 0)),
    y = alt.Y("tip:Q", title = "Média da GOrjeta (USD)"),
    color = "smoker:N",
    tooltip = ["smoker", "tip"]
    ).properties(title = "Impacto do tabagismo no valor das gorjetas",
                 width = 400, height = 300
                 )
                 
st.altair_chart(chart3, use_container_width=True)


# adicionando uma linha horizontal
st.markdown("---")


# criando uma tabela agrupada com a média das gorjetas por dia e horário
tabela_gorjetas = df_filtered.groupby(["day", "time"]).agg(
    Gorjeta_Média = ("tip", "mean"),
    Conta_Média = ("total_bill", "mean"),
    Qtde_Pedidos = ("tip", "count")
    ).reset_index()

# formatando os valores em duas cadas decimais
tabela_gorjetas["Gorjeta_Média"] = tabela_gorjetas["Gorjeta_Média"].map(lambda x: f"${x:.2f}")
tabela_gorjetas["Conta_Média"] = tabela_gorjetas["Conta_Média"].map(lambda x: f"${x:.2f}")

# exibindo um título para a tabela
st.subheader("Média das Gorjetas por dia e horário")

st.dataframe(tabela_gorjetas, use_container_width=True)


# criando um expander para a tabela acima
with st.expander("Ver mais"):
    st.write(
        "Esta tabela mostra a gorjeta média, a conta média e a quantidade de pedidos "
        "agrupados por dia da semana e período do dia (almoço/jantar).")



# adicionando uma linha horizontal
st.markdown("---")

# tabela de dados filtrados
st.subheader("Dados Filtrados")
st.dataframe(df_filtered, use_container_width=True)





























import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry


def _iso2_to_iso3(iso_2):
    country = pycountry.countries.get(alpha_2=iso_2)
    if country:
        return country.alpha_3
    return iso_2  # Return the original code if not found


# Page configuration
st.set_page_config(
    page_title="Dashboard Salários na Área de Dados",
    page_icon=":bar_chart:",
    layout="wide",
)

# Data loading
df = pd.read_csv(
    "https://raw.githubusercontent.com/guilhermeonrails/data-jobs/refs/heads/main/salaries.csv"
)

# Rename columns for easier access
df = df.rename(
    columns={
        "work_year": "ano",
        "experience_level": "senioridade",
        "employment_type": "contrato",
        "job_title": "cargo",
        "salary": "salario",
        "salary_currency": "moeda",
        "salary_in_usd": "usd",
        "employee_residence": "residencia",
        "remote_ratio": "remoto",
        "company_location": "localizacao_empresa",
        "company_size": "tamanho_empresa",
    }
)

# Data preprocessing
df["senioridade"] = df["senioridade"].replace(
    {"SE": "Senior", "MI": "Pleno", "EN": "Junior", "EX": "Executivo"}
)
df["contrato"] = df["contrato"].replace(
    {
        "FT": "Tempo Integral",
        "CT": "Contrato",
        "PT": "Tempo Parcial",
        "FL": "Freelancer",
    }
)
df["remoto"] = df["remoto"].replace({0: "Presencial", 50: "Hibrido", 100: "Remoto"})
df["tamanho_empresa"] = df["tamanho_empresa"].replace(
    {"S": "Pequena", "M": "Media", "L": "Grande"}
)

# Remove rows with missing values
clean_df = df.dropna()
clean_df = clean_df.assign(ano=clean_df["ano"].astype("int64"))


# Sidebar configuration
st.sidebar.title("🔍 Filtros")


# Filter by year
years = sorted(clean_df["ano"].unique())
selected_years = st.sidebar.multiselect("Anos:", years, default=years)

# Filter by seniority
seniority_levels = sorted(clean_df["senioridade"].unique())
selected_seniority = st.sidebar.multiselect(
    "Senioridade:", seniority_levels, default=seniority_levels
)

# Filter by job type
job_types = sorted(clean_df["contrato"].unique())
selected_job_types = st.sidebar.multiselect("Contratos:", job_types, default=job_types)

# Filter by company size
company_sizes = sorted(clean_df["tamanho_empresa"].unique())
selected_company_sizes = st.sidebar.multiselect(
    "Tamanho da Empresa:", company_sizes, default=company_sizes
)

# Filter by all jobs or one job title
job_titles = ["Todos"] + sorted(clean_df["cargo"].unique())
selected_job_title = st.sidebar.selectbox("Cargo:", job_titles)
# add option all as default
filtered_df = clean_df[
    (clean_df["ano"].isin(selected_years))
    & (clean_df["senioridade"].isin(selected_seniority))
    & (clean_df["contrato"].isin(selected_job_types))
    & (clean_df["tamanho_empresa"].isin(selected_company_sizes))
]
# Filtering the DataFrame based on user selections
filtered_df = clean_df[
    (clean_df["ano"].isin(selected_years))
    & (clean_df["senioridade"].isin(selected_seniority))
    & (clean_df["contrato"].isin(selected_job_types))
    & (clean_df["tamanho_empresa"].isin(selected_company_sizes))
]

# Main content
st.title("🎲 Dashboard Salários na Área de Dados 🎲")
st.markdown(
    """**Este dashboard apresenta uma análise dos salários na área de dados, com base em dados coletados de profissionais da área.**\n\nUtilize os filtros na barra lateral para explorar diferentes aspectos dos salários, como ano, senioridade, tipo de contrato e tamanho da empresa. \n\n Origim dos dados: https://raw.githubusercontent.com/guilhermeonrails/data-jobs/refs/heads/main/salaries.csv
    \n\nExplore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise."""
)

if not filtered_df.empty:
    mean_salary = filtered_df.groupby("ano")["usd"].mean()
    max_salary = filtered_df.groupby("ano")["usd"].max()
    min_salary = filtered_df.groupby("ano")["usd"].min()
    median_salary = filtered_df.groupby("ano")["usd"].median()
    total_entries = filtered_df.shape[0]
    most_common_job = filtered_df["cargo"].mode()[0]
else:
    mean_salary = pd.Series(dtype=float)
    max_salary = pd.Series(dtype=float)
    min_salary = pd.Series(dtype=float)
    median_salary = pd.Series(dtype=float)
    total_entries = 0
    most_common_job = "N/A"

row0_col0, row0_col1, row0_col2 = st.columns(3)
row1_col0, row1_col1, row1_col2 = st.columns(3)
row0_col0.metric("Média Salarial (USD)", f"${mean_salary.mean():,.2f}")
row0_col1.metric("Salário Máximo (USD)", f"${max_salary.max():,.2f}")
row0_col2.metric("Salário Mínimo (USD)", f"${min_salary.min():,.2f}")
row1_col0.metric("Mediana Salarial (USD)", f"${median_salary.median():,.2f}")
row1_col1.metric("Total de Entradas", total_entries)
row1_col2.metric("Cargo Mais Comum", most_common_job)

st.markdown(" ------ ")
st.subheader("📊 Gráficos")

col_graph0, col_graph1 = st.columns(2)
with col_graph0:
    if not filtered_df.empty:
        top_cargos = (
            filtered_df.groupby("cargo")["usd"]
            .mean()
            .nlargest(10)
            .sort_values(ascending=True)
            .reset_index()
        )
        graph_cargos = px.bar(
            top_cargos,
            x="usd",
            y="cargo",
            orientation="h",
            title="Top 10 Cargos por Média Salarial (USD)",
            color="cargo",  # use cargo as the color category
            color_discrete_sequence=px.colors.sequential.Plasma,
            template="plotly_white",
        )
        graph_cargos.update_layout(
            xaxis_title="Média Salarial (USD)",
            title_x=0.1,
            yaxis_title="Cargo",
            yaxis={"categoryorder": "total ascending"},
        )
        st.plotly_chart(graph_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de cargos.")

with col_graph1:
    if not filtered_df.empty:
        hist_graph = px.histogram(
            filtered_df,
            x="usd",
            nbins=30,
            title="Distribuição de salários anuais",
            labels={"usd": "Faixa salarial (USD)", "count": ""},
        )
        hist_graph.update_layout(title_x=0.1)
        st.plotly_chart(hist_graph, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de localizações.")

st.markdown(" ------ ")

col_graph2, col_graph3 = st.columns(2)
with col_graph2:
    if not filtered_df.empty:
        count_remote = filtered_df["remoto"].value_counts().reset_index()
        count_remote.columns = ["Tipo de Trabalho", "Quantidade"]
        remote_graph = px.pie(
            count_remote,
            values="Quantidade",
            names="Tipo de Trabalho",
            title="Proporção de Tipos de Trabalho Remoto",
            hole=0.5,
        )
        remote_graph.update_traces(textposition="inside", textinfo="percent+label")
        remote_graph.update_layout(title_x=0.1)
        st.plotly_chart(remote_graph, use_container_width=True)
    else:
        st.warning(
            "Nenhum dado disponível para exibir o gráfico de tipos de trabalho remoto."
        )

st.markdown(" ------ ")
st.subheader("🗃️ Salários por países")

if selected_job_title != "Todos":
    filtered_df = filtered_df[filtered_df["cargo"] == selected_job_title]

# Convert ISO2 to ISO3 for mapping
filtered_df["residencia_iso3"] = filtered_df["residencia"].apply(_iso2_to_iso3)

# Filter only one role
df_data_scientist = (
    filtered_df[filtered_df["cargo"] == selected_job_title]
    if selected_job_title != "Todos"
    else filtered_df
)
# Calculate average salary by country
avg_salary_by_country = (
    df_data_scientist.groupby("residencia_iso3")["usd"].mean().round(2).reset_index()
)

bar_fig = px.bar(
    avg_salary_by_country,
    x="residencia_iso3",
    y="usd",
    title=f"Média salarial para {selected_job_title} por país",
    labels={"residencia_iso3": "País", "usd": "Média Salarial Anual (USD)"},
    color="usd",
    color_continuous_scale=px.colors.sequential.Plasma,
)
bar_fig.update_layout(xaxis={"categoryorder": "total descending"})

map_fig = px.choropleth(
    avg_salary_by_country,
    locations="residencia_iso3",
    locationmode="ISO-3",
    color="usd",
    hover_name="residencia_iso3",
    title=f"Média Salarial Anual (USD) para {selected_job_title} por País",
    color_continuous_scale=px.colors.sequential.Plasma,
)
map_fig.update_layout(
    title_x=0.1,
)

col_graph4, col_graph5 = st.columns(2)
with col_graph4:
    st.plotly_chart(bar_fig, use_container_width=True)
with col_graph5:
    st.plotly_chart(map_fig, use_container_width=True)


st.markdown(" ------ ")
st.subheader("📁 Dados brutos")
st.dataframe(filtered_df, use_container_width=True)
clean_df.to_csv("dados_final.csv", index=False)

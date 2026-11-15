import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Malaysia Socioeconomic Visualization",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    df = pd.read_csv("merged_data_2017_2024.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year

    # Marriage is split by sex. Sum marriage counts, but keep population and income once.
    summary = (
        df.groupby(["state", "year"], as_index=False)
          .agg(
              marriages=("abs", "sum"),
              population=("population", "first"),
              income_mean=("income_mean", "first"),
              income_median=("income_median", "first")
          )
    )

    # Dataset population is in thousands.
    summary["marriage_per_1000"] = summary["marriages"] / summary["population"]
    return df, summary

raw_df, data = load_data()

st.title("Malaysia Population, Marriage and Household Income")
st.caption("Scientific Visualization Dashboard | OpenDOSM data merged by state and year")

available_years = sorted(data["year"].unique())
selected_year = st.sidebar.selectbox("Select year", available_years, index=len(available_years) - 1)
page = st.sidebar.radio(
    "Select objective",
    [
        "Objective 1: Population & Income",
        "Objective 2: Population & Marriage",
        "Objective 3: Income & Marriage"
    ]
)

year_df = data[data["year"] == selected_year].copy()

st.sidebar.markdown("---")
st.sidebar.write(f"Showing data for **{selected_year}**")
st.sidebar.write(f"States/territories: **{year_df['state'].nunique()}**")

if page == "Objective 1: Population & Income":
    st.header("Objective 1: Population and Household Income")
    st.write(
        "To examine the relationship between population size and mean household income "
        "across Malaysian states."
    )

    highest_income = year_df.loc[year_df["income_mean"].idxmax()]
    largest_population = year_df.loc[year_df["population"].idxmax()]
    correlation = year_df["population"].corr(year_df["income_mean"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Highest mean income", f"RM {highest_income['income_mean']:,.0f}", highest_income["state"])
    c2.metric("Largest population", f"{largest_population['population']:,.1f} thousand", largest_population["state"])
    c3.metric("Population-income correlation", f"{correlation:.2f}")

    fig1 = px.scatter(
        year_df, x="population", y="income_mean", text="state", size="population",
        color="income_mean", title=f"Population vs Mean Household Income ({selected_year})",
        labels={"population": "Population (thousand)", "income_mean": "Mean household income (RM)", "state": "State"}
    )
    fig1.update_traces(textposition="top center")
    st.plotly_chart(fig1, use_container_width=True)

    sorted_income = year_df.sort_values("income_mean", ascending=True)
    fig2 = px.bar(
        sorted_income, x="income_mean", y="state", orientation="h", color="income_mean",
        title=f"Mean Household Income by State ({selected_year})",
        labels={"income_mean": "Mean household income (RM)", "state": "State"}
    )
    st.plotly_chart(fig2, use_container_width=True)

    trend_state = st.selectbox("Choose a state for the population-income trend", sorted(data["state"].unique()), key="obj1_state")
    trend = data[data["state"] == trend_state]
    fig3 = px.line(
        trend, x="year", y=["population", "income_mean"], markers=True,
        title=f"Population and Income Trend: {trend_state}",
        labels={"value": "Value", "year": "Year", "variable": "Indicator"}
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.info(
        "Interpretation guide: A positive correlation means states with larger populations tend to have higher household income. "
        "A value near zero indicates little linear relationship. Correlation does not prove causation."
    )

elif page == "Objective 2: Population & Marriage":
    st.header("Objective 2: Population and Marriage")
    st.write(
        "To evaluate the relationship between population size and the number and rate of marriages "
        "across Malaysian states."
    )

    most_marriages = year_df.loc[year_df["marriages"].idxmax()]
    highest_rate = year_df.loc[year_df["marriage_per_1000"].idxmax()]
    correlation = year_df["population"].corr(year_df["marriages"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Highest marriage count", f"{most_marriages['marriages']:,.0f}", most_marriages["state"])
    c2.metric("Highest marriage rate", f"{highest_rate['marriage_per_1000']:.1f} per 1,000", highest_rate["state"])
    c3.metric("Population-marriage correlation", f"{correlation:.2f}")

    fig1 = px.scatter(
        year_df, x="population", y="marriages", text="state", size="marriages",
        color="marriage_per_1000", title=f"Population vs Number of Marriages ({selected_year})",
        labels={"population": "Population (thousand)", "marriages": "Number of marriages",
                "marriage_per_1000": "Marriages per 1,000", "state": "State"}
    )
    fig1.update_traces(textposition="top center")
    st.plotly_chart(fig1, use_container_width=True)

    sorted_rate = year_df.sort_values("marriage_per_1000", ascending=True)
    fig2 = px.bar(
        sorted_rate, x="marriage_per_1000", y="state", orientation="h", color="marriage_per_1000",
        title=f"Marriage Rate by State ({selected_year})",
        labels={"marriage_per_1000": "Marriages per 1,000 population", "state": "State"}
    )
    st.plotly_chart(fig2, use_container_width=True)

    selected_states = st.multiselect(
        "Choose states for marriage trend", sorted(data["state"].unique()),
        default=sorted(data["state"].unique())[:3], key="obj2_states"
    )
    trend = data[data["state"].isin(selected_states)]
    fig3 = px.line(
        trend, x="year", y="marriages", color="state", markers=True,
        title="Marriage Count Trend by Selected States",
        labels={"year": "Year", "marriages": "Number of marriages", "state": "State"}
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.info(
        "Interpretation guide: Compare the total marriage count with the standardized marriage rate. "
        "A state may have many marriages mainly because its population is large, while another state may have a higher rate."
    )

else:
    st.header("Objective 3: Household Income and Marriage")
    st.write(
        "To investigate the relationship between household income and marriage patterns "
        "across Malaysian states."
    )

    highest_income = year_df.loc[year_df["income_mean"].idxmax()]
    highest_rate = year_df.loc[year_df["marriage_per_1000"].idxmax()]
    correlation = year_df["income_mean"].corr(year_df["marriage_per_1000"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Highest mean income", f"RM {highest_income['income_mean']:,.0f}", highest_income["state"])
    c2.metric("Highest marriage rate", f"{highest_rate['marriage_per_1000']:.1f} per 1,000", highest_rate["state"])
    c3.metric("Income-rate correlation", f"{correlation:.2f}")

    fig1 = px.scatter(
        year_df, x="income_mean", y="marriage_per_1000", text="state", size="population",
        color="marriages", title=f"Mean Household Income vs Marriage Rate ({selected_year})",
        labels={"income_mean": "Mean household income (RM)",
                "marriage_per_1000": "Marriages per 1,000 population",
                "population": "Population (thousand)", "marriages": "Number of marriages", "state": "State"}
    )
    fig1.update_traces(textposition="top center")
    st.plotly_chart(fig1, use_container_width=True)

    compare = year_df.sort_values("income_mean", ascending=False)
    fig2 = px.bar(
        compare, x="state", y=["income_mean", "income_median"], barmode="group",
        title=f"Mean and Median Household Income by State ({selected_year})",
        labels={"value": "Household income (RM)", "state": "State", "variable": "Income measure"}
    )
    st.plotly_chart(fig2, use_container_width=True)

    corr_data = year_df[["population", "marriages", "marriage_per_1000", "income_mean", "income_median"]].corr()
    fig3 = px.imshow(
        corr_data, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
        title=f"Correlation Heatmap ({selected_year})"
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.info(
        "Interpretation guide: Focus on whether household income is associated with the marriage rate, rather than only the raw marriage count. "
        "Discuss outlier states separately and avoid claiming that income directly causes marriage patterns."
    )

with st.expander("View processed data"):
    st.dataframe(year_df.sort_values("state"), use_container_width=True)

st.caption("Source: OpenDOSM datasets processed and merged by state and year.")

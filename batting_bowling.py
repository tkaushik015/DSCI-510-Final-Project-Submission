import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

# Loading the datasets
@st.cache_data
def load_data():
    bowling_data = pd.read_csv("2023_bowling.csv")
    batting_data = pd.read_csv("2023_batting.csv")
    return bowling_data, batting_data

# Getting data
bowling_data, batting_data = load_data()

# Helper function to filter bowling data
def filter_bowling_data(data, player_name=None, teams=None, econ_range=None, avg_range=None):
    if player_name:
        data = data[data['Name'].str.contains(player_name, case=False)]
    if teams:
        data = data[data['2023_Team'].isin(teams)]
    if econ_range:
        data = data[(data['Economy'] >= econ_range[0]) & (data['Economy'] <= econ_range[1])]
    if avg_range:
        data = data[(data['Average'] >= avg_range[0]) & (data['Average'] <= avg_range[1])]
    return data

# Helper function to filter batting data
def filter_batting_data(data, player_name=None, teams=None, sr_range=None, hs_range=None):
    if player_name:
        data = data[data['Name'].str.contains(player_name, case=False)]
    if teams:
        data = data[data['2023_Team'].isin(teams)]
    if sr_range:
        data = data[(data['Strike_rate'] >= sr_range[0]) & (data['Strike_rate'] <= sr_range[1])]
    if hs_range:
        data = data[(data['Highest_score'] >= hs_range[0]) & (data['Highest_score'] <= hs_range[1])]
    return data

# Main interface setup
st.sidebar.header("Analysis Options")
analysis_type = st.sidebar.selectbox("Choose Analysis Type", options=["Bowling", "Batting", "Comparison"])

if analysis_type == "Bowling":
    # Sidebar inputs for bowling analysis
    player_name = st.sidebar.text_input("Player Name")
    teams = st.sidebar.multiselect("Teams", options=bowling_data['2023_Team'].unique())
    econ_range = st.sidebar.slider("Economy Rate Range", 0.0, 10.0, (0.0, 10.0))
    avg_range = st.sidebar.slider("Average Range", 0, 50, (0, 50))

    # Filtering bowling data based on inputs
    filtered_data = filter_bowling_data(bowling_data, player_name, teams, econ_range, avg_range)

    st.header("IPL 2023 Bowling Performance")

    if not filtered_data.empty:
        # Displaying filtered data
        st.write("Filtered Data")
        st.dataframe(filtered_data)

        # Visualization : Top Wicket-Takers
        st.subheader("Top Wicket-Takers")
        top_wicket_takers = filtered_data.nlargest(10, "Wickets")
        fig, ax = plt.subplots()
        sns.barplot(data=top_wicket_takers, x="Name", y="Wickets", ax=ax)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig)

        # Visualization : Economy Rate Distribution
        st.subheader("Economy Rate Distribution")
        fig, ax = plt.subplots()
        sns.histplot(data=filtered_data, x="Economy", kde=True, ax=ax)
        plt.tight_layout()
        st.pyplot(fig)

        # Visualization : Strike Rate Analysis
        st.subheader("Strike Rate Analysis")
        fig, ax = plt.subplots()
        sns.boxplot(data=filtered_data, x="2023_Team", y="Strike_Rate", ax=ax)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig)

        # Visualization: Comparison by Country
        st.subheader("Comparison by Country")
        country_stats = filtered_data.groupby("Country")[['Wickets', 'Economy', 'Strike_Rate']].mean().reset_index()
        fig, ax = plt.subplots()
        country_stats.plot(kind="bar", x="Country", stacked=True, ax=ax)
        plt.tight_layout()
        st.pyplot(fig)

        # Visualization: Correlation Heatmap
        st.subheader("Correlation Heatmap")
        corr = filtered_data[['Average', 'Economy', 'Strike_Rate', 'Wickets']].corr()
        fig, ax = plt.subplots()
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        plt.tight_layout()
        st.pyplot(fig)

    else:
        st.warning("No data matches your filters.")

elif analysis_type == "Batting":
    # Sidebar inputs for batting analysis
    player_name = st.sidebar.text_input("Player Name")
    teams = st.sidebar.multiselect("Teams", options=batting_data['2023_Team'].unique())
    sr_range = st.sidebar.slider("Strike Rate Range", 0.0, 200.0, (0.0, 200.0))
    hs_range = st.sidebar.slider("Highest Score Range", 0, 200, (0, 200))

    # Filtered batting data based on inputs
    filtered_data = filter_batting_data(batting_data, player_name, teams, sr_range, hs_range)

    st.header("IPL 2023 Batting Performance")

    if not filtered_data.empty:
        # Display filtered data
        st.write("Filtered Data")
        st.dataframe(filtered_data)

        # Visualization: Top Run Scorers
        st.subheader("Top Run Scorers")
        filtered_data["Total_Runs"] = filtered_data["Innings"] * filtered_data["Highest_score"]
        top_run_scorers = filtered_data.nlargest(10, "Total_Runs")
        fig, ax = plt.subplots()
        sns.barplot(data=top_run_scorers, x="Name", y="Total_Runs", ax=ax)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig)

        # Visualization: Strike Rate Distribution
        st.subheader("Strike Rate Distribution")
        fig, ax = plt.subplots()
        sns.histplot(data=filtered_data, x="Strike_rate", kde=True, ax=ax)
        plt.tight_layout()
        st.pyplot(fig)

        # Visualization: Comparison by Country
        st.subheader("Comparison by Country")
        country_stats = filtered_data.groupby("Country")[['Strike_rate', 'Fifties', 'Hundreds']].mean().reset_index()
        fig, ax = plt.subplots()
        country_stats.plot(kind="bar", x="Country", stacked=True, ax=ax)
        plt.tight_layout()
        st.pyplot(fig)

        # Visualization: Correlation Heatmap
        st.subheader("Correlation Heatmap")
        corr = filtered_data[['Strike_rate', 'Hundreds', 'Fifties', 'Fours', 'Sixes']].corr()
        fig, ax = plt.subplots()
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        plt.tight_layout()
        st.pyplot(fig)

    else:
        st.warning("No data matches your filters.")

elif analysis_type == "Comparison":
    st.header("2022 vs 2023 Team Comparison")

    # Comparing metrics between 2022 and 2023 teams based on new players
    def compare_team_performance(new_data, original_data, compare_metric):
        # Merging dataframes to compare key metrics
        merged_data = new_data.merge(original_data, how="inner", on=["2022_Team", "2023_Team", "Country"], suffixes=("", "_2022"))
        merged_data[f"{compare_metric}_Difference"] = merged_data[compare_metric] - merged_data[f"{compare_metric}_2022"]

        return merged_data

    comparison_metric = "Wickets"  # You can refine or change this metric
    team_comparison = compare_team_performance(bowling_data, batting_data, comparison_metric)

    if not team_comparison.empty:
        st.write("Team Comparison")
        st.dataframe(team_comparison)

        st.subheader("Performance Differences")
        fig, ax = plt.subplots()
        sns.barplot(data=team_comparison, x="Country", y=f"{comparison_metric}_Difference", ax=ax)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig)

    else:
        st.warning("No sufficient comparative metrics.")

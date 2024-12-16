import pandas as pd
import plotly.express as px
import streamlit as st

from processing import get_top_50_watched_videos

st.title("YouTube Wrapped")

uploaded_file = st.file_uploader(
    "Upload your YouTube Watch History CSV file", type="csv"
)
if uploaded_file:
    try:
        # # Process JSON file
        # data = pd.read_json(uploaded_file)
        # data = load_watch_history(data)
        # # Example stats (replace this with your logic)
        # yearly_stats = get_top_50_watched_videos(data, 2024)

        # # Process csv file
        data = pd.read_csv(uploaded_file)
        # Example stats (replace this with your logic)
        yearly_stats = get_top_50_watched_videos(data, 2024)

        # Display stats
        st.write("### Stats by Creator")
        st.dataframe(yearly_stats)

        # Display top creators by time watched in vertical bar chart, highest to lowest
        st.write("### Top Creators by Time Watched")
        fig = px.bar(
            yearly_stats,
            x=yearly_stats.index,
            y="adjusted_duration",
            title="Top Creators by Time Watched",
            labels={"x": "Creator", "y": "Adjusted Duration (mins)"},
        )
        st.plotly_chart(fig)

        # Prepare data for the Treemap
        # Filter the top 10 creators
        # copy yearly_stats to treemap_df
        treemap_df = yearly_stats.copy()
        # top_creators = yearly_stats.nlargest(10, 'adjusted_duration')
        yearly_stats["minutes"] = yearly_stats["adjusted_duration"] / 60
        yearly_stats["hours"] = yearly_stats["minutes"] / 60
        yearly_stats = yearly_stats[yearly_stats["hours"] != 0]
        # rename everything outside the top 20 to "other"
        yearly_stats = yearly_stats.reset_index()
        yearly_stats.loc[
            ~yearly_stats.index.isin(yearly_stats.nlargest(20, "hours").index), "name"
        ] = "Other"
        total_duration = yearly_stats["hours"].sum()
        fig = px.treemap(
            yearly_stats,
            path=["name"],
            values="hours",
            title=f"You watched {int(total_duration)} hours of YouTube! That's more than "
            + f"{int(total_duration/24)} days!"
            if total_duration > 48
            else f"You watched {int(total_duration)} hours!",
            color="hours",
            color_continuous_scale="Blues",
        )

        # Display in Streamlit
        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"An error occurred: {e}")

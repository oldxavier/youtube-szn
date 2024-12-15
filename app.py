import streamlit as st
import pandas as pd
from processing import load_watch_history, get_top_50_watched_videos
import plotly.express as px


st.title("YouTube Wrapped")

uploaded_file = st.file_uploader("Upload your YouTube Watch History CSV file", type="csv")
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

        # Display top creators by time watched
        st.write("### Top Creators by Total Time Watched")
        import pdb; pdb.set_trace()
        st.bar_chart(yearly_stats['adjusted_duration'])

        # Prepare data for the Treemap
        # Filter the top 10 creators
        top_creators = yearly_stats.nlargest(10, 'adjusted_duration')
        total_duration = yearly_stats['adjusted_duration'].sum()
        yearly_stats['percentage'] = (yearly_stats['adjusted_duration'] / total_duration) * 100
        top_creators = top_creators.reset_index()
        fig = px.treemap(
            top_creators,
            path=['name'],
            values='adjusted_duration',
            title=f"Top 10 Creators (Total Duration: {total_duration} mins)",
            color='adjusted_duration',
            color_continuous_scale='Blues'
        )

        # Display in Streamlit
        st.plotly_chart(fig)
    
    except Exception as e:
            st.error(f"An error occurred: {e}")

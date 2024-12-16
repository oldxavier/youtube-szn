import json

import isodate
import pandas as pd
import requests
from tqdm import tqdm

API_KEY = "AIzaSyBDS3Hn-Tl97Ihxms6XZkd6fXEZjeSL3Yw"


def load_watch_history(json_file_name: str):
    with open(f"{json_file_name}.json") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    # get 'name' from subtitles - subtitles in in the format of [{'name': 'value', 'language': 'value'}]
    df["name"] = df["subtitles"].apply(
        lambda x: x[0]["name"] if isinstance(x, list) else None
    )
    # keep only time, name and titleUrl but rename it to 'url'
    df = df[["time", "name", "titleUrl"]].rename(columns={"titleUrl": "url"})
    # keep only non-null names, times and urls
    df = df[df["name"].notnull()]
    df = df[df["time"].notnull()]
    df = df[df["url"].notnull()]
    # convert time to datetime
    df["time"] = pd.to_datetime(df["time"].str[:19])
    # keep only rows where the url contains '=' which means it has a video id
    df = df[df["url"].str.contains("=")]
    # extract the video id from the url
    df["video_id"] = df["url"].apply(lambda x: x.split("=")[1])
    # get list of video ids
    video_ids = df["video_id"].tolist()
    # create chunks of 50 video ids to feed to the api
    chunks = [video_ids[i : i + 50] for i in range(0, len(video_ids), 50)]
    # get the duration of each video
    durations = {}
    for chunk in tqdm(chunks):
        durations.update(_get_video_durations(chunk))
    df["duration"] = df["video_id"].map(durations)
    df["duration"] = df["duration"].fillna(0)
    # calculate adjusted duration
    df = df.sort_values(by=["time"])
    # calculate the time between each video
    df["time_diff"] = df["time"].diff().dt.total_seconds()
    # adjust durations
    df["adjusted_duration"] = df.apply(
        lambda row: min(row["duration"], row["time_diff"]), axis=1
    )
    # save
    df.to_csv(f"{json_file_name}-processed.csv", index=False)


def _get_video_durations(video_ids):
    """Fetch the duration of a YouTube video using the YouTube Data API."""
    ids = ",".join(video_ids)

    url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={ids}&key={API_KEY}"
    response = requests.get(url)

    data = response.json()
    results = {}
    for item in data.get("items", []):
        video_id = item["id"]
        duration = item["contentDetails"]["duration"]
        duration_seconds = isodate.parse_duration(duration).total_seconds()
        results[video_id] = duration_seconds

    # Handle IDs that weren't found
    for vid in video_ids:
        if vid not in results:
            results[vid] = None
    return results


def get_top_50_watched_videos(df: pd.DataFrame, year: int | None = None):
    # df = pd.read_csv(f"data/{csv_file_name}.csv")
    if year:
        # time column is datetime, so we can filter by year
        df["time"] = pd.to_datetime(df["time"])
        df = df[df["time"].dt.year == year]
    adf = df.groupby("name").agg(
        {"adjusted_duration": "sum", "video_id": pd.Series.nunique}
    )
    output = adf.sort_values(by="adjusted_duration", ascending=False)
    return output


if __name__ == "__main__":
    # load_watch_history(json_file_name = "salga-watch-history")
    get_top_50_watched_videos("watch-history-processed", 2024)

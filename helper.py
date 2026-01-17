from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
import streamlit as st


# URL extractor object
extractor = URLExtract()


def get_total_words(messages):
    words = []
    for word in messages:
        words.extend(word.split())
    return words


def fecth_stats(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    num_messages = df.shape[0]
    num_words = get_total_words(df["message"])
    num_media = df[df["message"] == "<Media omitted>\n"].shape[0]
    str_words = " ".join(get_total_words(df["message"]))
    num_links = extractor.find_urls(str_words)

    return num_messages, len(num_words), num_media, len(num_links)


def fetch_most_busy_user(df):
    busy_user_df = df["user"].value_counts().head()
    busy_user_percent_df = (
        round((df["user"].value_counts() / df.shape[0]) * 100, 2)
        .reset_index()
        .rename(columns={"index": "user", "user": "percent"})
    )
    return busy_user_df, busy_user_percent_df


def create_wordcloud(selected_user, df):
    f = open("stop_hinglish.txt", "r")
    stop_words = f.read()
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    temp = df[df["user"] != "group_notification"]
    temp = temp[temp["message"] != "<Media omitted>\n"]

    def remove_stopwords(message):
        words = []
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
        return " ".join(words)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color="white")
    temp["message"] = temp["message"].apply(remove_stopwords)
    df_wc = wc.generate(temp["message"].str.cat(sep=" "))
    return df_wc


def most_common_words(selected_user, df):
    f = open("stop_hinglish.txt", "r")
    stop_words = f.read()

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    temp = df[df["user"] != "group_notification"]
    temp = temp[temp["message"] != "<Media omitted>\n"]

    words = []
    for message in temp["message"]:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20)).rename(
        columns={0: "word", 1: "freq"}
    )
    return most_common_df


def emoji_helper(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    emojis = []
    for message in df["message"]:
        emojis.extend([c for c in message if emoji.is_emoji(c)])

    emoji_df = pd.DataFrame(Counter(emojis).most_common()).rename(
        columns={0: "emoji", 1: "freq"}
    )
    return emoji_df


def concat(a, b):
    return str(a) + "-" + str(b)


def monthly_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    timeline = df.groupby(["year", "month_num"]).count()["message"].reset_index()

    # Create YYYY-MM label
    timeline["year_month"] = (
        timeline["year"].astype(str)
        + "-"
        + timeline["month_num"].astype(str).str.zfill(2)
    )

    # Sort properly
    timeline = timeline.sort_values(["year", "month_num"])

    return timeline


def daily_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    daily_timeline = df.groupby("only_date").count()["message"].reset_index()

    return daily_timeline


def week_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    return df["day_name"].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    df["year_month"] = (
        df["year"].astype(str) + "-" + df["month_num"].astype(str).str.zfill(2)
    )

    return df["year_month"].value_counts().sort_index()


def user_heatmap(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    activity_heatmap = df.pivot_table(
        index="day_name", columns="period", values="message", aggfunc="count"
    ).fillna(0)

    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    activity_heatmap = activity_heatmap.reindex(day_order)

    return activity_heatmap


def get_instructions():
    st.title("How to Get Insights from Your WhatsApp Chat")
    st.text("Step 1: Open WhatsApp on your device")
    st.text(
        """Step 2: Choose the chat you want to analyze, whether it's a group chat or an 
        individual conversation."""
    )
    st.text(
        "Step 3: In the chat, tap on the three dots (menu icon) in the top right corner."
    )
    st.text(
        "Step 4: Select " "Export Chat" " from the menu options with without media."
    )
    st.text("Step 5: Upload the .txt file.")
    st.text(
        """Step 6: You'll be prompted to choose whether you want insights for the overall
        group or the individual chat. Make your selection."""
    )
    st.text("Step 6: After selecting your options, tap on " "Show Analysis" "")
    st.markdown(
        """\n\n *Note: None of your chats or the results obtained from them are stored or shared 
        with any third party for monetary gain. Your privacy and data security are 
        our top priorities.*"""
    )

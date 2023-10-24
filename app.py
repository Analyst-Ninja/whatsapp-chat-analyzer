import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns


st.sidebar.title("WhatsApp Chat Analyzer")


uploaded_file = st.sidebar.file_uploader("Upload a file")
if uploaded_file is None:
    helper.get_instructions()

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # fetch unique users
    user_list = df["user"].unique().tolist()
    user_list.remove("group_notification")
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)
    num_messages, num_words, num_media, num_links = helper.fecth_stats(
        selected_user, df
    )

    if st.sidebar.button("Show Analysis"):
        # Stats Area
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(f"{num_messages}")

        with col2:
            st.header("Total Words")
            st.title(f"{num_words}")

        with col3:
            st.header("Media Shared")
            st.title(f"{num_media}")

        with col4:
            st.header("Links Shared")
            st.title(f"{num_links}")

        # Timeline Statistics

        # Monthly timeline

        st.title("Monthly Timeline")
        monthly_timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(monthly_timeline["time"], monthly_timeline["message"], color="green")
        plt.xticks(rotation="vertical")
        st.pyplot(fig)

        # Daily Timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline["only_date"], daily_timeline["message"], color="black")
        plt.xticks(rotation="vertical")
        st.pyplot(fig)

        # Activity Map

        st.title("Activity Map")

        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)

            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            plt.xticks(rotation="vertical")
            st.pyplot(fig)

        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)

            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color="orange")
            plt.xticks(rotation="vertical")
            st.pyplot(fig)

        # finding the busiest user in the group (Group Level)

        if selected_user == "Overall":
            busy_users, busy_users_percent = helper.fetch_most_busy_user(df)

            fig, ax = plt.subplots()

            st.title("Most busy users")
            col1, col2 = st.columns(2)

            with col1:
                ax.bar(busy_users.index, busy_users.values, color="red")
                plt.xticks(rotation="vertical")
                st.pyplot(fig)

            with col2:
                st.dataframe(busy_users_percent)

        # Wordcloud
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # most common words
        most_common_df = helper.most_common_words(selected_user, df)

        fig, ax = plt.subplots()
        ax.barh(most_common_df["word"], most_common_df["freq"])
        plt.xticks(rotation="vertical")

        st.title("Most Common Words")
        st.pyplot(fig)

        # Emoji Analysis
        emoji_df = helper.emoji_helper(selected_user, df)

        st.title("Emoji Analysis")
        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:
            fig, ax = plt.subplots()
            ax.pie(
                emoji_df["freq"].head(),
                labels=emoji_df["emoji"].head(),
                autopct="%0.2f",
            )
            st.pyplot(fig)

        # Activity Heatmap
        st.title("Weekly Activity Map")
        user_heatmap = helper.user_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        plt.yticks(rotation="horizontal")
        plt.ylabel("Day")
        plt.xlabel("Period")
        st.pyplot(fig)

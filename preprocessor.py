import pandas as pd
import re


def preprocess(data):
    pattern = (
        r"(?:\[\s*)?"  # optional [
        r"(\d{1,2}/\d{1,2}/\d{2,4}),\s*"  # date
        r"(\d{1,2}:\d{2}(?::\d{2})?)"  # time (HH:MM or HH:MM:SS)
        r"(?:\s?(AM|PM|am|pm))?"  # optional AM/PM
        r"(?:\s*\])?"  # optional ]
        r"(?:\s*-\s*)?"  # optional " - "
    )

    matches = list(re.finditer(pattern, data))

    dates = []
    messages = []

    for i, match in enumerate(matches):
        date_part = match.group(1)
        time_part = match.group(2)
        am_pm = match.group(3) or ""

        timestamp = f"{date_part}, {time_part} {am_pm}".strip()
        dates.append(timestamp)

        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(data)
        messages.append(data[start:end].strip())

    df = pd.DataFrame({"user_message": messages, "message_date": dates})

    df["message_date"] = pd.to_datetime(
        df["message_date"], format="mixed", dayfirst=True
    )

    messages = []
    users = []
    for message in df["user_message"]:
        entry = re.split("([\w\W]+?): ", message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append("group_notification")
            messages.append(entry[0])
    df["user"] = users
    df["message"] = messages
    df.drop(columns=["user_message"], inplace=True)
    df["year"] = df["message_date"].dt.year
    df["month"] = df["message_date"].dt.month_name()
    df["month_num"] = df["message_date"].dt.month
    df["day"] = df["message_date"].dt.day
    df["day_name"] = df["message_date"].dt.day_name()
    df["hour"] = df["message_date"].dt.hour
    df["minute"] = df["message_date"].dt.minute
    df["only_date"] = df["message_date"].dt.date
    df["day_num"] = df["message_date"].dt.dayofweek

    # print(df[["hour"]].head())

    df["period"] = df["hour"].apply(lambda h: f"{h:02d}-{(h + 1) % 24:02d}")
    hour_order = [f"{h:02d}-{(h + 1) % 24:02d}" for h in range(24)]
    df["period"] = pd.Categorical(df["period"], categories=hour_order, ordered=True)

    return df

import pandas as pd
import re


def preprocess(data):
    if data[:25].find("pm") != -1 or data[:25].find("am") != -1:
        # pattern for chat with time in AM PM format
        pattern = "\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\u202f[ap]m\s-\s"
    else:
        # pattern for chat with time in HRS format
        pattern = "\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s"
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    modified_dates = [word.replace("\u202f", " ")[:-3] for word in dates]
    df = pd.DataFrame({"user_message": messages, "message_date": modified_dates})
    df["message_date"] = pd.to_datetime(df["message_date"], format="%d/%m/%y, %I:%M %p")

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

    period = []
    for hour in df[["day_name", "hour"]]["hour"]:
        if hour == 23:
            period.append(str(hour).zfill(2) + "-" + str("00").zfill(2))
        elif hour == 0:
            period.append(str("00").zfill(2) + "-" + str(hour + 1).zfill(2))
        else:
            period.append(str(hour).zfill(2) + "-" + str(hour + 1).zfill(2))
    df["period"] = period
    return df

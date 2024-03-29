import streamlit as st
import pandas as pd
from collections import Counter
import emoji
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date
import seaborn as sns

def raw_to_df(file, key):
    split_formats = {
        '12hr': '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][mM]\s-\s',
        '24hr': '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s',
        'custom': ''
    }
    datetime_formats = {
        '12hr': '%d/%m/%Y, %I:%M %p - ',
        '24hr': '%d/%m/%Y, %H:%M - ',
        'custom': ''
    }

    with open(file, 'r', encoding='utf-8') as raw_data:
        raw_string = ' '.join(raw_data.read().split('\n'))
        user_msg = re.split(split_formats[key], raw_string)[1:]
        date_time = re.findall(split_formats[key], raw_string)

        df = pd.DataFrame({'date_time': date_time, 'user_msg': user_msg})

    df['date_time'] = pd.to_datetime(df['date_time'], format=datetime_formats[key])
    df['date'] = df['date_time'].dt.date
    df['hour'] = df['date_time'].dt.hour

    usernames = []
    msgs = []
    emojis = []
    for i in df['user_msg']:
        a = re.split('([\w\W]+?):\s', i)
        if a[1:]:
            usernames.append(a[1])
            msgs.append(a[2])
            emojis.append(''.join(e for e in a[2] if e in emoji.EMOJI_DATA))
        else:
            usernames.append("group_notification")
            msgs.append(a[0])
            emojis.append(''.join(e for e in a[0] if e in emoji.EMOJI_DATA))

    df['user'] = usernames
    df['message'] = msgs
    df['emoji'] = emojis
    df.drop('user_msg', axis=1, inplace=True)
    df['message_count'] = 1

    return df

data = raw_to_df("sample.txt", '12hr')

# Ensures 'date' is a datetimelike object with the correct format
data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')

# Converts date to a formatted string
data['date_str'] = data['date'].dt.strftime('%d/%m/%Y')

# Title
st.title("WhatsApp Chat Analysis")

st.sidebar.title("Select for Visualization")

selected_option = st.sidebar.radio("Select Visualization", ["Messages per Day", "Top Emojis", "Most Active Hours", "Messages per User"])


if selected_option == "Messages per Day":
    fig, ax = plt.subplots()
    messages_per_day = data.groupby('date').sum().reset_index()
    sns.lineplot(x='date', y='message_count', data=messages_per_day, ax=ax, linestyle='-', color='b')
    plt.xlabel("Date")
    plt.ylabel("Number of Messages")
    plt.title("Messages per Day")

    # Sets the x-axis limits
    start_date = pd.to_datetime("2023-04-01")  
    plt.xlim(start_date, messages_per_day['date'].max())

    #  x-axis locator and formatter
    date_interval = 15  
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=date_interval))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    
    plt.xticks(rotation=90, ha='right')
    st.pyplot(fig)

elif selected_option == "Top Emojis":
    st.write("Top Emojis")

    all_emojis = ''.join(data['emoji'])

    emoji_counts = Counter([char for char in all_emojis if char in emoji.EMOJI_DATA])

    top_emojis = emoji_counts.most_common(10)

    emoji_table = pd.DataFrame(top_emojis, columns=['Emoji', 'Count'])

    st.table(emoji_table)

elif selected_option == "Most Active Hours":
    fig, ax = plt.subplots()
    sns.barplot(x='hour', y='message_count', data=data.groupby('hour').sum().reset_index(), ax=ax, color='skyblue')
    plt.xlabel("Hour of the Day")
    plt.ylabel("Number of Messages")
    plt.title("Most Active Hours")
    st.pyplot(fig)

elif selected_option == "Messages per User":
    fig, ax = plt.subplots()
    sns.barplot(x='user', y='message_count', data=data.groupby('user').sum().reset_index(), ax=ax)
    plt.xlabel("User")
    plt.ylabel("Number of Messages")
    plt.title("Messages per User")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

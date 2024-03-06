import streamlit as st
import pandas as pd
from collections import Counter
import emoji
import re

# Load the data from a text file
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
    df['date'] = df['date_time'].dt.date  # Add this line to create the 'date' column

    usernames = []
    msgs = []
    for i in df['user_msg']:
        a = re.split('([\w\W]+?):\s', i)
        if a[1:]:
            usernames.append(a[1])
            msgs.append(a[2])
        else:
            usernames.append("group_notification")
            msgs.append(a[0])

    df['user'] = usernames
    df['message'] = msgs
    df.drop('user_msg', axis=1, inplace=True)

    # Create the 'message_count' column
    df['message_count'] = 1  # Initialize with 1 for each message

    return df

# Replace 'your_whatsapp_data.txt' with the actual file path
data = raw_to_df("sample.txt", '12hr')

# Title
st.title("WhatsApp Chat Analysis")

# Sidebar for insights and radio buttons
st.sidebar.title("Select for Visualization")

selected_option = st.sidebar.radio("Select Visualization", ["Messages per Day", "Top Emojis", "Most Active Hours"])

# Display graphs based on selected option
if selected_option == "Messages per Day":
    st.line_chart(data.groupby('date').sum()['message_count'])

elif selected_option == "Top Emojis":
    st.write("Top Emojis:")
    st.write(Counter(''.join(data['emoji'])))

elif selected_option == "Most Active Hours":
    st.bar_chart(data.groupby('hour').sum()['message_count'])

from collections import Counter
import pandas as pd
from urlextract import URLExtract
from wordcloud import WordCloud,STOPWORDS
import emoji
import plotly.express as px
import streamlit as st

extract = URLExtract()
MEDIA_KEYWORDS = {
    "image", "omitted",
    "gif",
    "sticker",
    "media",
}
CUSTOM_STOPWORDS = STOPWORDS.union(MEDIA_KEYWORDS)

def fetch_stats(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

        # fetch the number of messages
    num_messages = df.shape[0]



    # fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    #fetch media messages from a file with no media
    media_keywords = ['image omitted', 'GIF omitted', 'sticker omitted']
    num_media = df[df['message'].str.contains('|'.join(media_keywords), na=False)].shape[0]

    #fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))
    return num_messages, len(words), num_media, len(links)


def most_active_user(df):
    x= df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x, df


def create_word_cloud(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    text = (
        df['message']
        .str.lower()
        .replace(
            to_replace=r'\b(?:image omitted|gif omitted|sticker omitted|media omitted)\b',
            value='',
            regex=True
        )
        .str.replace(r'[^\w\s]', ' ', regex=True)
        .str.cat(sep=' ')
    )
    wc = WordCloud(
        width=800,
        height=400,
        background_color='white',
        stopwords=CUSTOM_STOPWORDS,
    ).generate(text)

    return wc

def emoji_helper(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df

def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time
    return timeline

def daily_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()


def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap



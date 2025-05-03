import re
import pandas as pd
from datetime import datetime


def preprocess(data):
    pattern = r'\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}(?:\s(?:AM|PM))?\]'  # Updated to include AM/PM for 12-hour format
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    dates = [date.strip('[]') for date in dates]  # Remove square brackets from dates

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Determine the time format and convert accordingly
    def parse_datetime(date_str):
        try:
            # Try parsing 24-hour format
            return datetime.strptime(date_str, '%d/%m/%y, %H:%M:%S')
        except ValueError:
            # If 24-hour format fails, try 12-hour format (AM/PM)
            return datetime.strptime(date_str, '%d/%m/%y, %I:%M:%S %p')

    # Convert message_date type
    df['message_date'] = df['message_date'].apply(parse_datetime)

    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Process messages and users
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Extract additional datetime fields
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Define periods based on hour for activity maps
    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df

import re
import pandas as pd
from dateutil import parser
def align_datetime_format(datetime_str):
    datetime_formats = [
        '%d/%m/%y, %I:%M%p - ',
        '%d/%m/%Y, %I:%M %p - ',
        '%Y-%m-%d %H:%M:%S',
        '%m/%d/%y, %I:%M%p - ',
        '%m/%d/%Y, %I:%M %p - ',
        '%d-%m-%Y %H:%M:%S',

    ]

    for fmt in datetime_formats:
        try:
            # Parse the datetime string using the current format
            parsed_datetime = pd.to_datetime(datetime_str, format=fmt)
            print("Parsed datetime:", parsed_datetime)  # Debugging print statement
            # Reformat the parsed datetime to the desired format
            formatted_datetime = parsed_datetime.strftime('%d/%m/%y, %I:%M %p - ')
            print("Formatted datetime:", formatted_datetime)  # Debugging print statement
            return formatted_datetime
        except ValueError:
            # Try the next format if parsing fails
            continue
    return None

def preprocess(data):
    pattern =r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[AP]M\s-\s'
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    dates = [date.replace("\u202f", "") for date in dates]
    dates = [align_datetime_format(date_str) for date_str in dates]

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p - ',)

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(" ".join(entry[2]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    if pd.api.types.is_datetime64_any_dtype(df['date']):
        df['only_date'] = df['date'].dt.date
        df['year'] = df['date'].dt.year
        df['month_num'] = df['date'].dt.month
        df['month'] = df['date'].dt.month_name()
        df['day'] = df['date'].dt.day
        df['day_name'] = df['date'].dt.day_name()
        df['hour'] = df['date'].dt.hour
        df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 11:
            period.append(str(hour) + "-" + str('12 PM'))
        elif hour == 12:
            period.append(str(hour) + "-" + str('01 AM'))
        else:
            period.append(str(hour) + "-" + str(hour + 1)+" " + ('AM' if hour < 11 else 'PM'))

    df['period'] = period

    return df
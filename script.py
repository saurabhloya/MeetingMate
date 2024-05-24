import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import base64
from email.mime.text import MIMEText
from googleapiclient.errors import HttpError

# Define scopes for Google Calendar and Gmail APIs
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/gmail.send']

def authenticate():
    creds = None
    # Check if token.pickle file exists with stored credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# def get_upcoming_meetings(service):
#     # Define time range for upcoming meetings (e.g., next 7 days)
#     now = datetime.utcnow()
#     end_time = now + timedelta(days=7)
#     now_str = now.isoformat() + 'Z'  # 'Z' indicates UTC time
#     end_time_str = end_time.isoformat() + 'Z'

#     # Call the Google Calendar API
#     events_result = service.events().list(calendarId='primary', timeMin=now_str, timeMax=end_time_str,
#                                           singleEvents=True, orderBy='startTime').execute()
#     events = events_result.get('items', [])

#     # Filter one-on-one meetings
#     one_on_one_meetings = [event for event in events if 'attendees' in event and len(event['attendees']) == 2]

#     return one_on_one_meetings

def get_upcoming_meetings(service):
    # Define time range for upcoming meetings (e.g., next 7 days)
    now = datetime.utcnow()
    now_str = now.isoformat() + 'Z'  # 'Z' indicates UTC time

    # Call the Google Calendar API
    events_result = service.events().list(calendarId='primary', timeMin=now_str,
                                          singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        print("No Upcoming events found!")

    # Filter one-on-one meetings
    one_on_one_meetings = [event for event in events if 'attendees' in event and len(event['attendees']) == 2]

    return one_on_one_meetings

def send_reminder_email(service, meeting):
    subject = 'Reminder: Upcoming One-on-One Meeting'
    for i in range(len(meeting['attendees'])):
        body = f"Hi {meeting['attendees'][i]['email']},\n\nThis is a friendly reminder of your upcoming one-on-one meeting scheduled for {meeting['start']['dateTime']}.\n\nPlease make sure to attend on time and be prepared.\n\nBest regards,\nThe H7 Accelerator Team"

        message = MIMEText(body)
        message['to'] = meeting['attendees'][i]['email']
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        try:
            service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            print(f"Reminder email sent to {meeting['attendees'][i]['email']}")
        except HttpError as error:
            print(f"An error occurred: {error}")

def main():
    creds = authenticate()
    service_calendar = build('calendar', 'v3', credentials=creds)
    service_gmail = build('gmail', 'v1', credentials=creds)

    meetings = get_upcoming_meetings(service_calendar)

    for meeting in meetings:
        # print(meeting)
        # print(meeting['attendees'])
        # print(meeting['start'])
        # for i in range (len(meeting['attendees'])):
            # print(meeting['attendees'][i]['email'])
        # print("    ")

        send_reminder_email(service_gmail, meeting)

if __name__ == '__main__':
    main()

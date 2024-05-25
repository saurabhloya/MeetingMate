import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import base64
from email.mime.text import MIMEText
from googleapiclient.errors import HttpError
import pickle
import os
import pandas as pd
import time

# Define scopes for Google Calendar and Gmail APIs
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/gmail.send']

# Function to authenticate MeetingMate
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
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# Function to get upcoming meetings from Google Calendar
def get_upcoming_meetings(service,days_ahead):
    now = datetime.utcnow()
    end_time = now + timedelta(days=days_ahead)          #upcoming 7 days meetings
    now_str = now.isoformat() + 'Z'  # 'Z' indicates UTC time
    end_time_str = end_time.isoformat() + 'Z'

    events_result = service.events().list(calendarId='primary', timeMin=now_str, timeMax=end_time_str,
                                          singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    one_on_one_meetings = [event for event in events if 'attendees' in event and len(event['attendees']) == 2]

    return one_on_one_meetings

# Function to send reminder email
def send_reminder_email(service, meeting, note):
    subject = 'Reminder: Upcoming One-on-One Meeting'
    attendees = meeting['Participants'].split(",")
    for attendee in attendees:
        attendee=attendee.strip()
        body = f"Hi {attendee},\n\nThis is a friendly reminder of your upcoming one-on-one meeting scheduled.\n\n 📅 {meeting['Date']} \n ⏰ {meeting['Start Time']} to {meeting['End Time']}\n\n{note}\n\nBest regards,\nThe H7 Accelerator Team"
        message = MIMEText(body)
        message['to'] = attendee
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        try:
            service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            st.success(f"Reminder email sent to {attendee}")
        except HttpError as error:
            st.error(f"An error occurred while sending email to {attendee}: {error}")

def main():
    st.set_page_config(page_title="MeetingMate", page_icon="📅", layout="wide")

    # Load and apply custom CSS
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    with st.sidebar:
            
        # Container to center align content
        st.image("D:\Study\Projects\Automation\logo.webp")
        st.write(f'<p class="big-font">Manage your one-on-one meetings efficiently.</p>',unsafe_allow_html=True)

        # Authenticate MeetingMate
        creds = authenticate()
        if creds:
            service_calendar = build('calendar', 'v3', credentials=creds)
            service_gmail = build('gmail', 'v1', credentials=creds)
            st.sidebar.success("Authentication successful!")
        else:
            st.sidebar.error("Authentication failed. Please check your credentials.")

        #line seperator
        st.markdown('<hr class="separator">', unsafe_allow_html=True)

        # st.write(f'<p class="big-font">Select days ahead to look for meetings:</p>',unsafe_allow_html=True)
        st.write('<p class="big-font blinking-text">Select days ahead to look for meetings:</p>', unsafe_allow_html=True)
       
        # Options for users to select days ahead
        days_ahead = st.selectbox(f' ',[1, 7, 15, 30],index=2)

    # Get upcoming meetings
    meetings = get_upcoming_meetings(service_calendar,days_ahead)

    # Main content layout
    st.markdown('<p class="header-font">Upcoming One-on-One Meetings</p>', unsafe_allow_html=True)
    
    if meetings:
        # Display table of meetings
        meeting_data = []
        selected_meetings = {}  # Dictionary to store checkbox states
        for meeting_index, meeting in enumerate(meetings):
            start_time = datetime.fromisoformat(meeting['start']['dateTime'])
            end_time = datetime.fromisoformat(meeting['end']['dateTime'])
            formatted_date = start_time.strftime('%Y-%m-%d')
            formatted_start_time = start_time.strftime('%I:%M %p')
            formatted_end_time = end_time.strftime('%I:%M %p')
            participants = ', '.join(participant['email'] for participant in meeting['attendees'] if not participant.get('organizer', False)) 
            meeting_data.append({
                "Date": formatted_date,
                "Start Time": formatted_start_time,
                "End Time": formatted_end_time,
                "Participants": participants,
                "Select": False
            })
        meeting_df = pd.DataFrame(meeting_data)
        meeting_df.reset_index(drop=True, inplace=True)
        meeting_df.index += 1
        meeting_df.rename_axis('Sr. No', inplace=True)
        edited_df = st.data_editor(meeting_df, use_container_width=True)        

        st.markdown(f'<p class="big-font">Please feel free to customize the message below to encourage engagement for the reminder email:</p>', unsafe_allow_html=True)

        default_message = "Your participation and insights are highly valued, and I'm looking forward to our discussion. Let's make this meeting both productive and enjoyable!"
        placeholder = "Enter a brief note encouraging engagement for the reminder email"
        note = st.text_area("Encouraging Message", height=10, value=default_message, placeholder=placeholder,label_visibility="collapsed")

        # Button to send reminder email
        if st.button("Send Reminder","Send Reminder"):
            selected_meetings_info = edited_df[edited_df["Select"]].to_dict("records")
            if not selected_meetings_info:
                st.error("Please select at least one meeting.")
            else:
                for meeting_info in selected_meetings_info:
                    send_reminder_email(service_gmail, meeting_info, note)
    else:
        # Display the message if no upcoming meeting
        st.markdown("## 🌟 No Upcoming Meetings Scheduled 🌟")
        st.markdown(f'<p class="no-meeting">Your calendar is as clear as the sky on a perfect summer\'s day!<br> Enjoy the freedom to focus on what truly matters to you! </p>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()

# MeetingMate

This is a powerful automation tool designed to seamlessly integrate with the Google Calendar API and Gmail API. Its primary objective is to enhance productivity by sending timely reminders to all attendees of upcoming events scheduled on the user's Google Calendar.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have a Google account.
- You have Python 3.9 or higher installed.
- You have `pip` installed.

## Setup Instructions

Follow these steps to set up and run the project.

### 1. Clone the Repository

Clone this repository to your local machine using the following command: git clone https://github.com/saurabhloya/MeetingMate.git

### 2. Enable Google Calendar API

Follow the [Google Calendar API Quickstart](https://developers.google.com/calendar/api/quickstart/python) to enable the Google Calendar API. 

### 3. Enable Gmail API

Follow the [Gmail API Quickstart](https://developers.google.com/gmail/api/quickstart/python) to enable the Gmail API.

### 4. Configure OAuth Consent Screen and Download Credentials
If not already done in step 1 and step 2, configure the OAuth consent screen in the Google Cloud Console and download the OAuth client credentials. Follow these steps:

1. Go to the Google Cloud Console.
2. Click on the project dropdown and select or create the project.
3. In the left sidebar, navigate to APIs & Services > Credentials.
4. Click on Create Credentials and select OAuth client ID.
5. Configure the OAuth consent screen by providing the necessary details.
6. Create an OAuth client ID and download the JSON file.
7. Rename the downloaded JSON file to credentials.json and move it to your working directory (the root of the cloned repository).

### 5. Install Dependencies
Navigate to the project directory and install the required dependencies by running: pip install -r requirements.txt

### 6. Run the Application
To start the application, run the following command: streamlit run main.py

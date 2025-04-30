from django.shortcuts import requests

api_key = "AIzaSyC8OCqt1JXd1zTIbTeVPHBFf0q1tLvBArg"
url = f"https://www.googleapis.com/calendar/v3/calendars/th.th%23holiday%40group.v.calendar.google.com/events?key={api_key}"

response = requests.get(url)
data = response.json()

# พิมพ์ผลลัพธ์
for event in data.get('items', []):
    print(f"Event: {event['summary']}, Date: {event['start']['date']}")
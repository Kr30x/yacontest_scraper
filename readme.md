# Yandex contest parser

This app copies Yandex contest tables to Google Sheets. 
This app was used in my university to generate table with grades for nearly 400 students.

## Usage 

In file {group_name}key.txt provide user keys:
Username
Password

Add Surnames you want to track in file {group_name}.txt:
Surname 1 Name 1 Other name 1 (optional)
Surname 2 Name 2 Other name 2 (optional)

Add contests you want to track in file {group_name}contests.txt:
Link 1
Link 2

Add groups you want to track in main.py file in arrays groups to analyze

Provide keys from Google Sheets in credits.json
You need this structure:

{
  "type": ,
  "project_id":,
  "private_key_id": ,
  "private_key": ,
  "client_id": ,
  "auth_uri": ,
  "token_uri": ,
  "auth_provider_x509_cert_url": ,
  "client_x509_cert_url": ,
  "universe_domain": 
}

Make a table in Google Sheets named {group_name}_generate
Add needed number of sheets each for one contest.

Run main.py to generate all tables
Run server.py to start a script that updates table once per hour. 


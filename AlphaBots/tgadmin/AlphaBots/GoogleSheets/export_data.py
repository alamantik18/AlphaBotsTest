import os

import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


def get_service_sacc():
    creds_json = os.path.dirname(__file__) + "/sacc.json"
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)


sheet = get_service_sacc().spreadsheets()

# https://docs.google.com/spreadsheets/d/10nIqg7-ctljQMflMs-WsHSKGfNPp81XFn_mCPFEVauk/edit#gid=0
sheet_id = '10nIqg7-ctljQMflMs-WsHSKGfNPp81XFn_mCPFEVauk'


def set_data(data):
    values = [data]
    resp = sheet.values().append(
        spreadsheetId=sheet_id,
        range='Лист1!A2',
        valueInputOption='RAW',
        body={'values': values}
    ).execute()

from apiclient.discovery import build
import datetime
from httplib2 import Http
from oauth2client import file, client, tools
import card_read
import os
import pandas as pd
import time

tmp_database_path = os.getcwd() + "/temp_database.csv"


SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
store = file.Storage('token.json')
credentials = store.get()


if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    credentials = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=credentials.authorize(Http()))


spreadsheet_id = '***********************'
range_ = 'Sheet1!A:F'

employee_card = {"*****": "***",
                 "****": "****"}

gym_card = {"CARD1": "*****",
            "CARD2": "*****"}


def add_entry(time, employee_name, card_name, RowNumber):

    if not os.path.isfile(tmp_database_path):
        df = pd.DataFrame(columns=["Time", "EmployeeName", "CardName", "RowNumber"])
        df.to_csv(tmp_database_path, index=False)

    df = pd.read_csv(tmp_database_path)
    labels = ["Time", "EmployeeName", "CardName", "RowNumber"]
    df1 = pd.DataFrame.from_records([(time, employee_name, card_name, RowNumber)], columns=labels)
    df = df.append(df1, ignore_index=False)
    df.to_csv(tmp_database_path, index=False)


def read_entry(employee_name, card_name):

    if not os.path.isfile(tmp_database_path):
        return False, None
    else:
        df = pd.read_csv(tmp_database_path)
        RowNumber = df.loc[(df["EmployeeName"] == employee_name) & (df["CardName"] == card_name), "RowNumber"]
        # print RowNumber
        if len(RowNumber) > 0:
            print RowNumber.iloc[0]
            df = df[df["RowNumber"] != RowNumber.iloc[0]]
            df.to_csv(tmp_database_path, index=False)
            return True, RowNumber.iloc[0]
        else:
            return False, None


def ID2cardname(ID):

    for key, value in gym_card.iteritems():
        if value == ID:
            return key

    return None


def ID2empname(ID):

    for key, value in employee_card.iteritems():
        if value == ID:
            return key

    return None


def update(list1):
    value_input_option = 'RAW'
    insert_data_option = 'INSERT_ROWS'
    value_range_body = {
        "majorDimension": "COLUMNS",
        "values": list1
    }

    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_,
                                                     valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body).execute()

    return


def updateOUTtime(RowNumber, Time):

    updateRange = "Sheet1!D" + str(RowNumber) + ":D" + str(RowNumber)
    value_input_option = 'RAW'
    value_range_body = {
        "majorDimension": "COLUMNS",
        "values": [[str(Time)]]
    }
    request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=updateRange,
                                                     valueInputOption=value_input_option, body=value_range_body)
    response = request.execute()
    return


Employee_card = True
Gym_card = False
employee_name = None
card_name = None
number_of_entries = 0
IsReturn = False


if __name__ == '__main__':

    while True:

        if Employee_card:

            while True:
                print "Punch the Employee card"
                ID = card_read.read()
                if len(ID) == 0:
                    not_punched = True
                    break
                not_punched = False
                employee_name = ID2empname(ID)
                if employee_name is None:
                    print "Use proper card"
                    time.sleep(1)
                    continue
                print "Card punched successfully"
                Employee_card = False
                Gym_card = True
                break

        if not_punched:
            continue

        time.sleep(2)

        if Gym_card:

            while True:

                print "Punch the gym Card"
                ID = card_read.read()
                if len(ID) == 0:
                    not_punched = True
                    break
                not_punched = False
                card_name = ID2cardname(ID)
                if card_name is None:
                    print "Use proper card"
                    time.sleep(1)
                    continue
                print "Card punched successfully"
                Time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                Gym_card = False
                Employee_card = True
                break

        if not_punched:
            Employee_card = True
            continue

        IsReturn, RowNumber = read_entry(employee_name, card_name)

        if not IsReturn:

            list1 = [[employee_name], [card_name], [str(Time)]]
            print "Now updating record on spreadsheet"
            update(list1)
            print "Entry made successfully. Have a great Workout!!!"
            number_of_entries += 1
            add_entry(Time, employee_name, card_name, number_of_entries)

        else:
            # print RowNumber
            updateOUTtime(RowNumber, Time)
            print "Thanks for using the GYM!!"

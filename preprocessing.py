# Takes job search data from my original Google Sheets spreadsheet

import gspread 
import pandas as pd
import datetime

# Get data from google sheets
gc = gspread.oauth()
wks = gc.open("Recruiting Hell").worksheet("Applications")

# Exclude company name/location columns for privacy and job titles as they are already grouped in the Category column
df = pd.DataFrame(wks.get_all_records())[['Date','Category','Source','Applied','CL/msg?','Exam','Interview','Status']]
df.to_csv('jobdata.csv', index=False)

# Create dataframe from the jobdata.csv file and clean up data for use in other python scripts
def createDf():
    df = pd.read_csv('jobdata.csv')

    # Drop empty rows
    df.drop(df[df['Applied'] == False].index, inplace=True)

    # Convert dates to python date objects
    df['Date'] = [datetime.datetime.strptime(str(x),'%m/%d/%Y').date() for x in df['Date']]

    return df

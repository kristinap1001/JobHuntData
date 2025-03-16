# Takes job search data from my original Google Sheets spreadsheet

import gspread 
import pandas as pd
import datetime

# Get data from google sheets
gc = gspread.oauth()
wks = gc.open("Recruiting Hell").worksheet("Applications")

# Exclude company names for privacy and job titles as they are already grouped in the Category column
df = pd.DataFrame(wks.get_all_records())[['Date','Location','Category','Type','Source','Applied','CL/msg?','Exam','Interview','Status']]
df.to_csv('jobdata.csv', index=False)

# Create dataframe from the jobdata.csv file and clean up data for use in other python scripts
def createDf():
    df = pd.read_csv('jobdata.csv')

    # Drop empty rows
    df.drop(df[df['Applied'] == False].index, inplace=True)

    # Replace "On-site _____" and "Hybrid _____" with just "On-site" and "Hybrid" for privacy
    df['Location'] = df['Location'].str.extract(r'^(Hybrid|On-site|Remote)')

    # Convert dates to python date objects
    df['Date'] = [datetime.datetime.strptime(str(x),'%m/%d/%Y').date() for x in df['Date']]

    return df

# Encode a column to replace items with 0,1,2,... 
def encodeCol(df,col,order=[]):
    if len(order) == 0:
        # if order is unspecified, automatically use indices in order of appearance in the column
        order = df[col].unique().tolist()
    colDict = {item:index for index,item in enumerate(order)}
    df.replace({col: colDict}, inplace=True)
    print(col + ": " + str(colDict))
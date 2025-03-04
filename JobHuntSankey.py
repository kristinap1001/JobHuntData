import plotly.graph_objects as go
import pandas as pd
import gspread
import plotly.io as pio
import datetime
import numpy as np

# Image export settings
pio.kaleido.scope.default_width = 1920
pio.kaleido.scope.default_height = 1080

# Get data from google sheets
gc = gspread.oauth()
wks = gc.open("Recruiting Hell").worksheet("Applications")
jobDf = pd.DataFrame(wks.get_all_records())[['Date','Source','Applied','CL/msg?','Exam','Interview','Status']]

# Checkboxes use strings 'TRUE' and 'FALSE' instead of booleans True and False
jobDf['Applied'] = jobDf['Applied'].map({'TRUE':True, 'FALSE':False})
jobDf['CL/msg?'] = jobDf['CL/msg?'].map({'TRUE':True, 'FALSE':False})
jobDf['Exam'] = jobDf['Exam'].map({'TRUE':True, 'FALSE':False})
jobDf['Interview'] = jobDf['Interview'].map({'TRUE':True, 'FALSE':False})

# Drop empty rows
jobDf.drop(jobDf[jobDf['Applied'] == False].index, inplace=True)

# Convert dates to python date objects
jobDf['Date'] = [datetime.datetime.strptime(x,'%m/%d/%Y').date() for x in jobDf['Date']]

# Label names of job sources
jobSources = jobDf['Source'].unique().tolist()

# Number of jobs applied to from each job source, in same order as jobSources
applied = [(jobDf['Source'] == x).sum() for x in jobSources]

# Number of OAs, interviews, rejections, no response, accepted for each job source
oaCounts = jobDf[jobDf['Exam'] == True]['Source'].value_counts()
oas = [oaCounts.get(x,0) for x in jobSources] # ensure correct order

interCounts = jobDf[(jobDf['Exam'] == False) & (jobDf['Interview'] == True)]['Source'].value_counts() # Interviews without prior OA
inters = [interCounts.get(x,0) for x in jobSources]

rejCounts = jobDf[(jobDf['Exam'] == False) & (jobDf['Interview'] == False) & (jobDf['Status'] == 'Rejected')]['Source'].value_counts()
rejs = [rejCounts.get(x,0) for x in jobSources]

# Ghosted = no response for over 2 months
ghostCounts = jobDf[(jobDf['Exam'] == False) & (jobDf['Interview'] == False) & (jobDf['Status'] == 'Waiting') 
  & (jobDf['Date'] <= datetime.date.today() - datetime.timedelta(days=60))]['Source'].value_counts()
ghosts = [ghostCounts.get(x,0) for x in jobSources]

# Waiting = no response within 2 months
waitCounts = jobDf[(jobDf['Exam'] == False) & (jobDf['Interview'] == False) & (jobDf['Status'] == 'Waiting') 
  & (jobDf['Date'] > datetime.date.today() - datetime.timedelta(days=60))]['Source'].value_counts()
waits = [waitCounts.get(x,0) for x in jobSources]

# Results after OAs
oaToInt = jobDf[(jobDf['Exam'] == True) & (jobDf['Interview'] == True)]['Applied'].sum()
oaToRej = jobDf[(jobDf['Exam'] == True) & (jobDf['Interview'] == False) & (jobDf['Status'] == 'Rejected')]['Applied'].sum()
oaToGhost = jobDf[(jobDf['Exam'] == True) & (jobDf['Interview'] == False) & (jobDf['Status'] == 'Waiting')
                 & (jobDf['Date'] <= datetime.date.today() - datetime.timedelta(days=60))]['Applied'].sum()
oaToWait = jobDf[(jobDf['Exam'] == True) & (jobDf['Interview'] == False) & (jobDf['Status'] == 'Waiting')
                 & (jobDf['Date'] > datetime.date.today() - datetime.timedelta(days=60))]['Applied'].sum()

# Results after interviews
intToRej = jobDf[(jobDf['Interview'] == True) & (jobDf['Status'] == 'Rejected')]['Applied'].sum()
intToGhost = jobDf[(jobDf['Interview'] == True) & (jobDf['Status'] == 'Waiting')
                  & (jobDf['Date'] <= datetime.date.today() - datetime.timedelta(days=60))]['Applied'].sum()
intToWait = jobDf[(jobDf['Interview'] == True) & (jobDf['Status'] == 'Waiting')
                  & (jobDf['Date'] > datetime.date.today() - datetime.timedelta(days=60))]['Applied'].sum()
intToAcc = jobDf[(jobDf['Interview'] == True) & (jobDf['Status'] == 'Accepted')]['Applied'].sum()

# Construct Source, Target, and Value lists as an nx3 array to match plotly format

# first path = Applied ----> Job Sources
firstPath = [['Applied',jobSource,numApplied] for jobSource, numApplied in zip(jobSources,applied)]

# second path = Job Sources ----> OA/Int/Reject/Waiting/Ghost
secondPath = np.vstack(([[jobSource,'OA',oa] for jobSource, oa in zip(jobSources,oas)],
                        [[jobSource,'Interview',inter] for jobSource, inter in zip(jobSources,inters)],
                        [[jobSource,'Rejected',rej] for jobSource, rej in zip(jobSources,rejs)],
                        [[jobSource,'Waiting',wait] for jobSource, wait in zip(jobSources,waits)],
                        [[jobSource,'No Response',ghost] for jobSource, ghost in zip(jobSources,ghosts)]))

# third path = OA ----> Int/Reject/Waiting/Ghost
thirdPath = np.vstack((['OA','Interview',oaToInt], ['OA','Rejected',oaToRej], ['OA','Waiting',oaToWait], ['OA','No Response',oaToGhost]))

# fourth path = Int ----> Reject/Waiting/Ghost/Accept
fourthPath = np.vstack((['Interview','Rejected',intToRej], ['Interview','Waiting',intToWait], ['Interview','No Response',intToGhost],
                        ['Interview','Accepted',intToAcc]))

# Labels for final source/target/value lists
labels = ['Applied'] + jobSources + ['OA','Interview','Rejected','Waiting','No Response','Accepted']
labelDict = {item:index for index,item in enumerate(labels)} # Mapping labels to the indicies to be used by Plotly

sankeyTable = np.vstack((firstPath,secondPath,thirdPath,fourthPath))
sources = [labelDict[key] for key in sankeyTable[:,0]]
targets = [labelDict[key] for key in sankeyTable[:,1]]
values = sankeyTable[:,2].tolist()

# todo: add colors (random for job sources, red/gray/green for rejected/waiting/accepted, etc)
'''
colors = ['rgba(140, 140, 140, 1)', 'rgba(0, 119, 181, 1)', 'rgba(0, 58, 155, 1)', 'rgba(18, 161, 192, 1)', 'rgba(81, 74, 234, 1)', 
'rgba(211, 251, 82, 1)', 'rgba(135, 189, 230, 1)', 'rgba(204, 0, 51, 1)', 'rgb(25, 41, 112)', 'rgba(58, 207, 135, 1)', 
'rgba(255, 107, 243, 1)', 'rgba(237, 151, 64, 0.5)', 'rgba(237, 200, 14, 0.5)', 'rgba(6, 92, 63, 0.5)', 'rgba(110, 0, 0, 0.5)', 
'rgba(46, 46, 46, 0.5)', 'rgba(88, 255, 46, 0.5)']
jobDf['Color'] = jobDf.apply(lambda row: colors[int(row['Target'])], axis=1)
'''

fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = labels
    ),
    link = dict(
      source = sources,
      target = targets,
      value = values
  ))])

fig.update_layout(title_text="Job Hunt Sankey Diagram", font_size=10)
fig.write_image("diagram.png")
fig.show()
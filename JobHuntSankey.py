# Generates Plotly Sankey diagram from job data

import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio
import datetime
import numpy as np
from random import randint
from preprocessing import createDf

# Image export settings
pio.kaleido.scope.default_width = 1920
pio.kaleido.scope.default_height = 1080

# Import data from preprocessing
jobDf = createDf()

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

# Add colors
colors = ['rgba(140, 140, 140, 1)']
for i in range(len(jobSources)):
    colors.append('rgba(%d, %d, %d, 0.75)' % (randint(0,255),randint(0,255),randint(0,255)))
colors = colors + ['rgba(255, 123, 0, 0.5)', 'rgba(255, 187, 0, 0.5)', 'rgba(110, 0, 0, 0.5)', 'rgba(121, 121, 121, 0.5)', 
                  'rgba(26, 26, 26, 0.5)','rgba(88, 255, 46, 0.5)']

targetColors = [colors[x] for x in targets] # Link colors correspond to the color of the target node

fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 25,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = labels,
      color = colors
    ),
    link = dict(
      source = sources,
      target = targets,
      value = values,
      color = targetColors
  ))])

fig.update_layout(title_text="Job Hunt Sankey Diagram", font_size=10)
fig.write_html("SankeyDiagram.html")
fig.show()
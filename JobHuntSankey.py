import plotly.graph_objects as go
import pandas as pd
import gspread

# Get source/target/values data from google sheets
gc = gspread.oauth()
wks = gc.open("Recruiting Hell").worksheet("Sankey")
jobDf = pd.DataFrame(wks.get_all_records())[['Source','Target','Value']]

labels = ['Applied','LinkedIn','Indeed','Simplify Jobs','RippleMatch','Handshake','NLC','RH/Cella/Upwork','AAS','Career Fair','Company Website',
'Referral','Interview','OA','Rejected','No Response','Accepted']
colors = ['rgba(140, 140, 140, 1)', 'rgba(0, 119, 181, 1)', 'rgba(0, 58, 155, 1)', 'rgba(18, 161, 192, 1)', 'rgba(81, 74, 234, 1)', 
'rgba(211, 251, 82, 1)', 'rgba(135, 189, 230, 1)', 'rgba(204, 0, 51, 1)', 'rgba(36, 54, 136, 1)', 'rgba(58, 207, 135, 1)', 
'rgba(255, 107, 243, 1)', 'rgba(237, 151, 64, 0.5)', 'rgba(237, 200, 14, 0.5)', 'rgba(6, 92, 63, 0.5)', 'rgba(110, 0, 0, 0.5)', 
'rgba(46, 46, 46, 0.5)', 'rgba(88, 255, 46, 0.5)']
labelDict = {item:index for index,item in enumerate(labels)}

# Replace source/target names with indices
jobDf.replace({'Source':labelDict,'Target':labelDict}, inplace=True)

# Add column for target colors
jobDf['Color'] = jobDf.apply(lambda row: colors[int(row['Target'])], axis=1)

fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = labels,
      color = colors
    ),
    link = dict(
      source = jobDf['Source'].tolist(),
      target = jobDf['Target'].tolist(),
      value = jobDf['Value'].tolist(),
      color = jobDf['Color'].tolist()
  ))])

fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
fig.show()
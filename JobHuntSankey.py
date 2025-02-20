import plotly.graph_objects as go
import pandas as pd

jobDf = pd.read_csv("JobData.csv")[['Source','Target','Value']]

labels = ['Applied','LinkedIn','Indeed','Simplify Jobs','RippleMatch','Handshake','NLC','RH/Cella/Upwork','AAS','Career Fair','Company Website',
'Referral','Interview','OA','Rejected','No Response','Accepted']
labelDict = {item:index for index,item in enumerate(labels)}

# Replace source/target names with indices
jobDf.replace({'Source':labelDict,'Target':labelDict}, inplace=True)

fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = labels,
      color = "blue"
    ),
    link = dict(
      source = jobDf['Source'].tolist(), # indices correspond to labels, eg A1, A2, A1, B1, ...
      target = jobDf['Target'].tolist(),
      value = jobDf['Value'].tolist()
  ))])

fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
fig.show()
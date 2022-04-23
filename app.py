# Libraries
import dash
from dash import dcc
from dash import html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px


# Data 

data = pd.read_csv("FCC.csv",
                    dtype = {'Complaint ID':object})
data["Date Sumbited"] = pd.to_datetime(data["Date Sumbited"], format='%m/%d/%y')
data["Date Received"] = pd.to_datetime(data["Date Received"], format='%m/%d/%y')
data["Days To Deliever"] = data["Date Received"] - data["Date Sumbited"]
data.sort_values("Date Sumbited", inplace=True)
def complaint(x):
    if x is not None:
        return 1
    else: 
        return 0
data['complaint'] = data['Complaint ID'].apply(complaint)
data['year'] = data["Date Sumbited"].dt.year
data['month'] = data["Date Sumbited"].dt.month
data['State'].fillna(value= 'Not Recognized', inplace = True)


styling = {"backgroundColor": "black",
                        #'border': '2px solid black',
                        #'borderRadius': '15px',
                        #'overflow': 'hidden'
                        }
# App Called

app = dash.Dash(__name__, external_stylesheets= [dbc.themes.DARKLY],
                meta_tags = [{'name' : 'viewport',
                              'content' :  'width=device-width, intial-scale=1.0'}]
                )
server = app.server
app.title = "Complaints Analytics"


#### Layout Section -------> Bootstrap

app.layout = dbc.Container([

    dbc.Row([
        dbc.Col(html.H1("☹ Financial Consumer Complaints Dashboard ☹",
                style={'fontSize': 45, 'text-align':'center',},
                className= "text-center text-white bg-success h-100 "),
                #width = 9,
                xs=12, sm=12, md=12, lg=12, xl=9,
                ),
        
        dbc.Col([
            html.Div("Date",
                className= "text-center text-white bg-success",
                style={'fontSize': 20, 'text-align':'center',},),
                dcc.DatePickerRange(
                id="my-date-range",
                min_date_allowed=data["Date Sumbited"].min().date(),
                max_date_allowed=data["Date Received"].max().date(),
                start_date=data["Date Sumbited"].min().date(),
                end_date=data["Date Received"].max().date(),
                className= "text-center text-white bg-success w-100",
                ),
        ], #width= 3,
        xs=12, sm=12, md=12, lg=12, xl=3
        ),

    ],className="g-0",),

    html.Br(),
 

    dbc.Row([
        dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Total No. Of Complaints"),
                            html.H2(id="total", children="", style={'fontWeight':'bold'})
                        ], className='text-white rounded' , style = styling)
                    ])
        ],
        xs=12, sm=12, md=6, lg=6, xl=3,
        #width = {'size':3},
        ),

        dbc.Col([
            dbc.Card([
                        dbc.CardBody([
                            html.H5("Timely Responded Complaints"),
                            html.H2(id="timely", children="", style={'fontWeight':'bold'})
                        ], className='text-white rounded', style = styling)
                    ])
        ],
        #width = {'size':3}
        xs=12, sm=12, md=6, lg=6, xl=3,
        ),

        dbc.Col([
            dbc.Card([
                        dbc.CardBody([
                            html.H5("Customer Disputed"),
                            html.H2(id="dispute", children="", style={'fontWeight':'bold'})
                        ], className='text-white  rounded', style = styling)
                    ])
        ],
        #width = {'size':3}
        xs=12, sm=12, md=6, lg=6, xl=3,
        ),

        dbc.Col([
            dbc.Card([
                        dbc.CardBody([
                            html.H5("Avg. Time To Deliever"),
                            html.H2(id="deliever", children="", style={'fontWeight':'bold'})
                        ], className='text-white rounded', style = styling)
                    ])
        ],
        #width = {'size':3}
        xs=12, sm=12, md=6, lg=6, xl=3,        
        ),
    ] ,className="text-center", justify= 'around', ),

    html.Br(),

    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id= 'bar',
                figure= {}
            )
        ],
        className='rounded',
        #width = {'size':6},
        xs=12, sm=12, md=12, lg=6, xl=6,                
        ),

        html.Br(), 

        dbc.Col([
            dcc.Graph(
                id= 'map',
                figure= {}
            )
        ],
        #width = {'size':6},
        className='rounded',
        xs=12, sm=12, md=12, lg=6, xl=6,                
        ),

    ] ,className="text-center rounded", ),

    html.Br(),

    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id= 'line',
                figure= {}
            )
        ],
        className='rounded',
        #width = {'size':6}
        xs=12, sm=12, md=12, lg=6, xl=6,                        
        ),

        html.Br(),

        dbc.Col([
            dcc.Graph(
                id= 'pie',
                figure= {
                }
            )
        ],
        className='rounded',
        #width = {'size':6}
        xs=12, sm=12, md=12, lg=6, xl=6,                        
        ),

    ] ,className="text-center", ),

],#fluid= True
)


# ----------- Graphs ----------------

    # Cards
def cards(mask):
    filtered_data = data.loc[mask, :]
    total_complaints = filtered_data['Complaint ID'].count()
    timely =  round((filtered_data[filtered_data['Timely response?'] == 'Yes']['Complaint ID'].count() / filtered_data['Timely response?'].count() ) * 100, 2)
    timely_formated = f"{timely:,.2f} %"  
    dispute = round((filtered_data[filtered_data['Consumer disputed?'] == 'Yes']['Complaint ID'].count() / filtered_data['Consumer disputed?'].count() ) * 100, 2)
    dispute_formated = f"{dispute:,.2f} %"  
    deliever = round(filtered_data["Days To Deliever"].dt.days.agg('mean'),2)
    deliever_formatted = f"{deliever:,.2f} Days"
    return total_complaints, timely_formated , dispute_formated, deliever_formatted

    # Bar
def bar_chart(mask):
    filtered_data = data.loc[mask, :]
    bar_data = filtered_data.groupby('Product')['Product'].count().sort_values(ascending = True)
    figbar = px.bar(bar_data, x = bar_data.values, y = bar_data.index, orientation= 'h', color='Product',
    title= 'Products By Complaints', template= 'plotly_dark',
    color_continuous_scale='viridis', labels=dict(x="Total No. Of Complaints", index="Products"))
    figbar.update_coloraxes(showscale=False)
    return figbar   

    #  Map
def MAP(mask):
    filtered_data = data.loc[mask, :]
    map_data = filtered_data.groupby(['State'])['Complaint ID'].count()
    figmap = px.choropleth(map_data, locations=map_data.index, locationmode="USA-states", scope="usa",
                    title= 'Complaints By State', template= 'plotly_dark',
                    color=map_data.values, # lifeExp is a column of gapminder
                    #hover_name= map_data.index, # column to add to hover information
                    hover_data= {'Total No. Of Complaints' : map_data.values},
                    color_continuous_scale=px.colors.sequential.Plasma)
    figmap.update_coloraxes(showscale=False)
    return figmap

    # Line Chart
def LINE(mask):
    filtered_data = data.loc[mask, :]
    line_data = filtered_data.groupby('year')['Complaint ID'].count()
    figln = px.line(line_data, x = line_data.index, y = line_data.values, title= 'No. Of Complaints Yearly Trend',
                        labels=dict(y="Total No. Of Complaints", year="Year"),
                        template= 'plotly_dark', )
    return figln

    # PIE / Donut
def DONUT(mask):
    filtered_data = data.loc[mask, :]
    pie_data = filtered_data.groupby(['Submitted via'])['Complaint ID'].count()
    figpie = px.pie(pie_data, values=pie_data.values, names=pie_data.index, title='Submitted Via?',
                hole=.5, template= 'plotly_dark',)
    return figpie


# -------- MASKS -------------------

    # sd  = start_date
    # ed  = end_date
    # cdb = clk_data_bar
    # cdm = clk_data_map
    # cdp = clk_data_pie

def MASK( sd, ed, cdb = data['Product'],
            cdm = data['State'], cdp = data['Submitted via']):
    mask = (
        (data["Date Sumbited"] >= sd)
        & (data["Date Sumbited"] <= ed) 
        & (data['Product'] == cdb)
        & (data['State'] == cdm)
        & (data['Submitted via'] == cdp)
    ) 
    return mask


# -------- Callbacks ---------------

### KPI - No. Of Complaints
@app.callback(
    Output('total', 'children'),
    Output('timely', 'children'),
    Output('dispute', 'children'),
    Output('deliever', 'children'),
    Input(component_id='bar', component_property='clickData'),
    Input(component_id='map', component_property='clickData'),
    Input(component_id='pie', component_property='clickData'),
    Input("my-date-range", "start_date"),
    Input("my-date-range", "end_date"),
)
def update_graph(clk_data_bar, clk_data_map, clk_data_pie, start_date, end_date):
    if ((clk_data_bar is None) & (clk_data_map is None) & (clk_data_pie is None)):
        mask = MASK( start_date, end_date)
        total_complaints, timely_formated , dispute_formated, deliever_formatted = cards(mask)
        return total_complaints, timely_formated , dispute_formated, deliever_formatted
    elif ((clk_data_bar is None) & (clk_data_map is None)):
        clp = clk_data_pie['points'][0]['label']
        mask = MASK( start_date, end_date, cdp = clp)
        total_complaints, timely_formated , dispute_formated, deliever_formatted = cards(mask)
        return total_complaints, timely_formated , dispute_formated, deliever_formatted     
    elif ((clk_data_map is None) & (clk_data_pie is None)):
        clb = clk_data_bar['points'][0]['y']
        mask = MASK( start_date, end_date, cdb = clb)
        total_complaints, timely_formated , dispute_formated, deliever_formatted = cards(mask)
        return total_complaints, timely_formated , dispute_formated, deliever_formatted     
    elif ((clk_data_pie is None) & (clk_data_bar is None)):
        clm = clk_data_map['points'][0]['location']
        mask = MASK( start_date, end_date, cdm = clm)
        total_complaints, timely_formated , dispute_formated, deliever_formatted = cards(mask)
        return total_complaints, timely_formated , dispute_formated, deliever_formatted   
    elif clk_data_bar is None:
        clm = clk_data_map['points'][0]['location']
        clp = clk_data_pie['points'][0]['label']
        mask = MASK( start_date, end_date, cdm = clm, cdp = clp)
        total_complaints, timely_formated , dispute_formated, deliever_formatted = cards(mask)
        return total_complaints, timely_formated , dispute_formated, deliever_formatted
    elif clk_data_map is None:
        clb = clk_data_bar['points'][0]['y']
        clp = clk_data_pie['points'][0]['label']
        mask = MASK( start_date, end_date, cdb = clb, cdp = clp)
        total_complaints, timely_formated , dispute_formated, deliever_formatted = cards(mask)
        return total_complaints, timely_formated , dispute_formated, deliever_formatted
    elif clk_data_pie is None:
        clm = clk_data_map['points'][0]['location']
        clb = clk_data_bar['points'][0]['y']
        mask = MASK( start_date, end_date, cdb = clb, cdm = clm)
        total_complaints, timely_formated , dispute_formated, deliever_formatted = cards(mask)
        return total_complaints, timely_formated , dispute_formated, deliever_formatted             
    else:
        clb = clk_data_bar['points'][0]['y']
        clm = clk_data_map['points'][0]['location']
        clp = clk_data_pie['points'][0]['label']
        mask = MASK( start_date, end_date, cdb = clb, cdm = clm, cdp = clp) 
        total_complaints, timely_formated , dispute_formated, deliever_formatted = cards(mask)
        return total_complaints, timely_formated , dispute_formated, deliever_formatted


# BarChart
@app.callback(
    Output('bar', 'figure'),
    Input(component_id='map', component_property='clickData'),
    Input(component_id='pie', component_property='clickData'),
    Input("my-date-range", "start_date"),
    Input("my-date-range", "end_date"),
)
def update_graph(clk_data_map, clk_data_pie, start_date, end_date):
    if  ((clk_data_map is None) & (clk_data_pie is None)):
        mask = MASK( start_date, end_date)
        figbar = bar_chart(mask)
        return figbar
    elif clk_data_map is None:
        clp = clk_data_pie['points'][0]['label']
        mask = MASK( start_date, end_date,  cdp = clp)
        figbar = bar_chart(mask)
        return figbar
    elif clk_data_pie is None:
        clm = clk_data_map['points'][0]['location']
        mask = MASK( start_date, end_date, cdm = clm)
        figbar = bar_chart(mask)
        return figbar           
    else:
        clm = clk_data_map['points'][0]['location']
        clp = clk_data_pie['points'][0]['label']
        mask = MASK( start_date, end_date, cdm = clm, cdp = clp) 
        figbar = bar_chart(mask)
        return figbar



# Map
@app.callback(
    Output('map', 'figure'),
    Input(component_id='bar', component_property='clickData'),
    Input(component_id='pie', component_property='clickData'),
    Input("my-date-range", "start_date"),
    Input("my-date-range", "end_date"),
)
def update_graph(clk_data_bar, clk_data_pie, start_date, end_date):
    if ((clk_data_bar is None) & (clk_data_pie is None)):
        mask = MASK( start_date, end_date)
        figmap = MAP(mask)
        return figmap   
    elif clk_data_bar is None:
        clp = clk_data_pie['points'][0]['label']
        mask = MASK( start_date, end_date, cdp = clp)
        figmap = MAP(mask)
        return figmap  
    elif clk_data_pie is None:
        clb = clk_data_bar['points'][0]['y']
        mask = MASK( start_date, end_date, cdb = clb)
        figmap = MAP(mask)
        return figmap             
    else:
        clb = clk_data_bar['points'][0]['y']
        clp = clk_data_pie['points'][0]['label']
        mask = MASK( start_date, end_date, cdb = clb, cdp = clp) 
        figmap = MAP(mask)
        return figmap  
             

# Line chart - Single
@app.callback(
    Output('line', 'figure'),
    Input(component_id='bar', component_property='clickData'),
    Input(component_id='map', component_property='clickData'),
    Input(component_id='pie', component_property='clickData'),
    Input("my-date-range", "start_date"),
    Input("my-date-range", "end_date"),
)
def update_graph(clk_data_bar, clk_data_map, clk_data_pie, start_date, end_date):
    if (clk_data_bar is None) & (clk_data_map is None) & (clk_data_pie is None):
        mask = MASK( start_date, end_date)
        figln = LINE(mask)
        return figln
    elif ((clk_data_bar is None) & (clk_data_map is None)):
        clp = clk_data_pie['points'][0]['label']
        mask = MASK( start_date, end_date, cdp = clp)
        figln = LINE(mask)
        return figln     
    elif ((clk_data_map is None) & (clk_data_pie is None)):
        clb = clk_data_bar['points'][0]['y']
        mask = MASK( start_date, end_date, cdb = clb)
        figln = LINE(mask)
        return figln     
    elif ((clk_data_pie is None) & (clk_data_bar is None)):
        clm = clk_data_map['points'][0]['location']
        mask = MASK( start_date, end_date, cdm = clm)
        figln = LINE(mask)
        return figln  
    elif clk_data_bar is None:
        clm = clk_data_map['points'][0]['location']
        clp = clk_data_pie['points'][0]['label']
        mask = MASK( start_date, end_date, cdm = clm, cdp = clp)
        figln = LINE(mask)
        return figln
    elif clk_data_map is None:
        clb = clk_data_bar['points'][0]['y']
        clp = clk_data_pie['points'][0]['label']
        mask = MASK( start_date, end_date, cdb = clb, cdp = clp)
        figln = LINE(mask)
        return figln
    elif clk_data_pie is None:
        clm = clk_data_map['points'][0]['location']
        clb = clk_data_bar['points'][0]['y']
        mask = MASK( start_date, end_date, cdb = clb, cdm = clm)
        figln = LINE(mask)
        return figln            
    else:
        clb = clk_data_bar['points'][0]['y']
        clm = clk_data_map['points'][0]['location']
        clp = clk_data_pie['points'][0]['label']
        mask = MASK( start_date, end_date, cdb = clb, cdm = clm, cdp = clp) 
        figln = LINE(mask)
        return figln
    

## Pie - donut

@app.callback(
    Output("pie", "figure"), 
    Input(component_id='bar', component_property='clickData'),
    Input(component_id='map', component_property='clickData'),
    Input("my-date-range", "start_date"),
    Input("my-date-range", "end_date"),
)
def update_graph(clk_data_bar, clk_data_map, start_date, end_date):
    if ((clk_data_bar is None) & (clk_data_map is None)):
        mask = MASK( start_date, end_date)
        figpie = DONUT(mask)
        return figpie
    elif clk_data_bar is None:
        clm = clk_data_map['points'][0]['location']
        mask = MASK( start_date, end_date, cdm = clm)
        figpie = DONUT(mask)
        return figpie
    elif clk_data_map is None:
        clb = clk_data_bar['points'][0]['y']
        mask = MASK( start_date, end_date, cdb = clb)
        figpie = DONUT(mask)
        return figpie         
    else:
        clb = clk_data_bar['points'][0]['y']
        clm = clk_data_map['points'][0]['location']
        mask = MASK( start_date, end_date, cdb = clb, cdm = clm) 
        figpie = DONUT(mask)
        return figpie



# -------- Run App -----------------

if __name__ == "__main__":
    app.run_server(debug=True)
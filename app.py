from ast import If
from re import X
import dash
from dash import Dash, html, callback_context
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_daq as daq
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from plotly.graph_objs import *
from raceplotly.plots import barplot

# Dataset Processing
#----------------------------------------------------------------------------------------
path = 'https://raw.githubusercontent.com/TiagoQuaresma/Group14_Final_Project_Dashboard/main/data/'

df = pd.read_csv(path + 'energy_eu.csv')
df_map= pd.read_csv(path +'energy_euT.csv')
df_countries = pd.read_csv(path +'Electricity_prices.csv', index_col=0)
df_sector = pd.read_csv(path +'Electricity_by_sector.csv')
df_shares = pd.read_csv(path +'zero_mission.csv')

# 1st Part - energy_eu dataset | source of energy and source of energy per country
#----------------------------------------------------------------------------------------------------------------
country_name = df.iloc[:,1:28]
country_sector = df_sector.iloc[:,2:28]
country_map = df_map.iloc[:,1:12]


country_options = ['Austria','Belgium','Bulgaria','Croatia','Cyprus','Czechia','Denmark','Estonia',
                   'Finland','France','Germany','Greece','Hungary','Ireland','Italy','Latvia','Lithuania',
                   'Luxembourg','Malta','Netherlands','Poland','Portugal','Romania','Slovakia',
                   'Slovenia','Spain','Sweden']

source_options = ['Coal','Nuclear','Gas','Biofuels','Oil','Hydro','Solar',
                  'Geothermal','Wind','Non-renewable waste','Renewable waste']

    
radio_Re_Non_To = dbc.RadioItems(
        id='Re_Non_To', 
        className='radio',
        options=[dict(label='Renewable', value=0), dict(label='Non-renewable', value=1), dict(label='Total', value=2)],
        value=2, 
        inline=True
    )


fig_ce = px.sunburst(df, path=['Type', 'Sources'], values='Total', color='Sources', 
                        color_discrete_sequence = px.colors.sequential.haline_r).update_traces(hovertemplate = '%{label}<br>' + 'Sources: %{value} Gw/h')
fig_ce = fig_ce.update_layout({'margin' : dict(t=0, l=0, r=0, b=10),
                        'paper_bgcolor': '#e3f7ff',
                        'font_color':'#363535'})

# 2nd Part - energy_eu dataset | europe map
#----------------------------------------------------------------------------------------------------------------

data_choropleth = dict(type='choropleth',
                       locations=df_map['Country'],  
                       locationmode='country names',
                       autocolorscale = False,
                       z=df_map['Coal'],
                       colorbar= {'title':'Gw/h (log)'},
                       colorscale='ylgnbu',
                      )

layout_choropleth = dict(geo=dict(scope='europe',  
                                  projection=dict(type='natural earth'
                                                 ),
                                  showcoastlines=True,
                                  projection_scale=True,
                                  showland=True,   
                                  landcolor='white',
                                  lakecolor='white',
                                  showocean=True,
                                  oceancolor='azure',
                                  
                                 ),
                         
                         title=dict(text='xxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                                    x=.5 # Title relative position according to the xaxis, range (0,1)
                                   )
                        )
fig_choropleth = go.Figure(data=data_choropleth, layout=layout_choropleth)

# 3rd Part - Electricity prices dataset
#--------------------------------------------------------------------------------------------------------------------

# An empty graph object
fig_bar = go.Figure()

# Each year defines a new hidden (implies visible=False) trace in our visualization
for year in df_countries.columns:
    colors=[]
    for country in df_countries[year].sort_values(ascending = False).index:
        if(country=='EU'):
            colors.append("gold")
        else:
            colors.append("#636efa")

    fig_bar.add_trace(dict(type='bar',
                     x=df_countries[year].sort_values(ascending = False).index,
                     y=df_countries[year].sort_values(ascending = False),
                     name=year,
                     showlegend=False,
                     visible=False,
                     marker_color=colors
                    )
               )

# First seen trace
fig_bar.data[0].visible = True


# Lets create our slider, one option for each trace
steps = []
for i in range(len(fig_bar.data)):
    step = dict(
        label='Year ' + str(2010 + i),
        method="restyle", #there are four methods restyle changes the type of an argument (in this case if visible or not)
        args=["visible", [False] * len(fig_bar.data)], # Changes all to Not visible
    )
    step["args"][1][i] = True  # Toggle i'th trace to "visible"
    steps.append(step)

    
sliders = [dict(
    active=2010,
    pad={"t": 100},
    steps=steps
)]


fig_bar.update_layout(dict(yaxis=dict(title='EUR/Kw-h',
                             range=[0,0.25]
                            ),
                  sliders=sliders))

# 4th Part - electricity_by_sector dataset
#----------------------------------------------------------------------------------------------------------------

fig_tree = px.treemap(df_sector, path=[px.Constant("Electricity Consumption"), 'Sector', 'Sub-sector'], 
                values='Austria',
                color='Sector',
                color_discrete_map={'(?)':'lightgrey', 'Industry Sector':'lightblue', 
                                    'Transport Sector':'tomato',
                                   'Commercial and Public Services Sector':'tan',
                                   'Household Sector':'thistle',
                                   'Agriculture and Forestry Sector':'honeydew',
                                   'Fishing Sector':'lightskyblue'}
                )


# 5th Part - zero_emission dataset
#----------------------------------------------------------------------------------------------------------------

fig_race = barplot(df_shares,  item_column='Country', value_column='Share', time_column='Year')
fig_race = fig_race.plot(item_label = 'Top 10 Countries', value_label = 'Share (%)', frame_duration = 1000)



#-------------------------------------------------------------------------------------------------
#The App Itself
#-----------------------------------------------------------------------------------------------

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.layout = html.Div([
#TITLE
    dbc.Row([
        dbc.Col([html.Img(src = app.get_asset_url('logo.png'))],width=2),
        dbc.Col(html.H1('Electricity in the European Union', style={"margin-top": "0","font-weight": "bold","text-align": "center"}),width=8),
        dbc.Col(width=2),
        dbc.Col(width=2),
        dbc.Col(html.Label('We aim to understand the electricity consumption across European Union (EU) as well as its sources and respective prices throughout the years. With this dashboard, you will be able to explore the types of energy each EU country has and uses, their consumption per sector as well as the zero emission vehicles used in the 10 main countries.', 
                       style={"text-align": "center", "margin-top": "-25px","margin-bottom":"10px   "}),width=8)
    ],style={'background-color':'#89B7D3','padding':'10px'}),
#FIRST 2 PARTS (1 e 2)
    html.Div([
        html.Div([
            html.Label("1. Sources of the consumed electricity in 2020 (Gw/h)", style={'font-size': 'medium'}),
            html.Br(),
            html.Br(),
            
            html.Label('Select the type of energy:'),html.Br(),
            dcc.Dropdown(id='type_energy',
                         options=[{'label': x, 'value': x}
                                  for x in df['Type'].unique()],
                         searchable=False,
                         clearable=False,
                         value='Renewable'
                         ),
    
            html.Br(),
    
            dcc.Graph(id='bar_graph',figure = {'layout': {'plot_bgcolor': 'red','paper_bgcolor':'red'}}),
            dbc.Row(
                    dbc.Col(
                        html.Div([
                            html.P('Check out the differences between the renewable and non-renewable sources of the electricity we consume! Biofuels win the race in renewable sources and Nuclear energy dominates non-renewable.',style={'text-align':'justify'})
                        ],className='box_comment'),
                        width={"size": 8, "offset": 2},
                    )
                )
            ], className='box', style={'padding-bottom':'15px', 'width':'50%'}),
            html.Br(),
            
        
        html.Div([
            html.Label("2. Type of energy source per country in 2020", style={'font-size': 'medium'}),
            html.Br(),
            html.Br(),
    
            html.Label('Choose a Country:'),
            dcc.Dropdown(id='energy_country',
                         options=[{'label': x, 'value': x}
                                  for x in country_options],
                         searchable=False,
                         clearable=False,
                         value='Austria'
                         ),

            html.Label('Click on it to know more!', style={'font-size':'9px'}),
            html.Br(), 
            html.Br(), 
            dcc.Graph(id = 'cheese_graph', figure = fig_ce),
            dbc.Row(
                    dbc.Col(
                        html.Div([
                            html.P(' Here we have the energy sources of the electricity that each country uses. With this we can have a better understanding of whether the country is more dependent on renewable or non-renewable energies and what are the respective sources. Select different countries and explore the results!',style={'text-align':'justify'})
                        ],className='box_comment'),
                        width={"size": 8, "offset": 2},
                    )
                )

            ], className='box', style={'padding-bottom':'15px', 'width':'50%'}),
    ],style={'display':'flex'}),
#EUROPE MAP

    dbc.Row([
        dbc.Col([
            html.Div([
                html.Label('3.Source of energy in each European Country in 2020'),
                html.Br(),
                html.Br(),
                html.P("Select a source:"),
                dcc.RadioItems(id='source', 
                    options=[{'label': x, 'value': x}
                        for x in source_options],
                    value='Coal',
                    inline=True,
                    className='box',
                    labelStyle = {'padding':'3px'},
                    style={'margin': '10px', 'padding-top':'15px', 'padding-bottom':'15px', 'display':'inline-block'}
                    ),
                dcc.Graph(id="graphmap", figure = fig_choropleth),
                dbc.Row(
                    dbc.Col(
                        html.Div([
                            html.P('On the map above you can inspect the various sources of electricity used by each country and see the differences between them by source. Choose the different countries from the buttons above and check out the discrepancies!',style={'text-align':'justify'})
                        ],className='box_comment'),
                        width={"size": 8, "offset": 2},
                    )
                )
            ],className='box')
        ], width=8 ),

        dbc.Col([
            html.Img(src=app.get_asset_url('high_voltage_pole.png'), 
                                 style={'position':'relative', 
                                        'margin':'auto',
                                        'display':'block',
                                        'width':'80%',
                                        'opacity':'60%'}),
        ],width=4,style={'display':'flex'})
    ]),


#PRICE OF ELECTRICITY
    html.Div([
        html.Label("4. Electricity Prices for Household Consumers by Country in 2010 and 2021", 
                       style={'font-size': 'medium'}),
            html.Br(),
            
            dcc.Graph(id = 'elect_price', figure = fig_bar),
            dbc.Row(
                    dbc.Col(
                        html.Div([
                            html.P('The prices of electricity changed throughout the years and here you have the opportunity to see these changes and compare prices among countries. Besides that, you can also compare them with the EU average. Try it out!',style={'text-align':'justify'})
                        ],className='box_comment'),
                        width={"size": 8, "offset": 2},
                    )
                )
            ], className='box', style={'padding-bottom':'15px'}),
            
#TREEMAP | ELECTRICITY CONSUMPTION BY SECTOR
    html.Div([
        html.Label("5. Electricity Consumption by Sector in 2020", style={'font-size': 'medium'}),
            html.Br(),
            html.Br(),
    
            html.Label('Choose a Country:'),
            dcc.Dropdown(id='energy_sector',
                         options=[{'label': x, 'value': x}
                                  for x in country_options],
                         searchable=False,
                         clearable=False,
                         value='Austria',
                         style={'width':'50%'}
                         ),


            html.Label('Click on it to know more!', style={'font-size':'9px'}),
            html.Br(), 
            html.Br(), 
            dcc.Graph(id = 'tree_graph', figure = fig_tree),
            
            dbc.Row(
                    dbc.Col(
                        html.Div([
                            html.P('Every country consumes different amounts of electricity in its sectors. By the electricity consumption we can have a better understanding of the economic structure of the members primary, secondary, and tertiary sectors. Were you aware of the differences?',style={'text-align':'justify'})
                        ],className='box_comment'),
                        width={"size": 8, "offset": 2},
                    )
                )
            
            ], className='box', style={'padding-bottom':'15px'}),
#RACEPLOT

    dbc.Row([
        dbc.Col([
            html.Div([
                html.Label("6. Share of Zero Emission Vehicles in Newly Registered Passenger Cars in EU",style={'font-size': 'medium'}),
                html.Br(),
                dcc.Graph(id = 'share_zero', figure = fig_race),

                dbc.Row(
                    dbc.Col(
                        html.Div([
                            html.P('This plot provides us information about the newly registered electric vehicles in EU countries since 2011. From the goals of the Green Deal programm, we can see who is first in the race for the energetic transition of the automotive sector over the years. Click play or use the cursor to see who is first!',style={'text-align':'justify'})
                        ],className='box_comment'),
                        width={"size": 8, "offset": 2},
                    )
                )
            ], className='box', style={'padding-bottom':'15px'})
        ],width=8),

        dbc.Col([
            html.Img(src=app.get_asset_url('ev.png'), style={'width': '80%', 'position':'relative','margin':'auto','display':'block','opacity':'60%'}),
        ],width=4,style={'display':'flex'}),
    ],style={'padding-bottom':'15px'}),
   
            
#LAST PART | INFORMATION

    dbc.Row([
        dbc.Col([
            html.P('Group 14', style={"font-weight":'bold',"font-size":'22px'}),
            html.Ul("• Ana Resende, m20211018", style={"font-size":"18px"}),
            html.Ul("• Gonçalo Brancas, m20210760", style={"font-size":"18px"}),
            html.Ul("• Ricardo Gomes, m20211028", style={"font-size":"18px"}),
            html.Ul("• Tiago Quaresma, m20210766", style={"font-size":"18px"}),
        ],width=6),

        dbc.Col([
            html.P('Sources', style={"font-weight":'bold',"font-size":'22px'}),
            html.P("Eurostat:", style={"font-size":"20px"}),
            html.P([html.A('- Complete energy balances', 
                    href='https://ec.europa.eu/eurostat/databrowser/view/NRG_BAL_C__custom_938495/bookmark/table?lang=en,en&bookmarkId=3dd894c7-087c-418e-aa27-1e5945f5c705', target='_blank')]
                    , style={"font-size":"18px"}),
            html.P([html.A('- Electricity prices for household consumers', 
                    href='https://ec.europa.eu/eurostat/databrowser/view/NRG_PC_204__custom_2480521/default/table?lang=en ', target='_blank')]
                    , style={"font-size":"18px"}),
            html.P([html.A('- Supply, transformation and consumption of electricity', 
                    href='https://ec.europa.eu/eurostat/databrowser/view/NRG_CB_E__custom_2480511/default/table?lang=en', target='_blank')]
                    , style={"font-size":"18px"}),
            html.P([html.A('- Share of zero emission vehicles in newly registered passenger cars', 
                    href='https://ec.europa.eu/eurostat/databrowser/view/CLI_ACT_NOEC__custom_2233679/bookmark/table?lang=en&bookmarkId=7d6ad82b-6be6-46eb-920d-1cbbaa37bb33', target='_blank')]
                    , style={"font-size":"18px"}),

        ],width=6)

    ],style={'background-color':'#89B7D3','padding':'10px'})
])

    



#-----------------------------------------------Callbacks--------------------------------------------------------------

#barplot
@app.callback(
    Output('bar_graph', 'figure'),
    Input('type_energy', 'value'))
     


def interactive_barplot(value_type_energy):
    
    dff = df[df.Type == value_type_energy]
    fig1 = px.bar(data_frame=dff, x= 'Total', y= 'Sources', 
#                 title= '1. Sources of the consumed electricity (Gw/h)', 
                 orientation = 'h',
#                 width=600, height=400,
                 )
    return fig1



#europe map
@app.callback(
    Output('graphmap', "figure"), 
    Input('source', "value"))



def graph_map(source_options):
   
    data_choropleth = dict(type='choropleth',
                           locations=df_map['Country'],  
                           locationmode='country names',
                           autocolorscale = False,
                           z=df_map[source_options],
                           colorbar= {'title':'Gw/h (log)'},
                           colorscale='ylgnbu'
                          )

    layout_choropleth = dict(geo=dict(scope='europe',  
                                      projection=dict(type='natural earth'
                                                     ),
                                      showcoastlines=True,
                                      projection_scale=True,
                                      showland=True,   
                                      landcolor='white',
                                      lakecolor='white',
                                      showocean=True,   # default = False
                                      oceancolor='azure',
                                      bgcolor= 'rgba(0,0,0,0)'
                                     ), margin=dict(l=0,
                                r=0,
                                b=0,
                                t=30,
                                pad=0), paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                             
                             title=dict(x=.5 # Title relative position according to the xaxis, range (0,1)
                                       )
                            )
      
    fig = go.Figure(data=data_choropleth, layout=layout_choropleth)
    fig.update_geos(fitbounds="locations", visible=False, 
#                    showcoastlines=False, 
                    showsubunits=False,
                    showframe=False
)

    return fig




#sunburst plot
@app.callback(
    Output('cheese_graph', 'figure'),
    Input ('energy_country', 'value')
    
)

def cheesy_plot(country_name):
    
    dff = [df['Sources'], df['Type'], df['Total']]
    dfc = pd.concat(dff, axis = 1).set_index('Sources')
    cols = df.columns.drop(['Total','Type'])
    test = df[cols.to_list()].copy().set_index('Sources')
    dfc = dfc.join(test)
    dfc.reset_index(inplace = True)
   
    fig = px.sunburst(dfc, path=['Type','Sources'], values= country_name ,color='Sources', 
                            color_discrete_sequence = px.colors.sequential.haline_r).update_traces(hovertemplate = '%{label}<br>' + 'Sources: %{value} Gw/h')
    fig = fig.update_layout({
        'margin' : dict(t=0, l=0, r=0, b=10),
                        'paper_bgcolor': '#F9F9F8',
                        'font_color':'#363535'}
        )
    return fig


#Tree Map
@app.callback(
    Output('tree_graph', 'figure'),
    Input ('energy_sector', 'value')
)


def tree_map(country_sector):
    
    fig_tree = px.treemap(df_sector, path=[px.Constant("Electricity Consumption"), 'Sector', 'Sub-sector'], 
                values=country_sector,
                color='Sector',
                color_discrete_map={'(?)':'lightgrey', 'Industry Sector': 'lightskyblue', 
                                    'Transport Sector':'darkkhaki',
                                   'Commercial and Public Services Sector':'yellowgreen',
                                   'Household Sector':'cornflowerblue',
                                   'Agriculture and Forestry Sector':'cornsilk',
                                   'Fishing Sector':'mediumturquoise'},
#                width=800, height=600
                )
    
    fig_tree.update_layout(margin = dict(t=50, l=25, r=25, b=25))

    return fig_tree


# Running the app
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)


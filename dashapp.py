activate_this = "/home/qingyao/ncov/dash_env/bin/activate_this.py"
exec(open(activate_this).read(), {'__file__': activate_this})
import dash
from flask import Flask
import dash_table
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
from dash.dependencies import Input, Output
from pymongo import MongoClient
import numpy as np
import json, re, sys, math, os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# from urllib.request import urlopen
# import ssl

# ssl._create_default_https_context = ssl._create_unverified_context

print('hello Im running the App!', file=sys.stderr)
external_stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']#['/Users/pgweb/Downloads/WHITE_EDITION/css/style.css']

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

colors = {
    'background': '#111111',
    'text': '#747474',
    'pink':'#ccafaf',
    'green':'#cae8d5'
}


styles = {
    'H1': {
        'font-family':"Open Sans",
        'font-size': '3vh',
        'color':colors['text'],
        'text-align': 'center'
    },
    'H2': {
        'font-family':"Open Sans",
        'font-size': '2vh',
        'color':colors['text'],
        'text-align': 'center'
    },
    'toggle': {
        'font-family':"Open Sans",
        #'font-size': '2vh',
        'color':colors['text'],
    }

}

marker = {
    'size': 7,
    'small_size': 5
}


translate_map = {}
eng_chn = {}
with open('country_translation.csv') as f:
    for l in f:
        chn, eng = l.strip().split(',') 
        translate_map[chn] = eng
        eng_chn[eng] = chn
#https://github.com/longwosion/geojson-map-china/blob/master/china.json
with open('china.json','r') as f:
    provinces = json.load(f)
with open('world.geo.json') as f:
    world = json.load(f)

provinces['features']+=[i for i in world['features'] if i['properties']['name'] != 'China']
for province in provinces['features']:
    province['id']=province['properties']['name']

#load county data
with open('county_case.json') as f:
    county = json.load(f)
### load data
all_files = sorted(os.listdir('data_dict'))
with open('data_dict/'+all_files[-1]) as f: #latest
    data = json.load(f)

curr_dat = {'province':[],'no':[],'no_cure':[], 'no_death':[]}
for province, dat in data.items():
    
    curr_dat['province'].append(province)
    # curr_dat['province_id'].append(name_id_map[province])
    curr_dat['no'].append(dat['confirm']['no'][-1])
    if dat['cure']['no']:
        curr_dat['no_cure'].append(dat['cure']['no'][-1])
    else:
        curr_dat['no_cure'].append(0)
    if dat['death']['no']:
        curr_dat['no_death'].append(dat['death']['no'][-1])
    else:
        curr_dat['no_death'].append(0)

with open('oversea_data_dict/'+sorted(os.listdir('oversea_data_dict'))[-1]) as f: #latest
    oversea_data = json.load(f)

unknown_countries = set()
for country, dat in oversea_data.items():
    try: 
        data.update({translate_map[country]:dat})
    except KeyError:
        with open('new_data.log','a') as f:
            print(datetime.now().strftime('%d/%m/%Y'), country, 'new country', sep = ' -- ', file = f)
            unknown_countries.add(country)
        continue 

for country, dat in oversea_data.items():
    if country in unknown_countries:
        continue

    curr_dat['province'].append(translate_map[country])
    
    curr_dat['no'].append(dat['confirm']['no'][-1])
    if dat['cure']['no']:
        curr_dat['no_cure'].append(dat['cure']['no'][-1])
    else:
        curr_dat['no_cure'].append(0)
    if dat['death']['no']:
        curr_dat['no_death'].append(dat['death']['no'][-1])
    else:
        curr_dat['no_death'].append(0)
df = pd.DataFrame.from_dict(curr_dat)#.astype({'province_id':str})

country_population = {}
skip = 1 
with open('country_population.txt') as f:
    for l in f:
        if skip:
            skip-=1
            continue
        country,_,_,_,population,_ = l.strip().split('\t')
        country_population[country] = int(population)
with open('province_population.csv') as f:
    for l in f:
        prov, pop = l.strip().split(',')
        country_population[prov]=int(pop)

df['text'] = 'Cured:' + df['no_cure'].astype(str) + '<br>' + 'Dead:' + df['no_death'].astype(str)
df2 = df
df2 = df2[df2['province'].isin(country_population)]
df2['population'] = [country_population[i] for i in df2['province']]
df2['no'] /= df2['population']
df2['no_cure'] /= df2['population']
df2['no_death'] /= df2['population']
def plot_chroplethmap(df):
    fig = go.Figure(go.Choroplethmapbox(geojson=provinces, locations=df.province, z=df.no,
                                        text=df.text,
                                        # colorscale="BuPu", 
                                        colorscale= [
                                            [0, 'rgb(16, 16, 16)'],        #0
                                            [1./10000, 'rgb(62, 58, 13)'], #10
                                            [1./1000, 'rgb(109, 101, 10)'],  #100
                                            [1./100, 'rgb(156, 143, 6)'],   #1000
                                            [1./10, 'rgb(203, 186, 3)'],       #10000
                                            [1., 'rgb(250, 228, 0)'],             #100000
                                            ],
                                        zmin=0, zmax=max(df.no),
                                        showscale=False,
                                        marker_opacity=0.7, marker_line_width=0))

    fig.update_layout(mapbox_style="carto-darkmatter",
                    plot_bgcolor= colors['background'],
                    paper_bgcolor= colors['background'],
                      mapbox_zoom=1.2, mapbox_center = {"lat": 50, "lon": 10})
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

fig_map = plot_chroplethmap(df)
fig_map2 = plot_chroplethmap(df2)

def plot_newVStotal(df):
    fig = make_subplots()
    fig.add_trace(go.Scatter(x=df['no'],
                    y=df['new_ma2day'],
                    line = {'color': colors['pink']},
                    name='last 2 days',
                    showlegend = False
                    )),
    fig.add_trace(go.Scatter(x=df['no'],
                    y=df['new_ma5day'],
                    line = {'color': colors['green']},
                    name='last 5 days',
                    showlegend = False
                    ))
    no_max = max(df['no'])*1.05
    fig.add_trace(go.Scatter(x=[5, round(no_max/5)*5],
                            y=[1, round(no_max/5)],
                            mode='lines',
                            name='20% growth',
                            showlegend = True,
                            line={'dash':'dot', 'color': colors['text']}))
    fig.add_trace(go.Scatter(x=[10, round(no_max/10)*10],
                            y=[1, round(no_max/10)],
                            mode='lines',
                            name='10% growth',
                            showlegend = True,
                            line={'dash':'dash', 'color': colors['text']}))
    fig.add_trace(go.Scatter(x=[33, round(no_max/33)*33],
                            y=[1, round(no_max/33)],
                            mode='lines',
                            name='3% growth',
                            showlegend = True,
                            line={'dash':'dot', 'color': colors['text']}))
    fig.update_layout(plot_bgcolor=colors['background'], 
                        paper_bgcolor = colors['background'],
                        font={'color':colors['text']},
                        xaxis={'showgrid':False,'range':[1,np.log10(no_max)]},
                        yaxis={'showgrid':True,'gridcolor':colors['text']},
                        xaxis_title="Total cases",
                        yaxis_title="New cases",
                        margin={"r":0,"t":0,"l":0,"b":0},
                        xaxis_type="log", 
                        yaxis_type="log")
    return fig

def plot_trend(dataframe_1,dataframe_2,dataframe_3):

    fig = make_subplots()

    fig.add_trace(go.Scatter(x=dataframe_1['time'][-2:], 
                            y=dataframe_1['no'][-2:],
                            name = 'Confirmed',
                            showlegend=False,
                            line = {'dash':'dash', 'color': '#FFE400'},
                            marker = {'color':colors['background'], 'size':marker['small_size'],
                            'line':dict(
                                    color='#FFE400',
                                    width=1.5
                                )},          
                            ))  

    fig.add_trace(go.Scatter(x=dataframe_1['time'], 
                            y=(dataframe_1['no']*0.3).round().astype(int),
                            name = '30% of total',
                            showlegend=True,
                            line = {'dash':'dot', 'color': colors['text']},
                            ))  

    fig.add_trace(go.Scatter(x=dataframe_1['time'], 
                            y=(dataframe_1['no']/10).round().astype(int),
                            name = '10% of total',
                            showlegend=True,
                            line = {'dash':'dash', 'color': colors['text']},
                            ))  

    fig.add_trace(go.Scatter(x=dataframe_1['time'], 
                            y=(dataframe_1['no']/33.3).round().astype(int),
                            name = '3% of total',
                            showlegend=True,
                            line = {'dash':'dashdot', 'color': colors['text']},
                            ))  

    fig.add_trace(go.Scatter(x=dataframe_1['time'][:-1], 
                            y=dataframe_1['no'][:-1],
                            mode = 'lines+markers',
                            name = 'Confirmed',
                            marker = {'color':'#FFE400', 'size':marker['size'],
                            'line':dict(
                                    color=colors['background'],
                                    width=1
                                )}
                            ))
 
    fig.add_trace(go.Scatter(x=dataframe_2['time'][-2:], 
                            y=dataframe_2['no'][-2:],
                            name = 'Cured',
                            showlegend=False,
                            line = {'dash':'dash', 'color': '#14A76C'},
                            marker = {'color':colors['background'], 'size':marker['small_size'],
                            'line':dict(
                                    color='#14A76C',
                                    width=1.5
                                )}
                            ))
 
    fig.add_trace(go.Scatter(x=dataframe_2['time'][:-1], 
                            y=dataframe_2['no'][:-1],
                            name = 'Cured',
                            mode = 'lines+markers',
                            marker = {'color':'#14A76C', 'size':marker['size'],
                            'line':dict(
                                    color=colors['background'],
                                    width=1
                                )}
                            ))

    fig.add_trace(go.Scatter(x=dataframe_3['time'][-2:], 
                            y=dataframe_3['no'][-2:],
                            name = 'Dead',
                            showlegend=False,
                            line = {'dash':'dash', 'color': '#FF652F'},
                            marker = {'color':colors['background'], 'size':marker['small_size'],
                            'line':dict(
                                    color='#FF652F',
                                    width=1.5
                                )}
                            ))

    fig.add_trace(go.Scatter(x=dataframe_3['time'][:-1], 
                            y=dataframe_3['no'][:-1],
                            name = 'Dead',
                            mode = 'lines+markers',
                            marker = {'color':'#FF652F', 'size':marker['size'],
                            'line':dict(
                                    color=colors['background'],
                                    width=1
                                )}
                            ))

    fig.update_layout(
    plot_bgcolor=colors['background'], 
    paper_bgcolor = colors['background'],
    font={'color':colors['text']},
    xaxis={'showgrid':False},
    yaxis={'showgrid':True,'gridcolor':colors['text']},
    legend_orientation="h",
    margin={"r":0,"t":0,"l":0,"b":0})

    return fig

def get_china_plot(dat):
    df1 = pd.DataFrame.from_dict({**dat['China']['confirm'],**{'state':['confirmed']*len(dat['China']['confirm']['no'])}})
    df2 = pd.DataFrame.from_dict({**dat['China']['cure'],**{'state':['cured']*len(dat['China']['cure']['no'])}})
    df3 = pd.DataFrame.from_dict({**dat['China']['death'],**{'state':['dead']*len(dat['China']['death']['no'])}})

    df1['time'] = pd.to_datetime(df1['time']).dt.date
    df1 = df1.drop_duplicates('time', keep = 'last')
    df2['time'] = pd.to_datetime(df2['time']).dt.date
    df2 = df2.drop_duplicates('time', keep = 'last')
    df3['time'] = pd.to_datetime(df3['time']).dt.date
    df3 = df3.drop_duplicates('time', keep = 'last')

    return plot_trend(df1,df2,df3)

def get_world_plot(dat):
    
    for country, val in dat.items():
        if country in county:
            continue
#        elif country == 'China':
#            continue
        else:
#            print(country)
        
            tmp1 = pd.Series(val['confirm']['no'], index = val['confirm']['time'])
            tmp1 = tmp1.loc[~tmp1.index.duplicated(keep='last')]
            tmp2 = pd.Series(val['cure']['no'], index = val['cure']['time'])
            tmp2 = tmp2.loc[~tmp2.index.duplicated(keep='last')]
            tmp3 = pd.Series(val['death']['no'], index = val['death']['time'])
            tmp3 = tmp3.loc[~tmp3.index.duplicated(keep='last')]

            if 'df1' in locals():
                df1 = pd.concat([df1, tmp1], axis = 1).sum(axis = 1, skipna = True) 
            else:
                df1 = tmp1
            if 'df2' in locals():
                df2 = pd.concat([df2, tmp2], axis = 1).sum(axis = 1, skipna = True) 
            else:
                df2 = tmp2
            if 'df3' in locals():
                df3 = pd.concat([df3, tmp3], axis = 1).sum(axis = 1, skipna = True) 
            else:
                df3 = tmp3
            

    df1 = pd.DataFrame(df1.rename('no'))
    df1['state'] = 'confirmed'
    df1.reset_index(inplace = True)
    df1.rename(columns = {'index':'time'}, inplace = True)
#    print(df1.columns)

    df2 = pd.DataFrame(df2.rename('no'))
    df2['state'] = 'cured'
    df2.reset_index(inplace = True)
    df2.rename(columns = {'index':'time'}, inplace = True)

    df3 = pd.DataFrame(df3.rename('no'))
    df3['state'] = 'dead'
    df3.reset_index(inplace = True)
    df3.rename(columns = {'index':'time'}, inplace = True)

    df1['time'] = pd.to_datetime(df1['time']).dt.date
    df1 = df1.drop_duplicates('time', keep = 'last')
    df2['time'] = pd.to_datetime(df2['time']).dt.date
    df2 = df2.drop_duplicates('time', keep = 'last')
    df3['time'] = pd.to_datetime(df3['time']).dt.date
    df3 = df3.drop_duplicates('time', keep = 'last')

    return plot_trend(df1,df2,df3)

china_plot = get_china_plot(data)
world_plot = get_world_plot(data)
            
last_update_time = datetime.fromisoformat(data['China']['confirm']['time'][-1])
last_update_time = last_update_time.strftime("%b %d, %-I %p")

server = Flask(__name__)
server.secret_key ='test'

#@server.route("/")
#def hello():
#    return ('Hello')
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server = server)
app.title = 'COVID-19 timeline tracking'
app.config.suppress_callback_exceptions = True 
app.layout = dbc.Container(className="mt-4", fluid = True,
                    children = [dbc.Row([
                                        dbc.Col(html.Div([
                                            html.H1('COVID-19', id='title',style = styles['H1']),
                                            html.H2('Last Update: {} (GMT+8)'.format(last_update_time), id='subtitle',style = styles['H2']),
                                            html.H2('Data Source：WHO and NHC China', id='subtitle2',style = styles['H2']),
                                            daq.DarkThemeProvider(children=[daq.BooleanSwitch(id = 'toggle_data', color = '#fae400', label = {'style':styles['toggle'],'label':'per capita'})],theme = {'dark':True}),
                                            dcc.Graph(id='map',figure=fig_map, config={'displayModeBar':False})]),
                                            # width={'size':6, 'offset':1}
                                            xl = 6, 
                                            lg = 12,
                                            # md = 12
                                            ),
                                        dbc.Col(
                                            html.Div([
                                                html.H2('World prevalence', id='subtitle_main_plot', style = styles['H2']),
                                                dcc.Graph(
                                                id='main_plot',
                                                figure=world_plot,
                                                config={'displayModeBar':False}
                                                )]), 
                                                # width={'size':5}
                                                xl = 3,
                                                lg = 4,
                                                md = 6,
                                                style={ "margin-top":"40px"}

                                            )
                                        ,
                                        

                    # html.Div([
                    #         dcc.Markdown("""
                    #             **Click Data**

                    #             Click on points in the graph.
                    #         """),
                    #         html.Pre(id='click-data', style=styles['pre'])
                    #     ], className='three columns'),
                    
        

            # dbc.Col(html.Div([
            #     html.H1('点地图显示地区',style = styles['H1']),
            #     # html.Br(),
            #     # html.H1('截取放大'),
            #     # html.Br(),
            #     # html.H1('双击复原')]), 
            #     ]),
            #     align="center", width={'size':2,'offset':1},),
                                        
                                        dbc.Col(
                                            html.Div([
                                                html.H2('', id = 'title_infect_plot', style = styles['H2']),
                                                dcc.Graph(
                                                    id='infect_plot',
                                                    figure={'layout': {
                                                    'plot_bgcolor': colors['background'],
                                                    'paper_bgcolor': colors['background'],
                                                    'xaxis':{'showgrid':False, 'visible':False},
                                                    'yaxis':{'showgrid':False, 'visible':False},
                                                    'font': {
                                                        'color': colors['text']
                                                    }}},
                                                    config={'displayModeBar':False}
                                                    )
                                                ]),
                                                xl = 3,
                                                lg = 4,
                                                md = 6,
                                                style={ "margin-top":"40px"}
                                                # width={'size':5}
                                                )
                                        ,
                                        dbc.Col(
                                            html.Div([
                                                html.H2('', id = 'title_newVStotal', style = styles['H2']),
                                                dcc.Graph(
                                                    id='newVStotal_plot',
                                                    figure={'layout': {
                                                    'plot_bgcolor': colors['background'],
                                                    'paper_bgcolor': colors['background'],
                                                    'xaxis':{'showgrid':False, 'visible':False},
                                                    'yaxis':{'showgrid':False, 'visible':False},
                                                    'font': {
                                                        'color': colors['text']
                                                    }}},
                                                    config={'displayModeBar':False}
                                                    )
                                                ]),
                                                xl = 6, 
                                                lg = 12,
                                                style={ "margin-top":"40px"}
                                                # width={'size':5}
                                                ),
                                        dbc.Col([html.Div([html.H2(id = 'county_header', style = styles['H2']),
                                                    html.Br()]),
                                                dbc.Table(id='counties')

                                            ], 
                                            # width = 3,
                                            xl = 3,
                                            lg = 4,
                                            md = 6,
                                            style={ "margin-top":"40px"})
                                        ,
                                ])
                                        
])
    



# @app.callback(
#     Output('click-data', 'children'),
#     [Input('map', 'clickData')])
# def display_click_data(clickData):
#     return json.dumps(clickData, indent=2)

@app.callback(
    Output('main_plot', 'figure'),
    [Input('map', 'clickData')])
def toggle_main_plot(clickData):
    sel_province = clickData['points'][0]['location'].encode('utf-8').decode('utf-8')
    if sel_province in county:
        return china_plot
    else:
        return world_plot

@app.callback(
    Output('map','figure'),
    [Input('toggle_data','on')])
def toggle_per_capita(on):
    if on:
        print(df2.shape)
        return fig_map2
    else:
        print(df.shape)
        return fig_map

@app.callback(
    Output('subtitle_main_plot', 'children'),
    [Input('map', 'clickData')])
def toggle_main_plot(clickData):
    sel_province = clickData['points'][0]['location'].encode('utf-8').decode('utf-8')
    if sel_province in county:
        return 'China prevalence'
    else:
        return 'World prevalence'


@app.callback(
    Output('counties', 'children'),
    [Input('map', 'clickData')])
def display_counties(clickData):
    sel_province = clickData['points'][0]['location'].encode('utf-8').decode('utf-8')
    if sel_province in county:
        return_txt = ''
        con=[]
        cure=[]
        death=[]
        for i in county[sel_province].values():
            con.append(i[0])
            cure.append(i[1])
            death.append(i[2])

        df = pd.DataFrame({'区域': list(county[sel_province].keys()),'Confirmed':con, 'Cured':cure,'Dead':death})
        df.sort_values(by='Confirmed', inplace=True, ascending=False)
        # dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
        return dash_table.DataTable(
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto'
            },
            style_cell={'maxWidth': '60px','textAlign': 'left','backgroundColor':'black'},
            style_table={'maxHeight': '300px','overflowY': 'scroll','font-size':"16px",'backgroundColor':'black', 'color':colors['text']},
            data=df.to_dict('records'),
            columns=[{'id': c, 'name': c, 'selectable': False} for c in df.columns],
            style_as_list_view=True,
        )  
    else:
        return ''

@app.callback(
    Output('county_header', 'children'),
    [Input('map', 'clickData')])
def display_counties(clickData):
    sel_province = clickData['points'][0]['location'].encode('utf-8').decode('utf-8')
    if sel_province in county:        
        return '{}各市区'.format(sel_province)
    else:
        return ''

@app.callback(
    Output('infect_plot', 'figure'),
    [Input('map', 'clickData')])
def plot_infect(clickData):
    sel_province = clickData['points'][0]['location'].encode('utf-8').decode('utf-8')
    df1 = pd.DataFrame.from_dict({**data[sel_province]['confirm'],**{'state':['confirmed']*len(data[sel_province]['confirm']['no'])}})
    df2 = pd.DataFrame.from_dict({**data[sel_province]['cure'],**{'state':['cured']*len(data[sel_province]['cure']['no'])}})
    df3 = pd.DataFrame.from_dict({**data[sel_province]['death'],**{'state':['dead']*len(data[sel_province]['death']['no'])}})
    df1['time'] = pd.to_datetime(df1['time']).dt.date
    df1 = df1.drop_duplicates('time', keep = 'last')
    df2['time'] = pd.to_datetime(df2['time']).dt.date
    df2 = df2.drop_duplicates('time', keep = 'last')
    df3['time'] = pd.to_datetime(df3['time']).dt.date
    df3 = df3.drop_duplicates('time', keep = 'last')

    return plot_trend(df1,df2,df3)

@app.callback(
    Output('newVStotal_plot', 'figure'),
    [Input('map', 'clickData')])
def plot_newinfect(clickData):
    sel_province = clickData['points'][0]['location'].encode('utf-8').decode('utf-8')
    df1 = pd.DataFrame.from_dict({**data[sel_province]['confirm'],**{'state':['confirmed']*len(data[sel_province]['confirm']['no'])}})
    df1['time'] = pd.to_datetime(df1['time']).dt.date
    df1.drop_duplicates('time', keep = 'last', inplace = True)
    df1.reset_index(drop=True, inplace = True)
    df1['new'] = df1['no'].diff()
    df1['new_ma2day'] = pd.DataFrame({'0':df1['new'],
                                     '1':[None]+list(df1['new'][:-1])}).mean(axis=1)
    df1['new_ma5day']=pd.DataFrame({'0':df1['new'],
                                   '1':[None]+list(df1['new'][:-1]),
                                   '2':[None]*2+list(df1['new'][:-2]),
                                   '3':[None]*3+list(df1['new'][:-3]),
                                   '4':[None]*4+list(df1['new'][:-4])}).mean(axis=1)
    df1.dropna(inplace=True)
    df1['new_ma2day']=df1['new_ma2day'].round().astype(int)
    df1['new_ma5day']=df1['new_ma5day'].round().astype(int)
    df1=df1[:-1]
    return plot_newVStotal(df1)


@app.callback(
    Output('title_infect_plot', 'children'),
    [Input('map', 'clickData')])
def update_title_infect_plot(clickData):
    sel_province = clickData['points'][0]['location'].encode('utf-8').decode('utf-8')
    if sel_province in county:
        return '{}感染情况'.format(sel_province)
    else:
        return 'Current situation in {}'.format(sel_province)
    
@app.callback(
    Output('title_newVStotal', 'children'),
    [Input('map', 'clickData')])
def update_title_infect_plot(clickData):
    sel_province = clickData['points'][0]['location'].encode('utf-8').decode('utf-8')
    return 'new cases VS total cases in {}'.format(sel_province)
 

# app.layout = html.Div([say_hi()])
if __name__ == '__main__':
    app.run_server(host = '0.0.0.0',port=8051)#, debug=True)

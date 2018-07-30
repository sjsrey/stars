import pandas as pd
import numpy as np
import plotly.graph_objs as go
import pysal as ps   
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output , State
from scipy import stats
from scipy.stats import rankdata

app = dash.Dash()
app.config['suppress_callback_exceptions']=True # If you have an id in the layout/callbacks that is not in the callbacks/layout

# Boostrap CSS.
app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})  # noqa: E501

# Reading Data
# Read http://darribas.org/gds_scipy16/ipynb_md/01_data_processing.html
csv_path = ps.examples.get_path('usjoin.csv')
shp_path = ps.examples.get_path('us48.shp')

usjoin = pd.read_csv(csv_path)
us48_map = ps.pdio.read_files(shp_path)

# Columns to calculate PCR's and Moran'I as strings/objects
years = list(range(1929, 2010))                  
cols_to_calculate = list(map(str, years))

# For dropdowns
years_aux = [str(i) for i in years] # Converting each element to string (it could be list(map(str, years)))
years_options = [{'label': i, 'value': i} for i in years_aux]

# us48_map has a left zero in states that have FIPS under 10
#usjoin.STATE_FIPS
#us48_map.STATE_FIPS
us48_map.STATE_FIPS = us48_map.STATE_FIPS.astype(int)

df_map_raw = us48_map.merge(usjoin, on='STATE_FIPS')

rk_map_raw = us48_map.merge(usjoin, on='STATE_FIPS')
for year in years: rk_map_raw[str(year)] = rankdata(df_map_raw[str(year)], method='ordinal')



# Calculating PCR
def calculate_pcr(x):
    return x / np.mean(x)

all_pcrs = usjoin[cols_to_calculate].apply(calculate_pcr)

usjoin[cols_to_calculate] = all_pcrs

W = ps.queen_from_shapefile(shp_path)
W.transform = 'r'

df_map_pcr = us48_map.merge(usjoin, on='STATE_FIPS') 

rk_map_pcr = us48_map.merge(usjoin, on='STATE_FIPS')
for year in years: rk_map_pcr[str(year)] = rankdata(df_map_pcr[str(year)], method='ordinal')


###########################################         
# Aux Objects (Time Series, sliders, etc. #
###########################################        
step = 5
years_by_step = list(map(str, list(range(1929, 2010, step))))         

# Calculating Moran'I for every column
morans = []
for i in cols_to_calculate:
    aux = ps.Moran(df_map_pcr[i], W).I
    morans.append(aux)

############################################################  

 

############################################################  
# Layout     #
##############  
app.layout = html.Div(
    html.Div([    
        html.Div([
                    
                    html.H1(children='Web STARS'),
                    
                    html.Div(children='''
                        Web STARS: A web-based version of Space-Time Analysis of Regional Systems
                    '''),
                
                html.Div([                        
                        dcc.Checklist(
                            id='auto-check',
                            options=[{'label': ' Time Travel Animation ', 'value': 'auto'}],
                            values=[],
                        ),
                        ], style={'padding-top': '20px', 'display': 'inline-block', 'float': 'left'}),
                
                html.Div([
                        dcc.Slider(
                            id='years-slider',
                            min=min(years),
                            max=max(years),
                            value=min(years),
                            marks={str(year): str(year) for year in years_by_step},
                        ),                        
                        dcc.Interval(
                            id='interval-event',
                            interval=24*60*60*1000,
                            n_intervals=0
                        ),
                    
                    dcc.RadioItems(
                            id='type_data_selector',
                            options=[
                                {'label': 'Per Capita Relative Ratio (PCR)', 'value': 'pcr'},
                                {'label': 'Raw Income Data', 'value': 'raw'}
                            ],
                            value='pcr',
                            #labelStyle={'display': 'inline-block'},
                            style={'margin-top': '50'}
                    )
                                
                        ], style={'width':800, 'margin':25, 'float': 'left'}),
                    
                ], className="row"),
        
      html.Div([
            dcc.Checklist(
                id='spatial_travel-check',
                options=[{'label': ' Spatial Travel Animation ', 'value': 'auto'}],
                values=[],
            ),
            dcc.Interval(
                id='spatial_interval-event',
                interval=24*60*60*1000,
                n_intervals=0
            ),
        ], className="row"),
        
        html.Div([            
            html.Div([
                        
                            dcc.Graph(
                                id='choropleth-graph'
                            ),
                        
                            dcc.Graph( # ?dcc.Graph to learn more about the properties
                                id='timeseries-graph',
                            clear_on_unhover = 'True' # Sets the slider year when the mouse hover if off the graph
                            ),    
                        
                            # dcc.Graph(
                            #    id='timepath-graph'
                            #),
                                    
                    ], className="four columns"),        
            html.Div([                
                        
                        dcc.Graph(
                                id='scatter-graph'
                            ),
                        
                        html.P('Choose a pair of years for densities:'),
                        
                        html.Div([
                        dcc.Dropdown(
                            id='initial_years_dropdown',
                            options=years_options,
                            value='1929'
                        ),
                        dcc.Dropdown(
                            id='final_years_dropdown',
                            options=years_options,
                            value='2009'
                        )], className="row"),
                                
                            dcc.Graph(
                                id='density-graph' 
                            ),
                                               
                            #   dcc.Graph(
                            #    id='boxplot-graph'
                            #)            
                        
                    ], className="four columns"),        
            html.Div([
                            dcc.Graph(
                                id='timepath-graph'
                            ),
                             dcc.Graph(
                                id='boxplot-graph'
                            ),           
					 ], className="four columns"),    
        ], className="row")
    ], className='ten columns offset-by-one')
)




############################################################ 
@app.callback(
    Output('interval-event', 'interval'), 
    [Input('auto-check', 'values')],
    [State('interval-event', 'interval')]
)
def change_auto(checkedValues, interval):
    #print(checkedValues, interval)
    if (len(checkedValues) != 0): return 2*1000                      # AUTO is checked
    else:                         return 24*60*60*1000               # AUTO is not checked


#@app.callback(Output('years-slider', 'value'), [Input('interval-event', 'n_intervals')], events=[Event('interval-event', 'interval')])
@app.callback(
    Output('years-slider', 'value'), 
    [Input('interval-event', 'n_intervals')],
    [State('years-slider', 'value'), State('years-slider', 'min'), State('years-slider', 'max'), State('auto-check', 'values')]
)
def update_slider(n, theYear, minValue, maxValue, checkedValues):
    if (len(checkedValues) == 0): return theYear                     # AUTO is not checked
    newValue = theYear + 1
    if (newValue > maxValue): newValue = minValue
    #print(n, theYear, minValue, maxValue, newValue, checkedValues)
    return newValue


# hide the options of the spatial_travel-check when AUTO is checked
@app.callback(
    Output('spatial_travel-check', 'options'), 
    [Input('auto-check', 'values')],
)
def hide_show_spatial_travel_checkbox(checkedValues):
    print(checkedValues)
    if (len(checkedValues) != 0): return []                                    # AUTO is checked
    else: return [{'label': ' Spatial Travel Animation ', 'value': 'auto'}]    # AUTO is not checked

# clear the values of the spatial_travel-check when AUTO is checked or not
@app.callback(
    Output('spatial_travel-check', 'values'), 
    [Input('auto-check', 'values')],
)
def clear_values_of_spatial_travel_checkbox(checkedValues):
    #print(checkedValues)
    return []

# reset n_intervals in the Sspatial_interval-event when AUTO is checked or not
# reset n_intervals in the Sspatial_interval-event when year is changed in the years-slider
@app.callback(
    Output('spatial_interval-event', 'n_intervals'), 
    [Input('auto-check', 'values'), Input('years-slider','value')],
    [State('spatial_interval-event', 'n_intervals')],
)
def reset_n_intervals_of_spatial_interval_event(checkedValues, year, oldValue):
    #print(checkedValues, 'oldValue:', oldValue)
    return 0

# set the spatial_interval-event using the Spatial Travel Animation check box
@app.callback(
    Output('spatial_interval-event', 'interval'), 
    [Input('spatial_travel-check', 'values')],
    [State('spatial_interval-event', 'interval'), State('spatial_interval-event', 'n_intervals')]
)
def change_spatial_travel_interval(checkedValues, interval, n):
    print(checkedValues, interval, n)
    if (len(checkedValues) != 0): return 2*1000                      # AUTO is checked
    else:                         return 24*60*60*1000               # AUTO is not checked

############################################################ 



############################################################

@app.callback(
    Output('choropleth-graph', 'figure'),
    [Input('type_data_selector', 'value'),
     Input('timeseries-graph','hoverData'),
     Input('years-slider','value'), 
     Input('spatial_interval-event', 'n_intervals')],
    [State('spatial_travel-check', 'values')],
)
def update_map(type_data, year_hovered, year_selected_slider, n, checkedValues):
    
    if type_data == 'raw': 
        df_map = df_map_raw
        rk_map = rk_map_raw
        title_map = '(Raw)'
    
    else:
        df_map = df_map_pcr
        rk_map = rk_map_pcr
        title_map = '(PCR)'
    
    if year_hovered is None: 
        year = year_selected_slider
    
    else:
        year = year_hovered['points'][0]['x']

    heading = 'Income of US by State in ' + str(year)
    ranking = -1
    if (len(checkedValues) != 0):
        ranking = n % len(df_map[str(year)]) #+ 1
        msg = str(ranking) + 'th'
        if (ranking == 1): msg = '1st'
        if (ranking == 2): msg = '2nd'
        if (ranking == 3): msg = '3rd'
        for i, rank in enumerate(rk_map[str(year)]):
            if (rank == ranking): msg += ' ' + rk_map['STATE_NAME'][i] + ': {0:.2f}'.format(df_map[str(year)][i])
        heading += '<br>(' + msg + ')'
    
    scl  = [[0.0, '#eff3ff'],[0.2, '#c6dbef'],[0.4, '#9ecae1'],[0.6, '#6baed6'],[0.8, '#3182bd'],[1.0, '#08519c']]
    scl2 = [[0.0, '#ffffff'],[1.0, '#FFFF00']]

    Choropleth_Data = [ dict(
                        type='choropleth',
                        colorscale = scl,
                        autocolorscale = False,
                        locations = df_map['STATE_ABBR'],
                        z = df_map[str(year)],
                        locationmode = 'USA-states',
                        text = df_map['Name'],
                        marker = dict(
                            line = dict (
                                color = 'rgb(255,255,255)',
                                width = 1
                            ) ),
                        colorbar = dict(
                            thickness = 10,                          # default: 30 
                            title = title_map)
                        ) ]
        
    Choropleth_Layout =  dict(
                            #title = 'Income of US by State in 1929<br>(Hover for breakdown)',
                            title = heading,
                            geo = dict(
                            scope='usa',
                            projection=dict( type='albers usa' ),
                            showlakes = True,
                            lakecolor = 'rgb(255, 255, 255)'),
                        )
    Choropleth = {
        'data': Choropleth_Data,
        'layout': Choropleth_Layout
    }

    if (ranking > 0):
        Choropleth_highlighted = [ dict(
                        type='choropleth',
                        colorscale = scl2,
                        autocolorscale = False,
                        locations = df_map['STATE_ABBR'],
                        z = [1 if i == ranking else 0 for i in rk_map[str(year)]],
                        showscale = False,
                        locationmode = 'USA-states',
                        text = df_map['Name'],
                        marker = dict(
                            opacity = 0.5,
                            line = dict (
                                color = 'rgb(255,255,255)',
                                width = 0
                            ) ),
                        ) ]
        Choropleth = {
            'data': Choropleth_Data + Choropleth_highlighted,
            'layout': Choropleth_Layout
        }

    return Choropleth

############################################################

# https://dash.plot.ly/interactive-graphing

@app.callback(
    Output('scatter-graph', 'figure'),
    [Input('type_data_selector', 'value'),
     Input('timeseries-graph','hoverData'),
     Input('years-slider','value'),
     Input('choropleth-graph','selectedData'),
     Input('choropleth-graph','clickData')])
def update_scatter(type_data, year_hovered, year_selected_slider, states_selected_choropleth, state_clicked_choropleth):
    
    if type_data == 'raw': 
        df_map = df_map_raw
    
    else:
        df_map = df_map_pcr
        
    if year_hovered is None: 
        year = year_selected_slider
    
    else:
        year = year_hovered['points'][0]['x']
    
    if ((states_selected_choropleth is None) & (state_clicked_choropleth is None)):
        state_selected = ['California']
        title_graph = state_selected[0]
    
    elif ((states_selected_choropleth is None) & (state_clicked_choropleth is not None)):
        state_selected = [str(state_clicked_choropleth['points'][0]['text'])]
        title_graph = state_selected[0]
    
    else:
        state_selected = [i['text'] for i in states_selected_choropleth['points']]# state_selected_choropleth['points'][0]['text']
        title_graph = 'Multiple States'
    
    #df_map[str(year)] = [48,2,3,4,5,6,7,8,9,60,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,1]

    print(df_map[str(year)])
    VarLag = ps.lag_spatial(W, df_map[str(year)])
    Var = df_map[str(year)]

    states = np.array(df_map['Name'])
    colors = np.where(np.isin(states, state_selected), '#FF0066', '#0066FF')
    
    b,a = np.polyfit(Var, VarLag, 1)
    line0 = { 'x':[min(Var), max(Var)], 'y': [a + i * b for i in [min(Var), max(Var)]] }

    Scatter_Data = [
                        {
                            'x': Var, 
                            'y': VarLag,
                            'mode': 'markers',
                            'marker': {'size': 10,
                                       'color': colors},
                            'name': str(year),
                        'text': df_map['Name']},
                        {
                            'x': line0['x'], 
                            'y': line0['y'],
                            'mode': 'lines',
                            'line': {'color': '#009999'},
                            'name': 'Reg'}
    ]
    
    if (states_selected_choropleth is not None):
        var = [v['z'] for v in states_selected_choropleth['points']]
        varLag = [VarLag[v['pointIndex']] for v in states_selected_choropleth['points']]
        b,a = np.polyfit(var, varLag, 1)
        line1 = { 'x':[min(Var), max(Var)], 'y': [a + i * b for i in [min(Var), max(Var)]] }
        line2 = { 'x':[min(var), max(var)], 'y': [a + i * b for i in [min(var), max(var)]] }

        # recalculation line1 to fit scatter-graph area                                  # y = a * x + b
        minVar = min(Var)
        maxVar = max(Var)
        aa = (line1['y'][1] - line1['y'][0]) / (line1['x'][1] - line1['x'][0])
        bb = line1['y'][0] - aa * line1['x'][0]
        if (line1['y'][0] > max(VarLag)): minVar = (line0['y'][1] - bb) / aa             # x = ( y - b ) / a
        if (line1['y'][0] < min(VarLag)): minVar = (line0['y'][0] - bb) / aa             # x = ( y - b ) / a
        if (line1['y'][1] > max(VarLag)): maxVar = (line0['y'][1] - bb) / aa             # x = ( y - b ) / a
        if (line1['y'][1] < min(VarLag)): maxVar = (line0['y'][0] - bb) / aa             # x = ( y - b ) / a
        line1 = { 'x':[minVar, maxVar], 'y': [a + i * b for i in [minVar, maxVar]] }

        #print(var)
        Scatter_Data.append(
        	{
        		'x': line1['x'], 
                'y': line1['y'],
                'mode': 'lines', 
                'line': {'color': '#FF6600'},
                #'line': {'color': '#0000FF'},
                'name': 'Reg'}
        )
        Scatter_Data.append(
        	{
        		'x': line2['x'], 
                'y': line2['y'],
                'mode': 'lines', 
                'line': {'color': '#FF0000'},
                'name': 'Reg'}
        )
    
    Scatter_Layout = {
                        'xaxis': {'title': 'Original Variable'},
                        'yaxis': {'title': "Lagged Variable"},
                     'showlegend': False,
                     'title': 'Scatterplot for {} <br>{} highlighted'.format(year, title_graph)
                     }
    
    Scatter = {
        'data': Scatter_Data,
        'layout': Scatter_Layout
    }
    return Scatter

############################################################
    

@app.callback(
    Output('timeseries-graph', 'figure'),
    [Input('timeseries-graph','hoverData'),
    Input('years-slider', 'value')],
    [State('years-slider', 'min')]
)
def update_TimeSeries(year_hovered, year_selected_slider, minValue):
    
    if year_hovered is None:    
        theIDX = year_selected_slider - minValue
    
    else:
        theIDX = year_hovered['points'][0]['x'] - minValue
    
    TimeSeries_Data = [
        {
            'x': years, 
            'y': morans,
            'mode': 'lines', 
            'name': 'Moran\'s I'
        },
        {
            'x': [years[theIDX]], 
            'y': [morans[theIDX]],
            'mode': 'markers', 
            'marker': {'size': 10},
            'name': 'Moran\'s I',
            'showlegend': False,
            'hoverinfo': 'none'
        } # To supress the tooltip
    ]    

    TimeSeries_Choropleth_Layout = {
        'xaxis': {'title': 'Years'},
        'yaxis': {'title': "Moran's I"}
    }
            
    TimeSeries = {
        'data': TimeSeries_Data,
        'layout': TimeSeries_Choropleth_Layout
    }
             
    return TimeSeries


#################################################################



@app.callback(
    Output('boxplot-graph', 'figure'),
    [Input('type_data_selector', 'value'),
     Input('timeseries-graph','hoverData'),
     Input('choropleth-graph','selectedData'),
     Input('years-slider','value')])
def update_boxplot(type_data, year_hovered, states_selected_choropleth, year_selected_slider):
    
    if type_data == 'raw': 
        df_map = df_map_raw
    
    else:
        df_map = df_map_pcr

    selected = []
    if ((states_selected_choropleth is None)):
        state_selected = 'California'
    else:
        state_selected = [i['text'] for i in states_selected_choropleth['points']]
        selected = [i['pointIndex'] for i in states_selected_choropleth['points']]
    
    if year_hovered is None: 
        year = year_selected_slider
    
    else:
        year = year_hovered['points'][0]['x']

    #states = np.array(df_map['Name'])
    #colors = np.where(np.isin(states, state_selected), '#FF0066', '#0066FF')
        
    trace0 = go.Box(
        y = df_map[str(year)],
        name = 'Boxplot of the variable',
        boxpoints='all',                                             # Show the underlying point of the boxplot
        jitter=0.15,                                                 # Degree of fuzziness
        pointpos=0,                                                  # Adjust horizontal location of point
        #marker = dict(color = '#FF0066'),
        line = dict(color = '#444'),
        selected = dict(marker = dict(color = '#FF0066')),
        unselected = dict(marker = dict(color = '#0066FF', opacity = 1.0)),
        selectedpoints = selected,
    )
    BoxPlot_Data = [trace0]
    #print(BoxPlot_Data)
    
    BoxPlot = {
                'data': BoxPlot_Data,
                'layout': {'title': 'Boxplot of the year {}'.format(str(year))}
              } 
    return BoxPlot

 


############################################################


@app.callback(
    Output('timepath-graph', 'figure'),
    [Input('type_data_selector', 'value'),
     Input('choropleth-graph','clickData'),
     Input('timeseries-graph','hoverData'),
     Input('years-slider', 'value')],
     [State('years-slider', 'min')])

def update_timepath(type_data, state_clicked, year_hovered, year_selected_slider, minValue):
    
    if type_data == 'raw': 
        df_map = df_map_raw
    
    else:
        df_map = df_map_pcr
    
    if state_clicked is None: 
        chosen_state = 'California'
    
    else:
        chosen_state = str(state_clicked['points'][0]['text'])
        
    if year_hovered is None:    
        theIDX = year_selected_slider - minValue
    
    else:
        theIDX = year_hovered['points'][0]['x'] - minValue
    
    if year_hovered is None:    
        year = year_selected_slider
    
    else:
        year = year_hovered['points'][0]['x']
    
    def calculate_lag_value(x):
        return ps.lag_spatial(W, x)
    
    all_lagged = df_map[cols_to_calculate].apply(calculate_lag_value)
    
    state_row_index = list(df_map['Name']).index(chosen_state)
    
    VarLag = all_lagged.iloc[state_row_index,:]
    Var = df_map[cols_to_calculate].iloc[state_row_index,:]
    
    TimePath_Data = [
                        {
                            'x': Var[[theIDX]], 
                            'y': VarLag[[theIDX]],
                            'mode': 'markers',
                            'marker': {'size': 12},
                            'name': '',
                        'text': str(year)},
                        {
                            'x': Var, 
                            'y': VarLag,
                            'mode': 'lines', 
                            'name': 'Path',
                        'hoverinfo': 'none'}
                    ]
    
    TimePath_Layout = {
                        'xaxis': {'title': 'Original Variable'},
                        'yaxis': {'title': "Lagged Variable"},
                     'showlegend': False,
                     'title': 'Time-path for {}<br> Highlighted {}'.format(str(chosen_state), str(year))
                     }
    
    TimePath = {
        'data': TimePath_Data,
        'layout': TimePath_Layout
    }
    return TimePath

############################################################ 




@app.callback(
    Output('density-graph', 'figure'),
    [Input('type_data_selector', 'value'),
     Input('initial_years_dropdown','value'),
     Input('final_years_dropdown','value'),
     Input('choropleth-graph','clickData'),
     Input('spatial_interval-event', 'n_intervals')],
     [State('spatial_travel-check', 'values')])
def update_density(type_data, initial_year, final_year, state_clicked, n, checkedValues):
    
    if type_data == 'raw': 
        df_map = df_map_raw
        rk_map = rk_map_raw
    
    else:
        df_map = df_map_pcr
        rk_map = rk_map_pcr
        
    
    pair_of_years = [initial_year, final_year]
    
    
    if state_clicked is None: 
        chosen_state = 'California'
    
    else:
        chosen_state = str(state_clicked['points'][0]['text'])
   
    ranking = -1
    if (len(checkedValues) != 0):
    	ranking = n % len(df_map[str(year)]) + 1
        
    else:
       ranking = rk_map.loc[list(df_map['Name']).index(chosen_state), initial_year]
    
    state_row_index = list(rk_map[initial_year]).index(ranking)
    
    initial_state_value = df_map[initial_year][state_row_index]
    final_state_value = df_map[final_year][state_row_index]
        
    X1 = np.array(df_map[pair_of_years[0]])
    X2 = np.array(df_map[pair_of_years[1]])
    
    kde1 = stats.gaussian_kde(X1, bw_method = 'silverman')
    kde2 = stats.gaussian_kde(X2, bw_method = 'silverman')
    
    # Joint grid
    min_grid_aux = min(np.concatenate([X1, X2]))
    max_grid_aux = max(np.concatenate([X1, X2]))
    X_grid = np.linspace(min_grid_aux - 0.1 * abs(max_grid_aux), 
                         max_grid_aux + 0.1 * abs(max_grid_aux), 
                         10000)
    
    dens1 = kde1.evaluate(X_grid)
    dens2 = kde2.evaluate(X_grid)
    
    Density_Data = [  # Densities traces
                        {
                            'x': X_grid, 
                            'y': dens1,
                            'mode': 'lines',
                         'fill': 'tozeroy',
                            'name': initial_year,
                        'text': 'Year of {}'.format(initial_year),
                        'line': {'color': '#AAAAFF',
                                 'width': 3}},
                          {
                            'x': X_grid, 
                            'y': dens2,
                            'mode': 'lines',
                         'fill': 'tozeroy',
                            'name': final_year,
                        'text': 'Year of {}'.format(final_year),
                        'line': {'color': '#FF0000',
                                 'width': 3}},
            
            
                     # Segments of lines traces
                     {
                            'x': [initial_state_value, initial_state_value], # x-values of each point do draw a line
                            'y': [0, kde1.evaluate(initial_state_value)[0]], # Extract only the value from an array: https://stackoverflow.com/questions/21030621/how-to-extract-value-from-a-numpy-ndarray
                            'mode': 'lines',
                            'name': 'name_to_put',
                        'text': 'text_to_put_line',
                        'showlegend': False,
                        'line': {'color': '#AAAAFF',
                                 'width': 3}},
                     {
                            'x': [final_state_value, final_state_value], # x-values of each point do draw a line
                            'y': [0, kde2.evaluate(final_state_value)[0]],
                            'mode': 'lines',
                            'name': 'name_to_put_line',
                        'text': 'text_to_put_line',
                        'showlegend': False,
                        'line': {'color': '#FF0000',
                                 'width': 3}}
                          
                    ]
    
    Density_Layout = {
                        'xaxis': {'title': 'Original Variable'},
                        'yaxis': {'title': "Density Estimation"},
                     'title': '<b>{}</b> locations in densities for {} and {}'.format(chosen_state, initial_year, final_year)
                     }
    
    Density = {
        'data': Density_Data,
        'layout': Density_Layout
    }
    return Density

############################################################     



if __name__ == '__main__':
    app.run_server() # ,port=8055 debug=True,port=8000, host='0.0.0.0'

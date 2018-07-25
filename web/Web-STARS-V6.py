import pandas as pd
import numpy as np
import plotly.graph_objs as go
import pysal as ps   
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output , State
from scipy import stats

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

# us48_map has a left zero in states that have FIPS under 10
#usjoin.STATE_FIPS
#us48_map.STATE_FIPS
us48_map.STATE_FIPS = us48_map.STATE_FIPS.astype(int)

df_map_raw = us48_map.merge(usjoin, on='STATE_FIPS')

# Columns to calculate PCR's and Moran'I as strings/objects
years = list(range(1929, 2010))                  
cols_to_calculate = list(map(str, years))

# For dropdowns
years_aux = [str(i) for i in years] # Converting each element to string (it could be list(map(str, years)))
years_options = [{'label': i, 'value': i} for i in years_aux]

# Calculating PCR
def calculate_pcr(x):
    return x / np.mean(x)

all_pcrs = usjoin[cols_to_calculate].apply(calculate_pcr)

usjoin[cols_to_calculate] = all_pcrs

W = ps.queen_from_shapefile(shp_path)
W.transform = 'r'

df_map_pcr = us48_map.merge(usjoin, on='STATE_FIPS') 



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
					
					html.H1(children='Weeb STARS'),
					
					html.Div(children='''
						Web STARS: A web-based version of Space-Time Analysis of Regional Systems
					'''),
              
                	html.Div([					
						dcc.Checklist(
							id='auto-check',
							options=[{'label': ' PLAY TIME ', 'value': 'auto'}],
							values=[],
						),
						], style={'padding-top': '62px', 
                               'display': 'inline-block', 
                               'float': 'left'}),
                
                 html.Div([					
						dcc.Checklist(
							id='range-poor-rick-check',
							options=[{'label': ' RANGE POOR to RICH STATES ', 'value': 'auto'}],
							values=[],
						),
						], style={'padding-top': '62px', 
                               'display': 'inline-block', 
                               'float': 'left'}),   
                    
              html.Div([
                         
        				dcc.Slider(
        					id='years-slider',
        					min=min(years),
        					max=max(years),
        					value=min(years),
        					marks={str(year): str(year) for year in years_by_step}
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
                            labelStyle={'display': 'inline-block'},
                            style={'margin-top': '50'}
                    )
                                ]) #, style={'width':400, 'margin':25}
					
				], className="twelve columns"), # "row"
		html.Div([			
			html.Div([
                        
							dcc.Graph(
								id='choropleth-graph'
							),
						
							dcc.Graph( # ?dcc.Graph to learn more about the properties
								id='timeseries-graph',
                            clear_on_unhover = 'True' # Sets the slider year when the mouse hover if off the graph
							),	
                        
             				dcc.Graph(
								id='timepath-graph'
							),
                                    
					], className="six columns"),		
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
                                               
   							dcc.Graph(
								id='boxplot-graph'
							)            
                        
					], className="six columns"),		
						
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
	print(checkedValues, interval)
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
	print(n, theYear, minValue, maxValue, newValue, checkedValues)
	return newValue

############################################################ 



############################################################

@app.callback(
	Output('choropleth-graph', 'figure'),
	[Input('type_data_selector', 'value'),
    Input('timeseries-graph','hoverData'),
    Input('years-slider','value')])
def update_map(type_data, year_hovered, year_selected_slider):
    
    if type_data == 'raw': 
        df_map = df_map_raw
        title_map = 'US Income (U$)'
    
    else:
        df_map = df_map_pcr
        title_map = 'US Per Capita Ratio (PCR)'
    
    if year_hovered is None: 
        year = year_selected_slider
    
    else:
        year = year_hovered['points'][0]['x']
    
    scl = [[0.0, 'rgb(242,240,247)'],[0.2, 'rgb(218,218,235)'],[0.4, 'rgb(188,189,220)'],\
            [0.6, 'rgb(158,154,200)'],[0.8, 'rgb(117,107,177)'],[1.0, 'rgb(84,39,143)']]

    scl2 = [[0.0, '#ffffff'], [1.0, '#FFFF00']]
             
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
    							width = 2
    						) ),
    					colorbar = dict(
    						title = title_map)
    					) ]
    	
    highlighted_polygons = [ dict(
					type='choropleth',
					colorscale = scl2,
					autocolorscale = False,
					locations = df_map['STATE_ABBR'],
                    z = [0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
                    #opacity = 1,
                    showscale = False,
					locationmode = 'USA-states',
					text = df_map['Name'],
					marker = dict(
						opacity = 0.5,
						line = dict (
							color = 'rgb(255,255,0)',
							width = 0
						) ),
					) ]
    
    Choropleth_Layout =  dict(
                        	dragmode = "select",
                           #title = 'Income of US by State in 1929<br>(Hover for breakdown)',
                        	geo = dict(
                            scope='usa',
                            projection=dict( type='albers usa' ),
                            showlakes = True,
    	                    lakecolor = 'rgb(255, 255, 255)'
                           ),
                           title = 'Map data for US in {} <br> Clicking updates timepath and densities'.format(year)
                        )
    Choropleth = {
    	'data': Choropleth_Data + highlighted_polygons,
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
     Input('choropleth-graph','selectedData')])
def update_scatter(type_data, year_hovered, year_selected_slider, state_selected_choropleth):
    
    if type_data == 'raw': 
        df_map = df_map_raw
    
    else:
        df_map = df_map_pcr
    
    if state_selected_choropleth is None: 
        state_selected = 'California'
    
    else:
        state_selected = [i['text'] for i in state_selected_choropleth['points']]# state_selected_choropleth['points'][0]['text']
    
    if year_hovered is None: 
        year = year_selected_slider
    
    else:
        year = year_hovered['points'][0]['x']
    
    VarLag = ps.lag_spatial(W, df_map[str(year)])
    Var = df_map[str(year)]
    
    states = np.array(df_map['Name'])
    colors = np.where(np.isin(states, state_selected), '#0000FF', '#000000')
    
    b,a = np.polyfit(Var, VarLag, 1)
    
    Scatter_Data = [
    					{
    						'x': Var, 
    						'y': VarLag,
    						'mode': 'markers',
                            'marker': {'size': 15,
                                       'color': colors},
    						'name': str(year),
                        'text': df_map['Name']},
    					{
    						'x': [min(Var), max(Var)], 
    						'y': [a + i * b for i in [min(Var), max(Var)]],
    						'mode': 'lines', 
    						'name': 'Reg'}
                    ]
    
    Scatter_Layout = {
    					'xaxis': {'title': 'Original Variable (Hovered)'},
    					'yaxis': {'title': "Lagged Variable (Hovered)"},
                     'showlegend': False,
                     'title': 'Scatterplot for {} <br>{} highlighted'.format(year, state_selected)
    				 }
    
    Scatter = {
    	'data': Scatter_Data,
    	'layout': Scatter_Layout
    }
    return Scatter

############################################################
    

@app.callback(
	Output('timeseries-graph', 'figure'),
	[Input('years-slider', 'value')],
	[State('years-slider', 'min')]
)
def update_TimeSeries(year_selected_slider, minValue):
	theIDX = year_selected_slider - minValue
	
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
     Input('years-slider','value')])
def update_boxplot(type_data, year_hovered, year_selected_slider):
    
    if type_data == 'raw': 
        df_map = df_map_raw
    
    else:
        df_map = df_map_pcr
    
    if year_hovered is None: 
        year = year_selected_slider
    
    else:
        year = year_hovered['points'][0]['x']
        
    trace0 = go.Box(
        y = df_map[str(year)],
        name = 'Boxplot of the variable',
        boxpoints='all', # Show the underlying point of the boxplot
        jitter=0.15, # Degree of fuzziness
        pointpos=0 # Adjust horizontal location of point
    )
    BoxPlot_Data = [trace0]
    
    BoxPlot = {
    			'data': BoxPlot_Data,
    			'layout': {'title': 'Boxplot of the year {}'.format(str(year))}
    		  } 
    return BoxPlot

 


############################################################


@app.callback(
	Output('timepath-graph', 'figure'),
	[Input('type_data_selector', 'value'),
     Input('choropleth-graph','clickData')])
def update_timepath(type_data, state_clicked):
    
    if type_data == 'raw': 
        df_map = df_map_raw
    
    else:
        df_map = df_map_pcr
    
    if state_clicked is None: 
        chosen_state = 'California'
    
    else:
        chosen_state = str(state_clicked['points'][0]['text'])
        
    def calculate_lag_value(x):
        return ps.lag_spatial(W, x)
    
    all_lagged = df_map[cols_to_calculate].apply(calculate_lag_value)
    
    state_row_index = list(df_map['Name']).index(chosen_state)
    
    VarLag = all_lagged.iloc[state_row_index,:]
    Var = df_map[cols_to_calculate].iloc[state_row_index,:]
    
    TimePath_Data = [
    					{
    						'x': Var, 
    						'y': VarLag,
    						'mode': 'markers',
                            'marker': {'size': 12},
    						'name': '',
                        'text': Var.index},
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
                     'title': 'Time-path for {}'.format(str(chosen_state))
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
     Input('choropleth-graph','clickData')])
def update_density(type_data, initial_year, final_year, state_clicked):
    
    if type_data == 'raw': 
        df_map = df_map_raw
    
    else:
        df_map = df_map_pcr
    
    pair_of_years = [initial_year, final_year]
    
    if state_clicked is None: 
        chosen_state = 'California'
    
    else:
        chosen_state = str(state_clicked['points'][0]['text'])
    
    state_row_index = list(df_map['Name']).index(chosen_state)
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
        

            
            
            
            

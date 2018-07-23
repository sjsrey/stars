#import matplotlib
import pandas as pd
import numpy as np
#import geopandas as gpd
#import cenpy as cen
#import plotly.offline as offline
import plotly.graph_objs as go
import pysal as ps   
#import libpysal
#import plotly.plotly as py
#import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, Event #, State

# Installed via pip as in https://flask-caching.readthedocs.io/en/latest/
#from flask_caching import Cache

app = dash.Dash()
app.config['suppress_callback_exceptions']=True # If you have an id in the layout/callbacks that is not in the callbacks/layout

# Boostrap CSS.
app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})  # noqa: E501

# Reading Data
# Read http://darribas.org/gds_scipy16/ipynb_md/01_data_processing.html
csv_path = ps.examples.get_path('usjoin.csv')
shp_path = ps.examples.get_path('us48.shp')

usjoin = pd.read_csv(csv_path)

# Columns to calculate PCR's and Moran'I as strings/objects
years = list(range(1929, 2010))                  
cols_to_calculate = list(map(str, years)) 

# Calculating PCR
def calculate_pcr(x):
    return x / np.mean(x)

all_pcrs = usjoin[cols_to_calculate].apply(calculate_pcr)


usjoin[cols_to_calculate] = all_pcrs

W = ps.queen_from_shapefile(shp_path)
W.transform = 'r'

us48_map = ps.pdio.read_files(shp_path)

# us48_map has a left zero in states that have FIPS under 10
#usjoin.STATE_FIPS
#us48_map.STATE_FIPS
us48_map.STATE_FIPS = us48_map.STATE_FIPS.astype(int)

df_map = us48_map.merge(usjoin, on='STATE_FIPS') 



############################################################            
# Time series #
###############        
step = 8
years_by_step = list(map(str, list(range(1929, 2010, step))))         

# Calculating Moran'I for every column
morans = []
for i in cols_to_calculate:
    aux = ps.Moran(df_map[i], W).I
    morans.append(aux)
    
	
TimeSeries_Data =[
					{
						'x': years, 
						'y': morans,
						'mode': 'lines', 
						'name': 'Moran\'s I'
					},
					{
						'x': years, 
						'y': morans,
						'mode': 'markers', 
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
						
        				dcc.Slider(
        					id='years-slider',
        					min=min(years),
        					max=max(years),
        					value=min(years),
        					marks={str(year): str(year) for year in years_by_step},
        				),						
						dcc.Interval(
							id='graph-update',
							interval=1*1000,
							n_intervals=0
						),
                                ], style={'width':800, 'margin':25})
					
				], className="row"),

		html.Div([			
			html.Div([
                    
                        html.P('', # The title label will update in the callback function
                    			id = 'choropleth-title',
                    			style = {'fontWeight':600}
        		          ),
                        
							dcc.Graph(
								id='example-graph'#,
								#figure = Choropleth
							),
						
							dcc.Graph(
								id='example-graph-2',
								figure = TimeSeries 
							),	
                        
             				dcc.Graph(
								id='example-time-path'#,
								#figure = TimePath 
							),
                                    
					], className="six columns"),		
			html.Div([				
						
                        dcc.Graph(
								id='example-graph-3'#,
								#figure = Scatter 
							),
                        
							dcc.Graph(
								id='example-graph-4'#,
								#figure = BoxPlot 
							)
					], className="six columns"),		
						
		], className="row")

	], className='ten columns offset-by-one')
)

#@app.callback(Output('years-slider', 'value'), events=[Event('graph-update', 'interval')])
@app.callback(Output('years-slider', 'value'), [Input('graph-update', 'n_intervals')], events=[Event('graph-update', 'interval')])
def update_slider(n):
	#print(year_selected_slider)
	#print(year)
	minValue=min(years)
	maxValue=max(years)
	newValue = n % (maxValue - minValue + 1) + minValue
	#if (newValue > maxValue): newValue = minValue
	print(n, newValue)
	return newValue

############################################################  

@app.callback(
	Output('choropleth-title', 'children'),
	[Input('example-graph-2','hoverData'),
    Input('years-slider','value')])
def update_map_title(year_hovered, year_selected_slider):
    if year_hovered is None: 
        year = year_selected_slider
        
    
    else:
        year = year_hovered['points'][0]['x']
    return 'US PCR Data by state \
				in year {0}'.format(year)

############################################################

@app.callback(
	Output('example-graph', 'figure'),
	[Input('example-graph-2','hoverData'),
    Input('years-slider','value')])
def update_map(year_hovered, year_selected_slider):
    
    if year_hovered is None: 
        year = year_selected_slider
    
    else:
        year = year_hovered['points'][0]['x']
    
    scl = [[0.0, 'rgb(242,240,247)'],[0.2, 'rgb(218,218,235)'],[0.4, 'rgb(188,189,220)'],\
            [0.6, 'rgb(158,154,200)'],[0.8, 'rgb(117,107,177)'],[1.0, 'rgb(84,39,143)']]

    print(scl)
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
    						title = "US Income per capita (US$)")
    					) ]
    	
    Choropleth_Layout =  dict(
                        	#title = 'Income of US by State in 1929<br>(Hover for breakdown)',
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
    return Choropleth

############################################################

# https://dash.plot.ly/interactive-graphing

@app.callback(
	Output('example-graph-3', 'figure'),
	[Input('example-graph-2','hoverData'),
     Input('years-slider','value')]) # Input('years-slider','value')
def update_scatter_hovered(year_hovered, year_selected_slider):
    
    if year_hovered is None: 
        year = year_selected_slider
        
    else:
        year = year_hovered['points'][0]['x']
    
    VarLag = ps.lag_spatial(W, df_map[str(year)]) 

    
	
    Var = df_map[str(year)]
    
    b,a = np.polyfit(Var, VarLag, 1)

    
    Scatter_Data = [
    					{
    						'x': Var, 
    						'y': VarLag,
    						'mode': 'markers',
                            'marker': {'size': 15},
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
                     'title': 'Click on a state to update time-path evolution'
    				 }
    
    Scatter = {
    	'data': Scatter_Data,
    	'layout': Scatter_Layout
    }
    return Scatter

############################################################


@app.callback(
	Output('example-graph-4', 'figure'),
	[Input('example-graph-2','hoverData'),
     Input('years-slider','value')])
def update_boxplot(year_hovered, year_selected_slider):
    
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


############################################################


@app.callback(
	Output('example-time-path', 'figure'),
	[Input('example-graph-3','clickData')])
def update_timepath(state_clicked):
    
    if state_clicked is None: 
        chosen_state = 'California'
    
    else:
        chosen_state = str(state_clicked['points'][0]['text'])
        
    def calculate_lag_value(x):
        return ps.lag_spatial(W, x)
    
    all_lagged = df_map[cols_to_calculate].apply(calculate_lag_value)
    
    state_row_index = list(df_map['Name']).index(chosen_state)
    state_row_index
    
    VarLag = all_lagged.iloc[state_row_index,:]
    Var = df_map[cols_to_calculate].iloc[state_row_index,:]
    #print(VarLag)
    TimePath_Data = [
    					{
    						'x': Var, 
    						'y': VarLag,
    						'mode': 'markers',
                            'marker': {'size': 12},
    						'name': 'name_to_put',
                        'text': 'text_to_put'},
    					{
    						'x': Var, 
    						'y': VarLag,
    						'mode': 'lines', 
    						'name': 'Reg'}
                    ]
    
    TimePath_Layout = {
    					'xaxis': {'title': 'Original Variable (Hovered)'},
    					'yaxis': {'title': "Lagged Variable (Hovered)"},
                     'showlegend': False,
                     'title': 'Time-path for {}'.format(str(chosen_state))
    				 }
    
    TimePath = {
    	'data': TimePath_Data,
    	'layout': TimePath_Layout
    }
    return TimePath

############################################################     



if __name__ == '__main__':
    app.run_server(debug=True)
#, host='0.0.0.0', port=5091
        

            
            
            
            

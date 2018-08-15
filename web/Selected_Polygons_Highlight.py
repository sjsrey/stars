#import matplotlib
import pandas as pd
import numpy as np
#import geopandas as gpd
#import cenpy as cen
import plotly.offline as offline
import plotly.graph_objs as go
import pysal as ps   
#import libpysal
import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash()

# Boostrap CSS.
app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})  # noqa: E501

# Reading Data
# Read http://darribas.org/gds_scipy16/ipynb_md/01_data_processing.html
csv_path = ps.examples.get_path('usjoin.csv')
shp_path = ps.examples.get_path('us48.shp')


usjoin = pd.read_csv(csv_path)
W = ps.queen_from_shapefile(shp_path)
W.transform = 'r'

us48_map = ps.pdio.read_files(shp_path)

# us48_map has a left zero in states that have FIPS under 10
#usjoin.STATE_FIPS
#us48_map.STATE_FIPS
us48_map.STATE_FIPS = us48_map.STATE_FIPS.astype(int)

df_map = us48_map.merge(usjoin, on='STATE_FIPS')



scl = [[0.0, '#7fcdbb'],[0.2, '#41b6c4'],[0.4, '#1d91c0'],\
            [0.6, '#225ea8'],[0.8, '#253494'],[1.0, '#081d58']]
scl2 = [[0.0, '#ffffff'], [1.0, '#FFFF00']]

df_flight_paths = pd.read_csv('https://raw.githubusercontent.com/suhanmappingideas/data/master/WY.csv')
#df_flight_paths = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2011_february_aa_flight_paths.csv')
df_flight_paths.head()

print(df_map['STATE_ABBR'])
        
flight_paths = []
for i in range( len( df_flight_paths ) ):
    flight_paths.append(
        dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = [ df_flight_paths['start_lon'][i], df_flight_paths['end_lon'][i] ],
            lat = [ df_flight_paths['start_lat'][i], df_flight_paths['end_lat'][i] ],
            mode = 'lines',
			showlegend=False,
            line = dict(
                width = 2,
                color = 'red',
            ),
            #opacity = float(df_flight_paths['cnt'][i])/float(df_flight_paths['cnt'].max()),
			 opacity = 1
        )
    )
   
############################################################  
# Choropleth_1 #
################
Choropleth_Data = [ dict(
					type='choropleth',
					colorscale = scl,
					autocolorscale = False,
					locations = df_map['STATE_ABBR'],
					z = df_map['1929'],
					locationmode = 'USA-states',
					text = df_map['Name'],
					
					marker = dict(
						line = dict (
							color = 'rgb(255,255,255)',
							width = 2
						) ),					
					colorbar = dict(
						title = "Title of the Legend (US$)")
					) ]
############################################################  
# Highlight POlygons_1 #
########################

Choropleth_Layout =  dict(
                    	#title = 'Income of US by State in 1929<br>(Hover for breakdown)',
                    	geo = dict(
                        scope='usa',
                        projection=dict( type='albers usa' ),
                        showlakes = True,
	                    lakecolor = 'rgb(255, 255, 255)'),
                    )
Choropleth = {
	'data': Choropleth_Data ,
	'layout': Choropleth_Layout
} 
############################################################  

############################################################  
# Choropleth_2 #
################
Choropleth_Data2 = [ dict(
					type='choropleth',
					colorscale = scl,
					autocolorscale = False,
					locations = df_map['STATE_ABBR'],
					z = df_map['1929'],
					locationmode = 'USA-states',
					text = df_map['Name'],
					marker = dict(
						line = dict (
							color = '#ffffff',
							width = 2
						) ),
					selected = dict(
					    marker = dict (
						    opacity = 1
						)
					),
					unselected = dict(
					    marker = dict (
						    opacity = 0.2
						)
					),
					 selectedpoints = [10,23,21],			
					colorbar = dict(
                   	title = "Title of the Legend (US$)")
					) ]
									
Choropleth_Layout2 =  dict(
                    	#title = 'Income of US by State in 1929<br>(Hover for breakdown)',
                    	geo = dict(
                        scope='usa',
                        projection=dict( type='albers usa' ),
                        showlakes = True,
	                    lakecolor = 'rgb(255, 255, 255)'),
                    )
Choropleth2 = {
	'data':  Choropleth_Data2,
	'layout': Choropleth_Layout2
} 
############################################################  

############################################################  
# Choropleth_3 #
################
Choropleth_Data3 = [ dict(
					type='choropleth',
					colorscale = scl,
					autocolorscale = False,
					locations = df_map['STATE_ABBR'],
					z = df_map['1929'],
					locationmode = 'USA-states',
					text = df_map['Name'],
					marker = dict(
						line = dict (
							color = '#FFFF00',
							width = 3
						) ),
					selected = dict(
					    marker = dict (
						    opacity = 1
						)
					),
					unselected = dict(
					    marker = dict (
						    opacity = 0.3
						)
					),
                    selectedpoints = [10,23,21],						
					colorbar = dict(
						title = "Title of the Legend (US$)")
					) ]
			
Choropleth_Layout3 =  dict(
                    	#title = 'Income of US by State in 1929<br>(Hover for breakdown)',
                    	geo = dict(
                        scope='usa',
                        projection=dict( type='albers usa' ),
                        showlakes = True,
	                    lakecolor = 'rgb(255, 255, 255)'),
                    )
Choropleth3 = {
	'data': Choropleth_Data3 ,
	'layout': Choropleth_Layout3
} 
############################################################  

############################################################  
# Choropleth_4 #
################
					
Choropleth_Data4 = [ dict(
					type='choropleth',
					colorscale = scl,
					autocolorscale = False,
					locations = df_map['STATE_ABBR'],
					z = df_map['1929'],
					locationmode = 'USA-states',
					text = df_map['Name'],
					marker = dict(
						line = dict (
							color = '#FFFF00',
							width = 3
						) ),
					selected = dict(
					    marker = dict (
						    opacity = 1
						)
					),
					unselected = dict(
					    marker = dict (
						    opacity = 0
						)
					),
                    selectedpoints = [10,23,21],						
					colorbar = dict(
						title = "Title of the Legend (US$)")
					) ]
			
Choropleth_Layout4 =  dict(
                    	#title = 'Income of US by State in 1929<br>(Hover for breakdown)',
                    	geo = dict(
                        scope='usa',
                        projection=dict( type='albers usa' ),
                        showlakes = True,
	                    lakecolor = 'rgb(255, 255, 255)'),
                    )
Choropleth4 = {
	'data': Choropleth_Data + Choropleth_Data4 ,
	'layout': Choropleth_Layout3
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
						Web STARS: A web-based version of Space-TIme Analysis of Regional Systems
					''')
					
				], className="row"),
		html.Div([			
			html.Div([
							dcc.Graph(
								id='example-graph',
								figure = Choropleth
							),
						
							dcc.Graph(
								id='example-graph-2',
								figure = Choropleth2 
							),	

							dcc.Graph(
								id='example-graph-3',
								figure = Choropleth3 
							),							

							dcc.Graph(
								id='example-graph-4',
								figure = Choropleth4 
							),								
							
					], className="ten columns"),		

						
		], className="row")
	], className='ten columns offset-by-one')
)
############################################################  

if __name__ == '__main__':
    app.run_server(debug=True)


        

            
            
            
            

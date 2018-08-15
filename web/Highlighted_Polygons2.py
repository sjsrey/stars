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



scl = [[0.0, '#eff3ff'],[0.2, '#c6dbef'],[0.4, '#9ecae1'],\
            [0.6, '#6baed6'],[0.8, '#3182bd'],[1.0, '#08519c']]
scl2 = [[0.0, '#ffffff'], [1.0, '#FFFF00']]

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
	'data': Choropleth_Data,
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
							color = 'rgb(255,255,255)',
							width = 2
						) ),
					colorbar = dict(
						title = "Title of the Legend (US$)")
					) ]
############################################################  
# Highlight POlygons_2 #
########################
highlighted_polygons2 = [ dict(
					type='choropleth',
					colorscale = scl2,
					autocolorscale = False,
					locations = df_map['STATE_ABBR'],
                    z = [0, 1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
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

					
Choropleth_Layout2 =  dict(
                    	#title = 'Income of US by State in 1929<br>(Hover for breakdown)',
                    	geo = dict(
                        scope='usa',
                        projection=dict( type='albers usa' ),
                        showlakes = True,
	                    lakecolor = 'rgb(255, 255, 255)'),
                    )
Choropleth2 = {
	'data': Choropleth_Data2 + highlighted_polygons2,
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
							color = 'rgb(255,255,255)',
							width = 2
						) ),
					colorbar = dict(
						title = "Title of the Legend (US$)")
					) ]
############################################################  
# Highlight POlygons_3 #
########################
highlighted_polygons3 = [ dict(
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

					
Choropleth_Layout3 =  dict(
                    	#title = 'Income of US by State in 1929<br>(Hover for breakdown)',
                    	geo = dict(
                        scope='usa',
                        projection=dict( type='albers usa' ),
                        showlakes = True,
	                    lakecolor = 'rgb(255, 255, 255)'),
                    )
Choropleth3 = {
	'data': Choropleth_Data3 + highlighted_polygons3,
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
							
					], className="ten columns"),		

						
		], className="row")
	], className='ten columns offset-by-one')
)
############################################################  

if __name__ == '__main__':
    app.run_server(debug=True)


        

            
            
            
            

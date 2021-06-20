# app.py
# Responsive dashboard for exploring Julia sets

# import standard libraries
import io
import base64

# import third-party libraries
import numpy as np 
import matplotlib.pyplot as plt 

import dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

import json
import pandas as pd
import flask


server = flask.Flask(__name__)
app = dash.Dash(server=server, title='Julia set generator')

colors = {
	'background': '#C1C0C6',
	'text': '#10110'
}


def julia_set(c_value, max_iterations, res_value):
	# convert string resolution to int pair
	res_value = [i for i in res_value.split()]

	for i in range(len(res_value)):
		if res_value[i] == 'by':
			del res_value[i]
			break
	h_range = int(res_value[1])
	w_range = int(res_value[0])

	# initialize ogrid
	y, x = np.ogrid[1.4: -1.4: h_range*1j, -1.7: 1.7: w_range*1j]
	z_array = x + y*1j

	iterations_until_divergence = max_iterations + np.zeros(z_array.shape)
	not_already_diverged = iterations_until_divergence < 10000

	for i in range(max_iterations):
		z_array = z_array**2 + c_value

		# make a boolean array for diverging indicies of z_array
		z_size_array = z_array * np.conj(z_array)
		diverging = z_size_array > 4
		diverging_now = diverging & not_already_diverged

		iterations_until_divergence[diverging_now] = i
		not_already_diverged = np.invert(diverging_now) & not_already_diverged

		# prevent overflow (numbers -> infinity) for diverging locations
		z_array[diverging_now] = 0 
		
	return iterations_until_divergence

colormaps = [
            'viridis', 'plasma', 'inferno', 'magma', 'cividis',
            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 
            'seismic','binary', 'gist_yarg', 'gist_gray', 'gray', 
            'bone', 'pink','spring', 'summer', 'autumn', 'winter', 
            'cool', 'Wistia','hot', 'afmhot', 'gist_heat', 'copper',
            'twilight', 'twilight_shifted', 'hsv','Pastel1', 'Pastel2', 
            'Paired', 'Accent', 'Dark2', 'Set1', 'Set2', 'Set3',
            'tab10', 'tab20', 'tab20b', 'tab20c','flag', 'prism', 
            'ocean', 'gist_earth', 'terrain', 'gist_stern',
            'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
            'gist_rainbow', 'rainbow', 'jet', 'turbo', 'nipy_spectral',
            'gist_ncar'
            ]

resolutions = ['900 by 600', '1500 by 1000', '3000 by 2000', '6000 by 4000']

# page layout and inputs specified
app.layout = html.Div(
	style=
		{'backgroundColor': colors['background'], 
		'font-family': 'sans-serif'}, 
	children=[
	html.H1(
		children='Jotter: Julia set plotter',
		style={
			'textAlign': 'center',
			'color': colors['text']
		}
	),

	html.Div(

		html.Div(
			children=[
			html.Label('Specify real value'),
				dcc.Input(
				id='creal',
				type='text',
				value='-0.744',
				style={'margin-top': '1vh'})
			], 
			style={
			'display':'inline-block',
			'width': '13vw',
			'margin-left': '10vw', 
			'margin-right': '1vw',
			'margin-top': '0vh',
			'text-align': 'center'
		}),

		html.Div(
			children=[
			html.Label('Specify imaginary value'),
				dcc.Input(
				id='cimag',
				type='text',
				value='0.148',
				style={'margin-top': '1vh'})
			], 
			style={
			'display':'inline-block',
			'width': '13vw',
			'margin-left': '1vw', 
			'margin-right': '1vw',
			'margin-top': '0vh',
			'text-align': 'center'
		}),
	),

	html.Div(
		children=[
		html.Label('Maximum iteration number'),
			dcc.Input(
			id='steps',
			type='number',
			value=10,
			min=0,
			max=1000,
			style={'margin-top': '1vh'})
		], 
		style={
		'display':'inline-block',
		'width': '13vw',
		'margin-left': '1vw', 
		'margin-right': '1vw',
		'margin-top': '0vh',
		'text-align': 'center'
	}),

	html.Div(
		children=[
		html.Label('Choose resolution:'),
		dcc.Dropdown(
				id='res',
				options=[{'value': x, 'label': x} 
						 for x in resolutions],
				value=resolutions[-2],
				style={
					'width': '12vw'})
		],
		style={
		'display': 'inline-block',
		'width': '10vw',
		'margin-right': '2vw',
		'margin-left':'3vw'
	}),


	html.Div(
		children=[
		html.Label('Choose color map:'),
			dcc.Dropdown(
				id='colormap',
				options=[{'value': x, 'label': x} 
						 for x in colormaps],
				value='twilight',
				style={
					'width': '12vw'})
		],
		style={
		'display':'inline-block',
		'width': '13vw',
		'margin-left': '4vw', 
		'margin-right': '0vw',
		'margin-top': 0,
		'text-align': 'top'
	}),

	html.Div(
		id='equation', 
		style={
			'textAlign': 'center',
			'font-family': 'serif', 
			'font-weight': 'bold',
			'margin-top': '2vh'
		}),

	html.Br(),
	dcc.Loading(
		html.Img(
			id='image',
			style={'display': 'inline-block',
					'width': '75vw',
					'height': '100vh',
					'margin-left': '12vw'})
	)
])

# responsive callbacks
@app.callback(Output(component_id='image', component_property='src'), 
			[Input(component_id='creal', component_property='value'),
			 Input(component_id='cimag', component_property='value'),
			 Input(component_id='colormap', component_property='value'),
			 Input(component_id='steps', component_property='value'),
			 Input(component_id='res', component_property='value')])
def display_choropleth(creal_value, cimag_value, colormap_value, steps_value, res_value):
	# convert inputs to args and build array
	max_iterations = steps_value
	creal = float(creal_value)
	cimag = float(cimag_value)
	c = creal + cimag*1j
	arr = julia_set(c, max_iterations, res_value)

	# save array as bytestring image for html.Img div
	buf = io.BytesIO()
	plt.imsave(buf, arr, cmap=colormap_value, format='png')
	data = base64.b64encode(buf.getbuffer()).decode("utf8") 
	return "data:image/png;base64,{}".format(data)


@app.callback(
	Output('equation', 'children'),
	[Input('creal', 'value'),
	Input('cimag', 'value')])
def display_equation(creal_value, cimag_value):
	# show equation that is iterated in the complex plane
	return f'Equation: z\u00b2 + ({creal_value} + {cimag_value}i) '


# run the app in the cloud
if __name__ == '__main__':
	app.run_server(debug=True, port=8003)
	# app.run_server(debug=True, host='0.0.0.0')














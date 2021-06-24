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
import flask
import json
from rq.serializers import JSONSerializer

from redis import Redis
from rq import Queue
from juliaset import julia_set

# import connection from worker.py
from worker import conn 
import time

q = Queue(connection=conn)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
app = dash.Dash(server=server, title='Julia set generator', external_stylesheets=external_stylesheets)

colors = {
	'background': '#fffff',
	'text': '#10110'
}
# steps_value = 100
# creal = 1
# cimag = 1
# colormap_value = 'twilight'

# max_iterations = steps_value
# creal = float(creal)
# cimag = float(cimag)
# c = creal + cimag*1j
# cmap = colormap_value
# julia = Jset()

# # send job to redis queue
# job = q.enqueue(julia.julia_set, c, max_iterations, '1000 by 1000', cmap, description='Julia set job')

# # wait while img is generated (but only for 500s max)
# while job.result is None:
# 	time.sleep(0.1)

# arr = job.result
# print (arr)
# buf = io.BytesIO()
# plt.imsave(buf, arr, cmap=cmap, format='png')
# data = base64.b64encode(buf.getbuffer()).decode("utf8") 
# return "data:image/png;base64,{}".format(data)

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

resolutions = ['900 by 600', '1200 by 800', '1500 by 1000', '1800 by 1200', '2100 by 1500', '3000 by 2000', '4002 by 2668']

# page layout and inputs specified
app.layout = html.Div(
	style=
		{'backgroundColor': colors['background'], 
		'font-family': 'sans-serif'}, 
	children=[
	html.H1(
		children='Jenerator',
		style={
			'textAlign': 'center',
			'color': colors['text'],
			'margin-bottom': '1vh',
			'margin-top': '1vh'
		}
	),

	html.H4(
		children='Julia set generator',
		style={
			'textAlign': 'center',
			'color': colors['text'],
			'margin-bottom': '0vh',
			'margin-top': '0vh',
			'margin-left': '45vw'
		}
	),


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
		

	html.Div(
		children=[
		html.Label('Maximum iteration number'),
			dcc.Input(
			id='steps',
			type='number',
			value=100,
			min=0,
			max=300,
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
				value=resolutions[2],
				style={
					'width': '15vw'})
		],
		style={
		'display': 'inline-block',
		'width': '15vw',
		'margin-right': '0vw',
		'margin-left':'3.5vw',
		'padding-left': '1vw'
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
		'margin-left': '2.5vw', 
		'margin-right': '0vw',
		'margin-top': 0,
		'text-align': 'top'
	}),

	html.Div(
		id='equation', 
		style={
			'textAlign': 'left',
			'font-family': "Open Sans", # "HelveticaNeue", "Helvetica Neue", Helvetica, Arial, sans-serif;', 
			'font-weight': 'normal',
			'margin-top': '0vh',
			'margin-left': '26vw',
			# 'line-height': 1.8,
			'font-size': '2.2rem'
		}),

	html.Br(),
	dcc.Loading(
		html.Img(
			id='image',
			style={'display': 'inline-block',
					'width': '80vw',
					'margin-left': '9vw'}),
		type='cube'
	)
])

# responsive callbacks ('component_id' etc are not strictly necessary but 
# are included for clarity)
@app.callback(Output(component_id='image', component_property='src'), 
			[Input(component_id='creal', component_property='value'),
			 Input(component_id='cimag', component_property='value'),
			 Input(component_id='colormap', component_property='value'),
			 Input(component_id='steps', component_property='value'),
			 Input(component_id='res', component_property='value')])
def display_juliaset(creal_value, cimag_value, colormap_value, steps_value, res_value):
	# convert inputs to args and build array
	max_iterations = steps_value
	creal = float(creal_value)
	cimag = float(cimag_value)
	c = creal + cimag*1j
	cmap = colormap_value

	# send job to redis queue
	job = q.enqueue(julia_set, c, max_iterations, res_value, cmap,
					ttl=1, failure_ttl=0.5)

	# wait while img is generated (but only for 500s max)
	while job.result is None:
		time.sleep(0.1)

	img = job.result
	return img


@app.callback(
	Output(component_id='equation', component_property='children'),
	[Input(component_id='creal', component_property='value'),
	Input(component_id='cimag', component_property='value')])
def display_equation(creal_value, cimag_value):
	# show equation that is iterated in the complex plane
	return f'z\u00b2 + {creal_value} + {cimag_value}i '


# run the app in the cloud
if __name__ == '__main__':
	app.run_server(debug=True, port=8014)
	# app.run_server(debug=True, host='0.0.0.0')





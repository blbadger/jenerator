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
from dash.exceptions import PreventUpdate

from redis import Redis
from rq import Queue
from juliaset import julia_set
from mandelfind import mandelfind

# import connection from worker.py
from worker import conn 
import time

q = Queue(connection=conn)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
app = dash.Dash(server=server, title='Julia set generator', external_stylesheets=external_stylesheets)

job = ''

colors = {
	'background': '#fffff',
	'text': '#10110'
}

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

resolutions = ['900 by 600', '1200 by 800', '1500 by 1000', '1800 by 1200', '2100 by 1500', '2400 by 1800']

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
			'margin-bottom': '3vh',
			'margin-top': '1vh'
		}
	),
	html.Div(
		children=[
		html.Img(
			id='mandelimage',
			style={'display': 'inline-block',
					'width': '30vw',
					'margin-left': '8vw',
					'margin-top': '2vh'}),
		], style={
		'display': 'inline-block',
		'width': '40vw'
		}
	),


	html.Div(
		children=[
		html.H4(
			children='Julia set generator',
			style={
				'textAlign': 'center',
				'color': colors['text'],
				'margin-bottom': '2vh',
				'margin-top': '0vh',
				'margin-left': '15vw',
				'width': '20vw',
				'height': '8vh',
				'display': 'inline-block',
				'vertical-align': 'top'
			}
		),
		html.Br(),

		html.Div(
			children=[
				html.Label('Specify real value'),
					dcc.Input(
					id='creal',
					type='text',
					value='-0.744',
					style={'margin-top': '1vh',
							'width': '12vw'})
			], 
			style={
			'display':'inline-block',
			'width': '13vw',
			'margin-left': '3vw', 
			'margin-right': '1vw',
			'margin-top': '0vh',
			'text-align': 'center',
			'vertical-align':'top'
		}),

		html.Div(
			children=[
				html.Label('Specify imaginary value'),
					dcc.Input(
					id='cimag',
					type='text',
					value='0.148',
					style={'margin-top': '1vh',
							'width': '17vw'})
			], 
			style={
			'display':'inline-block',
			'width': '17vw',
			'margin-left': '1vw', 
			'margin-right': '1vw',
			'margin-top': '0vh',
			'text-align': 'center',
			'vertical-align': 'top'
		}),
			

		html.Div(
			children=[
			html.Label('Maximum iterations'),
				dcc.Input(
				id='steps',
				type='number',
				value=100,
				min=0,
				max=300,
				style={'margin-top': '1vh',
						'width': '13vw'})
			], 
			style={
			'display':'inline-block',
			'width': '13vw',
			'margin-left': '1vw', 
			'margin-right': '1vw',
			'margin-top': '0vh',
			'text-align': 'center',
			'vertical-align': 'top'
		}),

		html.Div(
			children=[
			html.Label('Choose resolution:'),
			dcc.Dropdown(
					id='res',
					options=[{'value': x, 'label': x} 
							 for x in resolutions],
					value=resolutions[1],
					style={
						'width': '15vw'})
			],
			style={
			'display': 'inline-block',
			'width': '15vw',
			'margin-right': '0vw',
			'margin-left':'8vw',
			'padding-left': '1vw',
			'margin-top': '4vh'
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
			'margin-top': '4vh',
			'text-align': 'top'
		}),

		html.Button('Click to run', 
			id='button', 
			style={'display': 'inline-block',
					'margin-left': '4vw'}),
		html.Div(
			id='equation', 
			style={
				'textAlign': 'left',
				'font-family': "Open Sans", # "HelveticaNeue", "Helvetica Neue", Helvetica, Arial, sans-serif;', 
				'font-weight': 'normal',
				'margin-top': '0vh',
				'margin-left': '2vw',
				'font-size': '2.2rem',
				'display': 'inline-block',
				'margin-top': '6vh',
				'margin-bottom': '1vh'
			}),


		html.Div(
			id='status', 
			style={
				'textAlign': 'left',
				'font-family': "Open Sans", # "HelveticaNeue", "Helvetica Neue", Helvetica, Arial, sans-serif;', 
				'font-weight': 'normal',
				'margin-top': '0vh',
				'margin-left': '2vw',
				'font-size': '2.2rem',
				'display': 'inline-block'
			})
		],
		style={
			'display': 'inline-block',
			'width': '53vw',
			'margin-top': '2vh',
			'vertical-align': 'top'
		}
	),

	html.Img(
			id='image',
			style={'display': 'inline-block',
					'width': '80vw',
					'margin-left': '9vw',
					'margin-top': '2vh'}),

	dcc.Interval(id='trigger', interval=2000),
	# hidden div to store redis queue info
	html.Div(id='job', style={'display': 'none'}, children=dcc.Store(job))
])

# responsive callbacks ('component_id' etc are not strictly necessary but 
# are included for clarity)
@app.callback(Output(component_id='image', component_property='src'),
			[Input(component_id='job', component_property='children'),
			Input(component_id='trigger', component_property='n_intervals'),
			Input(component_id='button', component_property='n_clicks')
			])
def update_redis(job, img, n_clicks):
	if n_clicks is None:
		raise PreventUpdate
		return 

	# wait while img is generated
	if q.count > 0:
		return 
	job_current = q.fetch_job('jset_job')
	
	if not job_current:
		return

	# executes if redis job is complete
	if job_current.result:
		n_clicks = None
		img = job_current.result
		return img


@app.callback(Output(component_id='job', component_property='children'),
			[Input(component_id='creal', component_property='value'),
			 Input(component_id='cimag', component_property='value'),
			 Input(component_id='colormap', component_property='value'),
			 Input(component_id='steps', component_property='value'),
			 Input(component_id='res', component_property='value'),
			 Input(component_id='button', component_property='n_clicks')
			])
def display_juliaset(creal_value, cimag_value, colormap_value, steps_value, res_value, n_clicks):
	if n_clicks is None:
		raise PreventUpdate
	# do not update if redis queue has items waiting
	if q.count > 0:
		return ''
	# convert inputs to args and build array
	max_iterations = steps_value
	creal = float(creal_value)
	cimag = float(cimag_value)
	c = creal + cimag*1j
	cmap = colormap_value

	# send job to redis queue
	q.enqueue(julia_set, c, max_iterations, res_value, cmap,
			ttl=1, failure_ttl=0.5, result_ttl=2, job_id='jset_job')

	return ''

@app.callback(Output(component_id='button', component_property='n_clicks'),
		Input(component_id='image', component_property='src'))
def reset_clicks(img):
	if img and q.count == 0:
		return None
	else:
		return 1


@app.callback(
	Output(component_id='equation', component_property='children'),
	[Input(component_id='creal', component_property='value'),
	Input(component_id='cimag', component_property='value')])
def display_equation(creal_value, cimag_value):
	# show equation that is iterated in the complex plane
	return f'z\u00b2 + {creal_value} + {cimag_value}i '


@app.callback(
	Output(component_id='mandelimage', component_property='src'),
	[Input(component_id='creal', component_property='value'),
	Input(component_id='cimag', component_property='value')])
def display_mandelbrot(creal_value, cimag_value):
	# show the location of the complex point chosen on the Mandelbrot set
	bytestring = mandelfind(creal_value, cimag_value)
	return bytestring

@app.callback(
	Output(component_id='status', component_property='children'),
	[Input(component_id='button', component_property='n_clicks')])
def display_status(n_clicks):
	# show program status
	if n_clicks:
		return 'Running...'
	else:
		return ''

@app.callback(Output('trigger', 'interval'),
              [Input('image', 'src')])
def disable_interval(img):
    if img:
        return 60*60*1000 # one day
    else:
        return 2000


# run the app in the cloud
if __name__ == '__main__':
	# app.run_server(debug=True, port=8068)
	app.run_server(debug=True, host='0.0.0.0')





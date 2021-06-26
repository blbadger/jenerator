# mandelfind.py
# module to show the coordinates of the chosen complex value 
# relative to the mandelbrot set

# import standard libs
import io
import base64
import time

# import third party libraries
import numpy as np 
import matplotlib.pyplot as plt


def mandelfind(creal, cimag):
	plt.clf()
	mandelbrot_arr = np.load('mandelbrot_set.npy')
	point = None

	plt.axis('on')
	plt.imshow(mandelbrot_arr, cmap = 'twilight_shifted')
	xtics = [i/10 for i in range(-22, 11, 4)] # 8 ticks
	ytics = [-i/10 for i in range(-13, 14, 2)] # 13 ticks

	xlocs = [i*(1000/8) for i in range(9)]
	ylocs = [i*(800/13) for i in range(13)]
	plt.xticks(xlocs, xtics)
	plt.yticks(ylocs, ytics)

	if not creal or not cimag:
		plt.imshow(mandelbrot_arr, cmap = 'twilight_shifted')
		buf = io.BytesIO()
		plt.savefig(buf, format='png', bbox_inches='tight') # pad_inches=0
		data = base64.b64encode(buf.getbuffer()).decode("utf8") 
		return "data:image/png;base64,{}".format(data)

	# TODO: only convert to float if creal and cimag are numeric
	try:
		creal, cimag = float(creal), float(cimag)
	except:
		plt.imshow(mandelbrot_arr, cmap = 'twilight_shifted')
		buf = io.BytesIO()
		plt.savefig(buf, format='png', bbox_inches='tight') # pad_inches=0
		data = base64.b64encode(buf.getbuffer()).decode("utf8") 
		return "data:image/png;base64,{}".format(data)


	if creal > -2.2 and creal < 1:
		if cimag > -1.3 and cimag < 1.3:
			point = [int(((creal - -2.2)*1000) / 3.2), 800 - int(((cimag - -1.3)*800)/ 2.6)]

	if creal <= -2.2 or creal >= 1 or cimag <= -1.3 or cimag >= 1.3:
		plt.imshow(mandelbrot_arr, cmap = 'twilight_shifted')
		buf = io.BytesIO()
		plt.savefig(buf, format='png', bbox_inches='tight') # pad_inches=0
		data = base64.b64encode(buf.getbuffer()).decode("utf8") 
		return "data:image/png;base64,{}".format(data)
	
	# send image to bytestring
	plt.plot(point[0], point[1], 'x', color='r', markersize = 15)
	buf = io.BytesIO()
	plt.savefig(buf, format='png', bbox_inches='tight') # pad_inches=0
	data = base64.b64encode(buf.getbuffer()).decode("utf8") 
	return "data:image/png;base64,{}".format(data)

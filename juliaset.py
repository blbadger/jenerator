# juliaset.py

# import standard libs
import io
import base64

# import third-party libs
import numpy as np 
import matplotlib.pyplot as plt 

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
	y, x = np.ogrid[1.3: -1.3: h_range*1j, -1.6: 1.6: w_range*1j]
	z_array = x + y*1j

	iterations_until_divergence = max_iterations + np.zeros(z_array.shape)

	# create array of all True
	not_already_diverged = iterations_until_divergence < 10000

	# creat array of all False
	diverged_in_past = iterations_until_divergence > 10000

	for i in range(max_iterations):
		z_array = z_array**2 + c_value

		# make a boolean array for diverging indicies of z_array
		z_size_array = z_array * np.conj(z_array)
		diverging = z_size_array > 4
		diverging_now = diverging & not_already_diverged
		iterations_until_divergence[diverging_now] = i
		not_already_diverged = np.invert(diverging_now) & not_already_diverged

		# prevent overflow (values headed towards infinity) for diverging locations
		diverged_in_past = diverged_in_past | diverging_now
		z_array[diverged_in_past] = 0

	arr = iterations_until_divergence

	# save array as bytestring image for html.Img div
	return arr
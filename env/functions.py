#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  functions.py
#
#  Copyright 2021 Kleydson Stenio <kleydson.stenio@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from numpy import ndarray, array, where, min as mini, hstack, vstack, polyfit, trapz, mean, nanmean, nanstd, zeros_like, linspace
from scipy.optimize import least_squares
from PySide2.QtCore import Signal
from typing import List, Tuple
from env.equations import *


def isopeaks(wavelength: ndarray, counts: ndarray, elements: List, lower: List, upper: List, center: List, linear: bool, anorm: bool, progress: Signal) -> Tuple[ndarray, ndarray]:
	# Allocate data
	new_wavelength = array([[None] * 3] * len(elements))
	new_counts = array([array([None for X in range(len(counts))]) for Y in range(len(elements))], dtype=object)
	# Cut data for each element in iso table
	for i, e in enumerate(elements):
		cut = where((wavelength >= lower[i]) & (wavelength <= upper[i]))[0]
		x = wavelength[cut]
		for j, c in enumerate(counts):
			y = c[cut, :]
			x_, y_ = hstack((x[:2], x[-2:])), vstack((y[:2], y[-2:]))
			# Corrects data in new isolated matrix
			for k in range(y.shape[1]):
				if linear:
					# Trace a line to correct inclination
					coefficients = polyfit(x_, y_[:, k], 1)
					y[:, k] -= coefficients[1] + coefficients[0] * x
					# If asked, also normalizes by the area
					if anorm:
						y[:, k] /= trapz(coefficients[1] + coefficients[0] * x, x)
				else:
					y_min = mini(y[:, k])
					if y_min > 0:
						y[:, k] -= y_min
					elif y_min < 0:
						y[:, k] += -1 * y_min
					else:
						pass
			# Saves new count
			new_counts[i][j] = y
		# Saves new wavelength
		new_wavelength[i][:] = e, array(([lower[i], upper[i], center[i]]), dtype=object), x
		progress.emit(i)
	return new_wavelength, new_counts


def residuals(guess, x, y, shape_id, **kwargs):
	function_kwargs = {'Center': kwargs['Center'], 'Asymmetry': kwargs['Asymmetry']}
	if shape_id == 'Trapezoidal rule':
		return zeros_like(y)
	else:
		return y - kwargs[shape_id](x, *guess, **function_kwargs)


def fit_guess(x: ndarray, y: ndarray, peaks: int, center: List, shape_id: str, asymmetry=None):
	guess = []
	for i in range(peaks):
		# Height/Area, Width, Center, Asymmetry
		guess.append( max(y)/(1 + i) ) # Intensity is the highest value
		guess.append( (x[-1] - x[0]) / (2 + i) ) # Width approximation by half of interval
		if 'voigt' in shape_id.lower():
			guess[-2] = ((x[-1] - x[0]) * max(y)) / (2 + i)  # Area approximation by triangle
			guess.append( (x[-1] - x[0]) / (2 + i*0.99) ) # Width approximation by half of interval
		if 'fixed' not in shape_id.lower():
			guess.append(center[i]) # Center (user entered value)
		if ('asymmetric' in shape_id.lower()) or ('asym' in shape_id.lower() and 'center fixed' in shape_id.lower()):
			guess.append(asymmetry)  # Asymmetry (auto or user entered value)
	return guess


def fitpeaks(iso_wavelengths: ndarray, iso_counts: ndarray, parameters: List, mean1st: bool):
	# Creates exit array
	# needs: y, nx, ny
	fit_w_counts = array([[[None] * 3] * len(iso_counts[0])] * len(iso_wavelengths))
	# Goes in element level: same size as iso_wavelengths
	for i, w in enumerate(iso_wavelengths):
		# Extra relevant information:
		#   w[0] = Element
		#   w[1] = lower, upper, center
		#   w[2] = wavelengths (x data)
		#   parameters[i][0] = shape
		#   parameters[i][1] = asymmetry
		#
		# Gets a dict for shapes and fit equations
		shape, asym = parameters[i]
		scd = equations_translator(center=w[1][2], asymmetry=asym)
		# Now goes into sample level: size of each i-th iso_wavelengths
		for j, ci in enumerate(iso_counts[i]):
			# Regarding modes, we have mean 1st or area 1st, which defines how results are exported
			if mean1st:
				# If mean1st is True, take the mean of iso_counts[i][j] and pass it to perform fit
				average_spectrum = mean(ci, axis=1)
				guess = fit_guess(x=w[2], y=average_spectrum, peaks=len(w[1][2]), center=w[1][2], shape_id=shape, asymmetry=asym)
				optimized = least_squares(residuals, guess, args=(w[2], average_spectrum, shape), kwargs=scd)
				# With optimized, we can have the fit curve
				if shape != 'Trapezoidal rule':
					nx = linspace(w[1][0], w[1][1], 1000)
					ny = scd[shape](nx, *optimized.x, **scd)
				else:
					nx = w[2]
					ny = average_spectrum
				fit_w_counts[i][j][:] = average_spectrum, nx, ny
			else:
				# If mean1st is False, area1st is select, and so we will need to iterates over each individual spectrum
				pass
		return fit_w_counts

def equations_translator(center: List, asymmetry: float):
	shapes_and_curves_dict = {'Lorentzian' : lorentz,
	                          'Lorentzian [center fixed]' : lorentz_fixed_center,
	                          'Asymmetric Lorentzian' : lorentz_asymmetric,
	                          'Asym. Lorentzian [center fixed]' : lorentz_asymmetric_fixed_center,
	                          'Asym. Lorentzian [center/as. fixed]' : lorentz_asymmetric_fixed_center_asymmetry,
	                          'Gaussian' : gauss,
	                          'Gaussian [center fixed]' : gauss_fixed_center,
	                          'Voigt Profile': voigt,
	                          'Voigt Profile [center fixed]': voigt_fixed_center,
	                          'Trapezoidal rule': trapz,
	                          'Center': center,
	                          'Asymmetry': asymmetry}
	return shapes_and_curves_dict
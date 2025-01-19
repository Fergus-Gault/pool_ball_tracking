from turtle import up
import numpy as np
import cv2 as cv

# Given color with independent HSV upper and lower limits
def get_limits(color):
    

    lower_limit = [color["H_lower"], color["S_lower"], color["V_lower"]]
    upper_limit = [color["H_upper"], color["S_upper"], color["V_upper"]]

    lower_limit = np.array(lower_limit, dtype=np.uint8)
    upper_limit = np.array(upper_limit, dtype=np.uint8)

    return lower_limit, upper_limit

# Ball detection logic
import imutils
import cv2 as cv
import yaml
import numpy as np
from src.util import get_limits

class BallDetector:
    def __init__(self, config):
        """
        Init ball detector with HSV color ranges
        :param config: The configuration dictionary (e.g., from load_config)
        """
        self.config = config
        self.profile = self.config["profile"]  # Access profile
        self.radius = self.config["radius"]  # Access radius
        self.color_ranges = self._load_color_ranges(filepath="config/colors.yaml", profile=self.profile)

    def detect(self, frame):
        """
        Detect balls in a given frame.
        :param frame: Input image frame.
        :return: List of detected balls with positions, colors, radius, and contours.
        """
        hsv_frame = self._process_frame(frame)
        detected_balls = []

        # Iterate over color ranges loaded from config file
        for color_name, color_values in self.color_ranges.items():
            # Get lower and upper limits from base color
            lower, upper = get_limits(color_values)

            # Create a binary mask for the color range
            mask = cv.inRange(hsv_frame, lower, upper)

            # Clean the mask using morphological operations
            mask = self._clean_mask(mask)

            # Find contours in the mask
            contours = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            contours = imutils.grab_contours(contours)

            # Filter contours by area and process them
            for contour in contours:
                perimeter = cv.arcLength(contour, True)
                approx = cv.approxPolyDP(contour, 0.04 * perimeter, True)
                if len(approx) > 5:  # Check if the contour is approximately a circle
                    ((x, y), radius) = cv.minEnclosingCircle(contour)
                    M = cv.moments(contour)

                    if M["m00"] > 0 and radius > self.radius:  # Use the radius from config
                        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                        detected_balls.append({
                            "position": center,
                            "radius": int(radius),
                            "color": color_name,
                            "contour": contour  # Include the contour in the output
                        })
            
            cv.imshow(f"{color_name} Mask", mask)  # Show the color mask for debugging

        return detected_balls


    def _process_frame(self, frame):
        """
        Process a frame by converting to HSV
        :param frame: frame to be processed
        :return: the processed frame
        """
        hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        return hsv_frame
    
    def _clean_mask(self, mask):
        """
        Clean the mask using morphological operations.
        :param mask: The binary mask to be cleaned.
        :return: The cleaned mask.
        """
        # Apply dilation to close gaps in the mask
        kernel = np.ones((7, 7), np.uint8)
        mask = cv.dilate(mask, kernel, iterations=2)
        
        # Apply erosion to remove noise
        mask = cv.erode(mask, kernel, iterations=1)

        return mask
    
    def _load_color_ranges(self, filepath, profile="default"):
        """
        Load color ranges from config file
        :param filepath: filepath of config file
        :param profile: color range profile to be used
        :return: color ranges
        """
        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)
        if "profiles" in data and profile in data["profiles"]:
            return data["profiles"][profile]
        else:
            raise ValueError(f"Profile '{profile}' not found in {filepath}.")
        


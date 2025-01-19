import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import queue
import yaml
import os

# Load profiles from colors.yaml
def load_profiles():
    global profiles

    # Get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(script_dir, 'colors.yaml')

    # Check if colors.yaml exists
    if os.path.exists(yaml_path):
        try:
            with open(yaml_path, 'r') as yaml_file:
                data = yaml.safe_load(yaml_file)
                if "profiles" in data:
                    profiles = data["profiles"]
                    return
        except Exception as e:
            print(f"Error reading colors.yaml: {e}")

    # Fallback to default profiles if the file is missing or invalid
    print("Using default profiles.")
    profiles = {
        "default": {
            "red": {
                "H_lower": 0, "H_upper": 10,
                "S_lower": 100, "S_upper": 255,
                "V_lower": 100, "V_upper": 255
            },
            "green": {
                "H_lower": 50, "H_upper": 70,
                "S_lower": 100, "S_upper": 255,
                "V_lower": 100, "V_upper": 255
            },
        }
    }

# Load profiles at startup
load_profiles()

# Active profile and selected color
current_profile = "default"
selected_color = "red"

# Queue to store frames
frame_queue = queue.Queue(maxsize=1)

# Function to save profiles to a YAML file
def save_to_yaml():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path for colors.yaml
    yaml_path = os.path.join(script_dir, 'colors.yaml')

    # Save the profiles to the YAML file
    with open(yaml_path, 'w') as yaml_file:
        yaml.dump({"profiles": profiles}, yaml_file)
    messagebox.showinfo("Success", f"Profiles saved to {yaml_path}")


# Function to load a new profile
def load_profile(profile_name):
    global current_profile, selected_color
    current_profile = profile_name

    # Check if the profile is empty
    if not profiles[current_profile]:
        selected_color = None
        color_dropdown['values'] = []  # Clear color dropdown
        color_dropdown.set("")
        color_label.config(text="No colors in this profile.")
    else:
        # Load the first color in the profile
        selected_color = list(profiles[current_profile].keys())[0]
        color_dropdown['values'] = list(profiles[current_profile].keys())
        color_dropdown.set(selected_color)
        update_sliders(selected_color)


# Function to add a new profile
def add_new_profile():
    global profiles
    profile_name = simpledialog.askstring("New Profile", "Enter the name of the new profile:")
    if profile_name:
        if profile_name in profiles:
            messagebox.showwarning("Profile Exists", f"The profile '{profile_name}' already exists!")
        else:
            # Initialize the new profile with a default color
            profiles[profile_name] = {
                "red": {
                    "H_lower": 0, "H_upper": 10,
                    "S_lower": 100, "S_upper": 255,
                    "V_lower": 100, "V_upper": 255
                }
            }
            profile_dropdown['values'] = list(profiles.keys())  # Update profile dropdown
            profile_dropdown.set(profile_name)  # Set the new profile as active
            load_profile(profile_name)


# Function to add a new color to the current profile
def add_new_color():
    global profiles
    color_name = simpledialog.askstring("New Color", "Enter the name of the new color:")
    if color_name:
        if color_name in profiles[current_profile]:
            messagebox.showwarning("Color Exists", f"The color '{color_name}' already exists in profile '{current_profile}'!")
        else:
            profiles[current_profile][color_name] = {
                "H_lower": 0, "H_upper": 10,
                "S_lower": 100, "S_upper": 255,
                "V_lower": 100, "V_upper": 255
            }
            color_dropdown['values'] = list(profiles[current_profile].keys())
            color_dropdown.set(color_name)
            update_sliders(color_name)

# Function to update sliders based on the selected color
def update_sliders(color_name):
    global selected_color
    selected_color = color_name
    current_color = profiles[current_profile][selected_color]
    hue_lower_slider.set(current_color["H_lower"])
    hue_upper_slider.set(current_color["H_upper"])
    saturation_lower_slider.set(current_color["S_lower"])
    saturation_upper_slider.set(current_color["S_upper"])
    value_lower_slider.set(current_color["V_lower"])
    value_upper_slider.set(current_color["V_upper"])
    color_label.config(text=f"{selected_color}: H_lower={current_color['H_lower']} H_upper={current_color['H_upper']} "
                            f"S_lower={current_color['S_lower']} S_upper={current_color['S_upper']} "
                            f"V_lower={current_color['V_lower']} V_upper={current_color['V_upper']}")

# Function to update HSV values
def update_color_hsv(val, color_index, lower_or_upper):
    if selected_color:
        if lower_or_upper == "lower":
            if color_index == 0:  # Hue
                profiles[current_profile][selected_color]["H_lower"] = int(val)
            elif color_index == 1:  # Saturation
                profiles[current_profile][selected_color]["S_lower"] = int(val)
            elif color_index == 2:  # Value
                profiles[current_profile][selected_color]["V_lower"] = int(val)
        elif lower_or_upper == "upper":
            if color_index == 0:  # Hue
                profiles[current_profile][selected_color]["H_upper"] = int(val)
            elif color_index == 1:  # Saturation
                profiles[current_profile][selected_color]["S_upper"] = int(val)
            elif color_index == 2:  # Value
                profiles[current_profile][selected_color]["V_upper"] = int(val)

# Function to update the video feed
def update_video_feed():
    if not frame_queue.empty():
        frame = frame_queue.get()

        # Resize the frame for faster processing
        frame = cv2.resize(frame, (640, 480))

        # Skip processing if no color is selected
        if not selected_color or selected_color not in profiles[current_profile]:
            masked_frame = np.zeros_like(frame)  # Display an empty frame
        else:
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Get HSV values of the selected color
            current_color = profiles[current_profile][selected_color]
            lower_hsv = np.array([current_color["H_lower"], current_color["S_lower"], current_color["V_lower"]])
            upper_hsv = np.array([current_color["H_upper"], current_color["S_upper"], current_color["V_upper"]])

            # Create a mask and apply it
            mask = cv2.inRange(hsv_frame, lower_hsv, upper_hsv)
            masked_frame = cv2.bitwise_and(frame, frame, mask=mask)

        # Convert masked frame to RGB and display it
        masked_frame_rgb = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2RGB)
        masked_frame_pil = Image.fromarray(masked_frame_rgb)
        masked_frame_tk = ImageTk.PhotoImage(masked_frame_pil)

        masked_label.config(image=masked_frame_tk)
        masked_label.image = masked_frame_tk

    # Schedule the next update
    masked_label.after(30, update_video_feed)


# Video capture in a separate thread
def capture_video():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    while True:
        ret, frame = cap.read()
        if ret:
            if not frame_queue.full():
                frame_queue.put(frame)
        else:
            break
    cap.release()

# Create the GUI
root = tk.Tk()
root.title("HSV Profiles Manager with Webcam")

# Profile dropdown
profile_dropdown = ttk.Combobox(root, values=list(profiles.keys()))
profile_dropdown.set("default")
profile_dropdown.pack(pady=10)
profile_dropdown.bind("<<ComboboxSelected>>", lambda e: load_profile(profile_dropdown.get()))

# Color dropdown
color_dropdown = ttk.Combobox(root, values=list(profiles[current_profile].keys()))
color_dropdown.set("red")
color_dropdown.pack(pady=10)
color_dropdown.bind("<<ComboboxSelected>>", lambda e: update_sliders(color_dropdown.get()))

# Color info label
color_label = tk.Label(root, text="")
color_label.pack()

# Hue sliders
hue_lower_slider = tk.Scale(root, from_=0, to_=179, orient="horizontal", label="Hue Lower",
                            command=lambda val: update_color_hsv(val, 0, "lower"))
hue_lower_slider.pack()
hue_upper_slider = tk.Scale(root, from_=0, to_=179, orient="horizontal", label="Hue Upper",
                            command=lambda val: update_color_hsv(val, 0, "upper"))
hue_upper_slider.pack()

# Saturation sliders
saturation_lower_slider = tk.Scale(root, from_=0, to_=255, orient="horizontal", label="Saturation Lower",
                                    command=lambda val: update_color_hsv(val, 1, "lower"))
saturation_lower_slider.pack()
saturation_upper_slider = tk.Scale(root, from_=0, to_=255, orient="horizontal", label="Saturation Upper",
                                    command=lambda val: update_color_hsv(val, 1, "upper"))
saturation_upper_slider.pack()

# Value sliders
value_lower_slider = tk.Scale(root, from_=0, to_=255, orient="horizontal", label="Value Lower",
                               command=lambda val: update_color_hsv(val, 2, "lower"))
value_lower_slider.pack()
value_upper_slider = tk.Scale(root, from_=0, to_=255, orient="horizontal", label="Value Upper",
                               command=lambda val: update_color_hsv(val, 2, "upper"))
value_upper_slider.pack()

# Buttons
tk.Button(root, text="Add New Color", command=add_new_color).pack(pady=10)
tk.Button(root, text="Add New Profile", command=add_new_profile).pack(pady=10)
tk.Button(root, text="Save to colors.yaml", command=save_to_yaml).pack(pady=10)

# Video display
masked_label = tk.Label(root)
masked_label.pack(pady=10)

# Start video thread and GUI loop
update_video_feed()
threading.Thread(target=capture_video, daemon=True).start()
root.mainloop()

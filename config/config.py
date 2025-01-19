import os
import yaml

def load_config(profile):
    # Get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(script_dir, 'config.yaml')

    # Check if config.yaml exists
    if os.path.exists(yaml_path):
        try:
            with open(yaml_path, 'r') as yaml_file:
                data = yaml.safe_load(yaml_file)
                if "profiles" in data and profile in data["profiles"]:
                    return data["profiles"][profile]
                elif "profiles" in data and "default" in data["profiles"]:
                    return data["profiles"]["default"]
                else:
                    print("No profile found, returning default profile.")
                    return data.get("profiles", {}).get("default", None)
        except Exception as e:
            print(f"Error reading config.yaml: {e}")
    else:
        print("config.yaml not found, creating a new one.")
        # Create default profiles if the config file doesn't exist
        profiles = {
            "profiles": {
                "default": {
                    "detector": {
                        "profile": "default",
                        "radius": 50,
                    },
                    "tracking": {
                        "buffer_size": 64,
                        "max_distance": 50,
                        "min_area": 1000,
                        "circle_outline_color": [0, 255, 255],  # Use list instead of tuple
                        "circle_thickness": 2,
                        "radius_line_color": [255, 0, 0],
                        "radius_line_thickness": 2,
                        "center_point_color": [0, 0, 255],
                        "center_point_radius": 5,
                        "font_color": [255, 255, 255],
                        "font_scale": 0.5,
                        "font_thickness": 2,
                        "tracking_line_color": [0, 0, 255],  # List instead of alias
                    },
                }
            }
        }
        # Write the default profile to the YAML file
        try:
            with open(yaml_path, 'w') as yaml_file:
                yaml.dump(profiles, yaml_file)
            print("config.yaml created with default profile.")
            return profiles["profiles"]["default"]  # Return the default profile
        except Exception as e:
            print(f"Error writing config.yaml: {e}")
            return None

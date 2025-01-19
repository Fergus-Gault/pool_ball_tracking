# Main script

import cv2 as cv
import argparse
from src.detection import BallDetector
from src.tracking import MultiBallTracker
from config.config import load_config

def main():
    profile = parse_args()
    config = load_config(profile)

    # Ensure the profile was correctly loaded
    if config is None:
        print("Error: Profile configuration could not be loaded.")
        return

    # Extract the configuration for detector and tracker from the loaded profile
    detector_config = config.get("detector", {})
    tracker_config = config.get("tracking", {})

    # Initialize the BallDetector and MultiBallTracker with the extracted configuration
    detector = BallDetector(detector_config)
    tracker = MultiBallTracker(tracker_config)

    # Open the camera
    camera = cv.VideoCapture(0)

    if not camera.isOpened():
        print("Cannot open camera")
        exit()

    while True:
        # Capture frame by frame
        ret, frame = camera.read()

        if not ret:
            print("Cannot receive frame. Exiting...")
            break

        # Detect balls in the frame
        detected_balls = detector.detect(frame)

        # Update and draw the tracking on the frame
        tracker.update_tracks(detected_balls)
        tracker.draw_tracks(frame)

        # Show the frame with tracking results
        cv.imshow("Pool ball tracker", frame)

        # Exit the loop if 'q' is pressed
        if cv.waitKey(1) == ord('q'):
            break

    # Release the camera and close the window
    camera.release()
    cv.destroyAllWindows()

def parse_args():
    parser = argparse.ArgumentParser(description="Select a config profile to use.")
    parser.add_argument(
        "--profile",
        type=str,
        default='default',
        help="The name of the profile to use (default: `default`)"
    )

    args = parser.parse_args()

    return args.profile

if __name__ == "__main__":
    main()

import numpy as np
from collections import deque
import cv2 as cv

class MultiBallTracker:
    def __init__(self, buffer_size=64, max_distance=50, min_area=1000):
        """
        Initialize multi-ball tracker.
        :param buffer_size: Maximum trajectory points to store for each ball.
        :param max_distance: Maximum distance to associate a detection with an existing ball.
        :param min_area: Minimum contour area to consider it as a valid detection.
        """
        self.buffer_size = buffer_size
        self.max_distance = max_distance
        self.min_area = min_area  # Ignore contours smaller than this area
        self.ball_tracks = {}  # {ball_id: {"positions": deque, "radius": radius, "velocity": velocity}}
        self.next_ball_id = 0

    def update_tracks(self, detected_balls):
        """
        Update ball tracks with the latest detections.
        :param detected_balls: List of detected balls from BallDetector.
        """
        new_tracks = {}

        for ball in detected_balls:
            position = np.array(ball["position"])
            radius = ball["radius"]
            matched_id = None

            # Skip small detections that are likely noise
            if cv.contourArea(ball["contour"]) < self.min_area:
                continue

            # Try to match the ball with an existing track
            for ball_id, track in self.ball_tracks.items():
                # Prediction: the predicted position based on the last known velocity
                if len(track["positions"]) > 1:
                    velocity = (track["positions"][-1] - track["positions"][-2])
                    predicted_position = track["positions"][-1] + velocity
                    predicted_distance = np.linalg.norm(position - predicted_position)

                    # Match if the predicted distance is within the max_distance threshold
                    if predicted_distance < self.max_distance:
                        matched_id = ball_id
                        break
                else:
                    # First frame for this ball, use the last position
                    if np.linalg.norm(position - np.array(track["positions"][-1])) < self.max_distance:
                        matched_id = ball_id
                        break

            if matched_id is not None:
                # Update the existing track
                new_tracks[matched_id] = self.ball_tracks[matched_id]
                new_tracks[matched_id]["positions"].append(position)
                new_tracks[matched_id]["radius"] = radius
            else:
                # Start a new track
                new_tracks[self.next_ball_id] = {
                    "positions": deque([position], maxlen=self.buffer_size),
                    "radius": radius
                }
                self.next_ball_id += 1

        # Update the tracker state
        self.ball_tracks = new_tracks

    def draw_tracks(self, frame):
        """
        Draw ball tracks and current positions on the frame.
        :param frame: Frame to draw on.
        """
        for ball_id, track_data in self.ball_tracks.items():
            positions = track_data["positions"]
            radius = track_data["radius"]
            center = tuple(positions[-1].astype(int))

            # Draw the circle outline
            cv.circle(frame, center, int(radius), (0, 255, 255), 2)

            # Draw the radius as a line
            edge_point = (center[0] + int(radius), center[1])
            cv.line(frame, center, edge_point, (255, 0, 0), 2)

            # Draw the center point
            cv.circle(frame, center, 5, (0, 0, 255), -1)

            # Label the ball ID
            cv.putText(frame, f"ID: {ball_id}", (center[0] - 20, center[1] - 20),
                       cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # Draw the trajectory
            for i in range(1, len(positions)):
                if positions[i - 1] is None or positions[i] is None:
                    continue

                thickness = int(np.sqrt(self.buffer_size / float(i + 1)) * 2.5)
                cv.line(frame, tuple(positions[i - 1].astype(int)), tuple(positions[i].astype(int)), (0, 0, 255), thickness)


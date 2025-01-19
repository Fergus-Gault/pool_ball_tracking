# Main script

import cv2 as cv
from detection import BallDetector
from tracking import MultiBallTracker

def main():

    detector = BallDetector(profile = "default")
    tracker = MultiBallTracker()

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


        detected_balls = detector.detect(frame)

        tracker.update_tracks(detected_balls)

        tracker.draw_tracks(frame)


        cv.imshow("Pool ball tracker", frame)

        if cv.waitKey(1) == ord('q'):
            break

    camera.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
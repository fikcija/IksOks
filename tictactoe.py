import cv2
import numpy as np
import os
import sys
from tictactoe_detection import *

def main(video_number):
    # Initialize the variables
    displayed_horizontal_lines = []
    displayed_vertical_lines = []

    game_state = [[-1, -1, -1], 
                  [-1, -1, -1], 
                  [-1, -1, -1]]

    cell_positions = []
    hand_in_frame = False

    # Import video
    video_path = os.path.join('videos', f'xo{video_number}c.avi')
    cap = cv2.VideoCapture(video_path)

    # Process the video and detect tic tac toe moves
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        displayed_horizontal_lines, displayed_vertical_lines, cell_positions = detect_grid_lines(frame, displayed_horizontal_lines, 
                                                                                                 displayed_vertical_lines, hand_in_frame, 
                                                                                                 cell_positions)
        detected_lines_canvas = np.zeros_like(frame)
        hand_in_frame = detect_hand(frame)

        if not hand_in_frame and len(cell_positions) > 0:
            game_state = detect_signs(frame, game_state, cell_positions)
            
        draw_detected_lines(detected_lines_canvas, displayed_horizontal_lines + displayed_vertical_lines)
        draw_shapes(detected_lines_canvas, game_state, cell_positions)

        game_result, winning_line = gameScore(game_state)
        if game_result is not None:
            writeScore(game_result, winning_line, cell_positions, detected_lines_canvas)

        # Display the stacked frames
        stacked_frames = np.hstack((frame, detected_lines_canvas))
        cv2.imshow('Tic tac toe', stacked_frames)

        # Check for the 'q' key press to exit the loop
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    # Release the video capture object and close all windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    video_number = input("Enter the video number that you want to play (1 or 2): ")

    if video_number not in {'1', '2'}:
        print("Invalid video number. Please specify 1 or 2")
        sys.exit(1)

    main(video_number)
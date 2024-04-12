import cv2
import numpy as np

horizontal_lines = []
vertical_lines = []

intersection_points = []
cell_height = 0
cell_width = 0

previous_frame = None


def detect_grid_lines(img, bu_horizontal_lines, bu_vertical_lines, hand_in_frame, cell_positions):
    global horizontal_lines, vertical_lines

    bottom_ignore_pixels = 10
    right_ignore_pixels = 10
    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=70, minLineLength=115, maxLineGap=45)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if min(y1, y2) < height - bottom_ignore_pixels and max(x1, x2) < width - right_ignore_pixels:
                if is_nearly_horizontal(x1, y1, x2, y2):
                    add_line = True
                    for h_line in horizontal_lines:
                        x1_h, y1_h, x2_h, y2_h = h_line[0]
                        if abs(y1 - y1_h) < 20 or abs(y2 - y2_h) < 20:
                            add_line = False
                            break
                    if add_line:
                        horizontal_lines.append(line)
                elif is_nearly_vertical(x1, y1, x2, y2):
                    add_line = True
                    for v_line in vertical_lines:
                        x1_v, y1_v, x2_v, y2_v = v_line[0]
                        if abs(x1 - x1_v) < 20 or abs(x2 - x2_v) < 20:
                            add_line = False
                            break
                    if add_line:
                        vertical_lines.append(line)
    
    if len(horizontal_lines) >= 2 and len(vertical_lines) >= 2:
            cell_positions = find_cell_positions(cell_positions)
            bu_horizontal_lines = horizontal_lines.copy()
            bu_vertical_lines = vertical_lines.copy()

    if hand_in_frame:
        hand_in_frame = False
        horizontal_lines.clear()
        vertical_lines.clear()

    return bu_horizontal_lines, bu_vertical_lines, cell_positions


def find_cell_positions(cell_positions):
    global intersection_points

    intersection_points = []
    for h_line in horizontal_lines:
        for v_line in vertical_lines:
            px, py = find_intersection(h_line, v_line)
            intersection_points.append((px, py))
    
    if len(intersection_points) > 0:
        cell_positions = calculate_surrounding_cell_positions(cell_positions)

    return cell_positions


def calculate_surrounding_cell_positions(cell_positions):
    global intersection_points, cell_height, cell_width
    
    cell_positions = []

    # Extract points of the middle cell
    x1, y1 = intersection_points[0]
    x2, y2 = intersection_points[1]
    x3, y3 = intersection_points[2]
    x4, y4 = intersection_points[3]

    # Calculate width and height of the middle cell
    cell_width = int(abs(x2 - x1))
    cell_height = int(abs(y3 - y1))

    # Calculate center of the middle cell
    middle_cell_center_x = (x1 + x2 + x3 + x4) / 4
    middle_cell_center_y = (y1 + y2 + y3 + y4) / 4

    # Define offsets for surrounding cells relative to the middle cell
    offsets = [(-1, -1), (-1, 0), (-1, 1),
               ( 0, -1),          ( 0, 1),
               ( 1, -1), ( 1, 0), ( 1, 1)]

    cell_positions.append((int(middle_cell_center_x), int(middle_cell_center_y)))

    # Calculate position of each surrounding cell based on the middle cell
    for dx, dy in offsets:
        cell_x = middle_cell_center_x + dx * cell_width
        cell_y = middle_cell_center_y + dy * cell_height
        cell_positions.append((int(cell_x), int(cell_y)))

    cell_positions = sorted(cell_positions, key=lambda pos: (pos[1], pos[0]))

    return cell_positions
    

def find_intersection(line1, line2):
    x1, y1, x2, y2 = line1[0]
    x3, y3, x4, y4 = line2[0]
    Px = ((x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4 - y3*x4))/  \
        ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))
    Py = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4 - y3*x4))/  \
        ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))

    return Px, Py


def is_nearly_horizontal(x1, y1, x2, y2, threshold=5):
    angle = np.arctan2(abs(y2 - y1), abs(x2 - x1)) * 180 / np.pi
    return abs(angle - 0) < threshold or abs(angle - 180) < threshold


def is_nearly_vertical(x1, y1, x2, y2, threshold=5):
    angle = np.arctan2(abs(y2 - y1), abs(x2 - x1)) * 180 / np.pi
    return abs(angle - 90) < threshold


def detect_hand(frame):
    global previous_frame

    # Define region of interest (ROI) in the top center part of the frame
    height, width = frame.shape[:2]
    roi_top = 5
    roi_bottom = height // 5
    roi_left = width // 5
    roi_right = width - roi_left
    roi = frame[roi_top:roi_bottom, roi_left:roi_right]

    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    if previous_frame is None:
        previous_frame = gray_roi
        return
    else:
        frame_diff = cv2.absdiff(gray_roi, previous_frame)
        _, motion_mask = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)
        if cv2.countNonZero(motion_mask) > 100:
            return True
        else:
            return False


def draw_detected_lines(frames, lines):
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(frames, (x1, y1), (x2, y2), (255, 255, 255), 2)


def detect_signs(frame, game_state, cell_positions):
    global cell_height, cell_width
    
    for i, cell_center in enumerate(cell_positions):
        if game_state[i // 3][i % 3] == -1:
            x = int(cell_center[0] - cell_width / 2)
            y = int(cell_center[1] - cell_height / 2)

            x_roi = x + 2
            y_roi = y + 2
            width_roi = cell_width - 4
            height_roi = cell_height - 4
            
            # Crop the cell area from the frame, excluding the border area
            cell_image = frame[y_roi:y_roi+height_roi, x_roi:x_roi+width_roi]

            # Convert the cell image to grayscale
            cell_gray = cv2.cvtColor(cell_image, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding to isolate signs
            _, thresh = cv2.threshold(cell_gray, 135, 255, cv2.THRESH_BINARY)
            
            # Find contours in the thresholded image
            contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            if contours and len(contours) > 1:
                # Sort contours by area in descending order
                contours = sorted(contours, key=cv2.contourArea, reverse=True)
                shape = contours[1]
                
                # Calculate the area of the contour
                contour_area = cv2.contourArea(shape)
                
                # Determine if the contour represents X or O based on area
                if contour_area > 100 and contour_area < 190:
                    game_state[i // 3][i % 3] = 1  # X (player 1)
                elif contour_area > 200 and contour_area < 400:
                    game_state[i // 3][i % 3] = 0  # O (player 2)
                else:
                    game_state[i // 3][i % 3] = -1  # Empty
                    
                # Optionally, draw the detected contour on the original frame
                # cell_cont = cv2.drawContours(cell_image, [shape], -1, (0, 0, 255), 2)
                # cv2.imshow(f"Cell {i + 1} with contours", cell_cont)
                # cv2.waitKey(0)
                # print(contour_area)
                # cv2.destroyWindow(f"Cell {i + 1} with contours")
            else:
                game_state[i // 3][i % 3] = -1  # Empty
        
    return game_state


def draw_circle(frame, center):
    cv2.circle(frame, center, 15, (0, 0, 255), 2)


def draw_x(frame, center):
    x, y = center
    cv2.line(frame, (x - 15, y - 15), (x + 15, y + 15), (255, 0, 0), 2)
    cv2.line(frame, (x - 15, y + 15), (x + 15, y - 15), (255, 0, 0), 2)


def draw_shapes(frame, game_state, cell_positions):
    for i, row in enumerate(game_state):
        for j, value in enumerate(row):
            if value != -1:
                center = cell_positions[i * 3 + j]
                if value == 0:
                    draw_circle(frame, center)
                elif value == 1:
                    draw_x(frame, center)


def draw_grid_lines_on_img(img, lines):
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

def draw_cells(image, cell_positions):
    global cell_height, cell_width

    for cell_center in cell_positions:
        x = int(cell_center[0] - cell_width / 2)
        y = int(cell_center[1] - cell_height / 2)
        top_left = (x, y)
        bottom_right = (x + cell_width, y + cell_height)
        cv2.rectangle(image, top_left, bottom_right, (255, 0, 0), 2)

def gameScore(game_state):
    # Check rows
    for row_index, row in enumerate(game_state):
        if row.count(1) == 3:
            return 1, [(row_index, col) for col in range(3)]  # Player X wins
        elif row.count(0) == 3:
            return 0, [(row_index, col) for col in range(3)]  # Player O wins

    # Check columns
    for col in range(3):
        if game_state[0][col] == game_state[1][col] == game_state[2][col] == 1:
            return 1, [(row, col) for row in range(3)]
        elif game_state[0][col] == game_state[1][col] == game_state[2][col] == 0:
            return 0, [(row, col) for row in range(3)]

    # Check diagonals
    if game_state[0][0] == game_state[1][1] == game_state[2][2] == 1:
        return 1, [(i, i) for i in range(3)]
    elif game_state[0][0] == game_state[1][1] == game_state[2][2] == 0:
        return 0, [(i, i) for i in range(3)]
    elif game_state[0][2] == game_state[1][1] == game_state[2][0] == 1:
        return 1, [(i, 2 - i) for i in range(3)]
    elif game_state[0][2] == game_state[1][1] == game_state[2][0] == 0:
        return 0, [(i, 2 - i) for i in range(3)]

    # Check for draw
    for row in game_state:
        if -1 in row:
            return None, []  # Game still in progress
    return -1, []  # Draw


def writeScore(score, winning_line, cell_positions, frame):
    if score == -1:
        cv2.putText(frame, "It's a draw!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    elif score == 0:
        cv2.putText(frame, "O wins!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    elif score == 1:
        cv2.putText(frame, "X wins!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Draw winning line
    if winning_line and score in {0, 1}:
        position1 = winning_line[0]
        position2 = winning_line[-1]

        x1, y1 = cell_positions[position1[0] * 3 + position1[1]]
        x2, y2 = cell_positions[position2[0] * 3 + position2[1]]

        cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        
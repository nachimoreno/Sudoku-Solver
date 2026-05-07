import cv2
import numpy as np
import os
import glob

def extract_board(image_path: str, output_size: int = 900, debug_dir: str = None) -> np.ndarray:
    """
    Extracts the Sudoku board from a screenshot.
    
    Steps:
    1. Convert screenshot to grayscale.
    2. Detect edges or threshold dark grid lines.
    3. Find large rectangular contours.
    4. Crop that region.
    5. Resize to standard size.
    """
    if debug_dir and not os.path.exists(debug_dir):
        os.makedirs(debug_dir, exist_ok=True)

    def save_debug(filename, img):
        if debug_dir:
            cv2.imwrite(os.path.join(debug_dir, filename), img)

    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not load image from {image_path}")

    # 1. Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    save_debug("01_grayscale.png", gray)

    # 2. Detect edges / threshold dark lines
    # The outline for the board is the darkest part of the screenshot.
    # We use adaptive thresholding to robustly find the dark lines against a lighter background.
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    save_debug("02_blurred.png", blur)

    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    save_debug("03_thresholded.png", thresh)

    # 3. Find large rectangular contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort contours by area in descending order
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    board_contour = None
    for c in contours:
        area = cv2.contourArea(c)
        # Skip unreasonably small contours
        if area < 1000:
            continue
            
        # Approximate the contour to a polygon
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.015 * peri, True)

        # The board is a square, which means it should be approximated to a 4-sided polygon
        if len(approx) == 4:
            board_contour = approx
            break

    if board_contour is None:
        raise ValueError(f"Could not find the Sudoku board contour in the image: {image_path}")

    # Draw the found contour for debugging
    if debug_dir:
        contour_img = image.copy()
        cv2.drawContours(contour_img, [board_contour], -1, (0, 255, 0), 3)
        save_debug("04_contour_found.png", contour_img)

    # 4. Crop that region (using perspective transform)
    # Reshape to a list of 4 coordinates: [top-left, top-right, bottom-right, bottom-left]
    pts = board_contour.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # Top-left has the smallest sum
    rect[2] = pts[np.argmax(s)]  # Bottom-right has the largest sum

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # Top-right has the smallest difference
    rect[3] = pts[np.argmax(diff)]  # Bottom-left has the largest difference

    # 5. Resize to standard size
    # The contour typically includes the thick outer black border. 
    # To ensure it is cut out completely, we warp to a slightly larger square 
    # and then crop the margin off so we get only the inside of the board.
    margin = int(output_size * 0.008)  # 1.5% margin cuts out the outer border
    padded_size = output_size + 2 * margin
    
    dst = np.array([
        [0, 0],
        [padded_size - 1, 0],
        [padded_size - 1, padded_size - 1],
        [0, padded_size - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    padded_warped = cv2.warpPerspective(image, M, (padded_size, padded_size))
    
    # Crop out the margin to get the final exact output_size
    warped = padded_warped[margin:-margin, margin:-margin]
    
    save_debug("05_final_cropped.png", warped)

    return warped

def split_board_into_cells(board_image: np.ndarray, debug_dir: str = None) -> list:
    """
    Splits the extracted Sudoku board into 81 individual cell images.
    Returns a list of 81 images (each cell).
    """
    if debug_dir and not os.path.exists(debug_dir):
        os.makedirs(debug_dir, exist_ok=True)

    cells = []
    height, width = board_image.shape[:2]

    # Parameters for grid line thickness (in pixels for a ~900x900 image)
    # These can be tuned if the lines are slightly thicker/thinner
    thick_line_width = 7
    thin_line_width = 3
    
    # Calculate the exact floating point size of a single cell
    # Total width = 9 * cell_width + 2 * thick_line_width + 6 * thin_line_width
    cell_width = (width - 2 * thick_line_width - 6 * thin_line_width) / 9.0
    cell_height = (height - 2 * thick_line_width - 6 * thin_line_width) / 9.0

    for row in range(9):
        # Calculate number of lines before this row
        thick_lines_y = row // 3
        thin_lines_y = row - thick_lines_y

        y_start = int(row * cell_height + thick_lines_y * thick_line_width + thin_lines_y * thin_line_width)
        y_end = int(y_start + cell_height)

        # Apply an extra crop on the top for specific rows that have residual outlines
        if row in [4, 6, 8]:
            y_start += 2

        for col in range(9):
            # Calculate number of lines before this column
            thick_lines_x = col // 3
            thin_lines_x = col - thick_lines_x

            x_start = int(col * cell_width + thick_lines_x * thick_line_width + thin_lines_x * thin_line_width)
            x_end = int(x_start + cell_width)

            cell = board_image[y_start:y_end, x_start:x_end]
            cells.append(cell)

            if debug_dir:
                # Save each cell with a format like cell_rX_cY.png
                filename = f"cell_r{row}_c{col}.png"
                cv2.imwrite(os.path.join(debug_dir, filename), cell)

    return cells

def threshold_cells(cells: list, debug_dir: str = None) -> list:
    """
    Thresholds the list of cell images to pure black and white.
    Returns a list of thresholded cell images.
    """
    if debug_dir and not os.path.exists(debug_dir):
        os.makedirs(debug_dir, exist_ok=True)

    thresholded_cells = []
    
    for idx, cell in enumerate(cells):
        gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
        
        # Since this is a screenshot, the background is perfectly light and text is dark.
        # A global fixed threshold is very safe and avoids the noise Otsu's or adaptive 
        # thresholding would introduce on empty cells.
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        thresholded_cells.append(thresh)

        if debug_dir:
            row = idx // 9
            col = idx % 9
            filename = f"cell_r{row}_c{col}.png"
            cv2.imwrite(os.path.join(debug_dir, filename), thresh)

    return thresholded_cells

def classify_and_save_cells(thresh_cells: list, base_debug_dir: str = None) -> dict:
    """
    Classifies cells into "Values", "Candidates", or "Empty" based on contour bounding box height.
    Saves them into corresponding subdirectories if base_debug_dir is provided.
    """
    val_dir = cand_dir = empty_dir = None
    if base_debug_dir:
        val_dir = os.path.join(base_debug_dir, "Values")
        cand_dir = os.path.join(base_debug_dir, "Candidates")
        empty_dir = os.path.join(base_debug_dir, "Empty")
        os.makedirs(val_dir, exist_ok=True)
        os.makedirs(cand_dir, exist_ok=True)
        os.makedirs(empty_dir, exist_ok=True)

    classified = {"Values": [], "Candidates": [], "Empty": []}

    for idx, cell in enumerate(thresh_cells):
        # Invert the image so text is white and background is black for findContours
        inverted = cv2.bitwise_not(cell)

        # Find contours
        contours, _ = cv2.findContours(inverted, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        max_h = 0
        cell_h = cell.shape[0]

        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if h > max_h:
                max_h = h

        # Classify based on max bounding box height
        # Values are usually very large, > 35% of cell height
        # Candidates are small, ~10-25% of cell height
        if max_h > cell_h * 0.35:
            category = "Values"
        elif max_h > cell_h * 0.05: # Threshold above microscopic noise
            category = "Candidates"
        else:
            category = "Empty"

        classified[category].append((idx, cell))

        if base_debug_dir:
            row = idx // 9
            col = idx % 9
            filename = f"cell_r{row}_c{col}.png"
            if category == "Values":
                cv2.imwrite(os.path.join(val_dir, filename), cell)
            elif category == "Candidates":
                cv2.imwrite(os.path.join(cand_dir, filename), cell)
            else:
                cv2.imwrite(os.path.join(empty_dir, filename), cell)

    return classified

def parse_candidates(cand_cells: list, debug_dir: str = None) -> dict:
    """
    Parses candidate cells to determine which candidates (1-9) are present.
    cand_cells: list of tuples (idx, cell_image)
    Returns a dictionary mapping idx -> list of present candidates [1..9].
    """
    if debug_dir and not os.path.exists(debug_dir):
        os.makedirs(debug_dir, exist_ok=True)

    parsed_candidates = {}

    for idx, cell in cand_cells:
        # Invert to make digits white (255) and background black (0)
        inverted = cv2.bitwise_not(cell)
        h, w = inverted.shape[:2]
        
        sub_h = h / 3.0
        sub_w = w / 3.0
        
        present_candidates = []
        
        # Create a BGR version for debug drawing
        if debug_dir:
            debug_img = cv2.cvtColor(cell, cv2.COLOR_GRAY2BGR)
        
        candidate_num = 1
        for r in range(3):
            for c in range(3):
                # We can add a slight inner padding to the subcells to avoid capturing edges
                # of neighboring digits if they overflow slightly.
                pad_y = int(sub_h * 0.15)
                pad_x = int(sub_w * 0.15)
                
                y_start = int(r * sub_h) + pad_y
                y_end = int((r + 1) * sub_h) - pad_y
                x_start = int(c * sub_w) + pad_x
                x_end = int((c + 1) * sub_w) - pad_x
                
                subcell = inverted[y_start:y_end, x_start:x_end]
                
                # Count non-zero (white) pixels
                ink_pixels = cv2.countNonZero(subcell)
                
                # If ink pixels exceed a small threshold, candidate is present
                # NYT sudoku candidates are quite small but they have more than 10-15 pixels.
                is_present = ink_pixels > 15
                
                if is_present:
                    present_candidates.append(candidate_num)
                    
                if debug_dir:
                    color = (0, 255, 0) if is_present else (0, 0, 255) # Green if present, Red if not
                    # Draw rectangle on debug_img
                    cv2.rectangle(debug_img, (x_start, y_start), (x_end, y_end), color, 1)
                    
                    if is_present:
                        cv2.putText(debug_img, str(candidate_num), (x_start + 2, y_start + 12), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
                
                candidate_num += 1
                
        parsed_candidates[idx] = present_candidates
        
        if debug_dir:
            row = idx // 9
            col = idx % 9
            filename = f"cell_r{row}_c{col}.png"
            cv2.imwrite(os.path.join(debug_dir, filename), debug_img)
            
    return parsed_candidates

def load_reference_digits():
    """
    Loads reference digit images 1-9 from src/reference/digits.
    Returns a dictionary mapping digit -> thresholded reference image.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ref_dir = os.path.join(base_dir, "src", "reference", "digits")
    
    references = {}
    if not os.path.exists(ref_dir):
        print(f"Warning: Reference directory {ref_dir} not found.")
        return references
        
    for i in range(1, 10):
        path = os.path.join(ref_dir, f"{i}.png")
        if os.path.exists(path):
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                # Threshold to black and white
                _, thresh = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)
                # We need to invert it for template matching (white text on black background)
                inv_thresh = cv2.bitwise_not(thresh)
                references[i] = inv_thresh
            else:
                print(f"Warning: Could not read {path}")
        else:
            print(f"Warning: Reference image {path} not found.")
            
    return references

def parse_values(val_cells: list, references: dict, debug_dir: str = None) -> dict:
    """
    Parses value cells using template matching against reference digits.
    val_cells: list of tuples (idx, cell_image)
    Returns a dictionary mapping idx -> predicted digit.
    """
    if debug_dir and not os.path.exists(debug_dir):
        os.makedirs(debug_dir, exist_ok=True)

    parsed_values = {}

    for idx, cell in val_cells:
        # Invert to make digits white (255) and background black (0)
        inverted = cv2.bitwise_not(cell)
        
        best_match_digit = None
        best_match_score = -1.0
        
        for digit, ref_img in references.items():
            # If the reference image is larger than the cell, resize it.
            if ref_img.shape[0] > inverted.shape[0] or ref_img.shape[1] > inverted.shape[1]:
                h, w = inverted.shape[:2]
                ref_img = cv2.resize(ref_img, (w - 10, h - 10))
            
            result = cv2.matchTemplate(inverted, ref_img, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            if max_val > best_match_score:
                best_match_score = max_val
                best_match_digit = digit
                
        parsed_values[idx] = best_match_digit
        
        if debug_dir:
            debug_img = cv2.cvtColor(cell, cv2.COLOR_GRAY2BGR)
            if best_match_digit is not None:
                text = f"{best_match_digit} ({best_match_score:.2f})"
                cv2.putText(debug_img, text, (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            row = idx // 9
            col = idx % 9
            filename = f"cell_r{row}_c{col}.png"
            cv2.imwrite(os.path.join(debug_dir, filename), debug_img)
            
    return parsed_values

def ingest_screenshot(image_path: str) -> list:
    """
    Runs the entire pipeline on a single image and returns the parsed board data.
    Returns a 9x9 list of dicts: {"value": int, "candidates": list[int]}
    """
    board_data = [[{"value": 0, "candidates": []} for _ in range(9)] for _ in range(9)]
    
    board = extract_board(image_path)
    cells = split_board_into_cells(board)
    thresh_cells = threshold_cells(cells)
    classified_cells = classify_and_save_cells(thresh_cells)
    
    parsed_cands = parse_candidates(classified_cells["Candidates"])
    
    references = load_reference_digits()
    parsed_vals = {}
    if references:
        parsed_vals = parse_values(classified_cells["Values"], references)
        
    for idx in range(81):
        row = idx // 9
        col = idx % 9
        
        if idx in parsed_vals:
            # We found a value
            board_data[row][col]["value"] = parsed_vals[idx]
        elif idx in parsed_cands:
            # We found candidates
            board_data[row][col]["candidates"] = parsed_cands[idx]
            
    return board_data

def process_all_inputs():
    # Use absolute paths based on the script's location or assume running from project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    inputs_dir = os.path.join(base_dir, "inputs")
    outputs_base_dir = os.path.join(base_dir, "outputs", "cv")
    
    if not os.path.exists(inputs_dir):
        print(f"Directory {inputs_dir} does not exist.")
        return

    # Find all images in inputs folder
    valid_extensions = ("*.png", "*.jpg", "*.jpeg", "*.webp")
    image_paths = []
    for ext in valid_extensions:
        image_paths.extend(glob.glob(os.path.join(inputs_dir, ext)))
        
    if not image_paths:
        print(f"No images found in {inputs_dir}")
        return

    references = load_reference_digits()

    for img_path in image_paths:
        # Get filename without extension
        filename = os.path.basename(img_path)
        name_no_ext = os.path.splitext(filename)[0]
        
        # Directories for the stepping
        image_out_dir = os.path.join(outputs_base_dir, name_no_ext)
        crop_dir = os.path.join(image_out_dir, "01_Cropping")
        split_dir = os.path.join(image_out_dir, "02_Splitting")
        thresh_dir = os.path.join(image_out_dir, "03_Thresholded")
        sep_dir = os.path.join(image_out_dir, "04_Separated")
        parse_cand_dir = os.path.join(image_out_dir, "05_Parse_Candidates")
        parse_val_dir = os.path.join(image_out_dir, "06_Parse_Values")
        
        print(f"Processing {filename}")
        print(f"  -> Cropping steps in {crop_dir}")
        print(f"  -> Splitting steps in {split_dir}")
        print(f"  -> Threshold steps in {thresh_dir}")
        print(f"  -> Separation steps in {sep_dir}")
        print(f"  -> Candidate parsing steps in {parse_cand_dir}")
        print(f"  -> Value parsing steps in {parse_val_dir}")
        
        try:
            board = extract_board(img_path, debug_dir=crop_dir)
            cells = split_board_into_cells(board, debug_dir=split_dir)
            thresh_cells = threshold_cells(cells, debug_dir=thresh_dir)
            classified_cells = classify_and_save_cells(thresh_cells, base_debug_dir=sep_dir)
            
            # Parse candidates
            parsed_cands = parse_candidates(classified_cells["Candidates"], debug_dir=parse_cand_dir)
            
            # Parse values
            if references:
                parsed_vals = parse_values(classified_cells["Values"], references, debug_dir=parse_val_dir)
            else:
                print("Skipping value parsing because reference digits were not loaded.")
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    process_all_inputs()

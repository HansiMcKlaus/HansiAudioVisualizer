import numpy as np
import cv2
import matplotlib.colors as mcolors

def render_frame(data, settings):
    if (settings["visualization"] == "volume"):
        return render_volume(data, settings)
    if (settings["visualization"] == "spectrum"):
        return render_spectrum(data, settings)

def render_volume(data, settings):
    color = hex_to_bgr(settings["color"])
    bg_color = hex_to_bgr(settings["backgroundColor"])
    img = initialImage(settings, bg_color)
    height, width, channels = img.shape

    smallest_side = min(height, width)
    min_radius, max_radius = settings["innerOuterRadius"]
    radius = int(smallest_side/2 * (min_radius + (data * (max_radius - min_radius))))

    midpoint = (width//2, height//2)
    cv2.circle(img, midpoint, radius, color, -1)
    if (min_radius > 0):
        cv2.circle(img, midpoint, int(smallest_side/2 * min_radius), bg_color, -1)
    if (settings["antiAliasing"]):
        img = cv2.resize(img, (settings["width"], settings["height"]))
    return img

def render_spectrum(data, settings):
    color = hex_to_bgr(settings["color"])
    bg_color = hex_to_bgr(settings["backgroundColor"])
    img = initialImage(settings, bg_color)
    height, width, channels = img.shape

    num_bins = len(data)
    if settings["style"] == "bar":
        for i, value in enumerate(data):
            if (settings["styleVariant"] == "simple"):
                bar_height = int(height * value)
                bin_width = width / num_bins
                offset = bin_width * (1 - settings["binWidth"]) / 2
                x1 = int(bin_width * i + offset)
                x2 = int(bin_width * (i + 1) - offset)
                y1 = height - bar_height
                y2 = height
                cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)

            elif (settings["styleVariant"] == "lcd"):
                bin_width = width / num_bins
                offset = bin_width * (1 - settings["binWidth"]) / 2
                row_height = int(bin_width - 2 * offset)
                max_rows = height / row_height
                rows = int(round(value * max_rows))
                for row in range(rows):
                    x1 = int(bin_width * i + offset)
                    x2 = int(bin_width * (i + 1) - offset)
                    y1 = height - int(row_height * (row + 0.5)) + 1
                    y2 = height - int(row_height * row)
                    cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)

    elif settings["style"] == "point":
        for i, value in enumerate(data):
            if (settings["styleVariant"] == "circle"):
                radius = width / num_bins / 2
                x = int(width / num_bins * i + radius)
                point_height = int(height * value - radius)
                midpoint = (x, height - point_height)
                cv2.circle(img, midpoint, int(radius * settings["binWidth"]), color, -1)
            elif (settings["styleVariant"] == "square"):
                bar_height = int(height * value)
                bin_width = width / num_bins
                offset = bin_width * (1 - settings["binWidth"]) / 2
                x1 = int(bin_width * i + offset)
                x2 = int(bin_width * (i + 1) - offset)
                y1 = height - bar_height
                y2 = height - bar_height + int(bin_width - 2 * offset)
                cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)
            elif (settings["styleVariant"] == "donut"):
                radius = width / num_bins / 2
                x = int(width / num_bins * i + radius)
                point_height = int(height * value - radius)
                midpoint = (x, height - point_height)
                cv2.circle(img, midpoint, int(radius * settings["binWidth"]), color, -1)
                cv2.circle(img, midpoint, int(radius * settings["binWidth"] / 2), bg_color, -1)

    elif settings["style"] == "line":
        lineThickness = settings["lineThickness"]
        if (settings["antiAliasing"]):
            lineThickness = settings["lineThickness"] * 2
        bin_width = width / num_bins
        x_coords = [int(bin_width * i) for i in range(len(data) + 1)]
        y_coords = (
            [int(height - height * data[i]) for i in range(len(data))] + [int(height - height * data[0])]
            if settings["polarWarp"]
            else [int(height - height * data[i]) for i in range(len(data))] + [height]
        )
        if settings["styleVariant"] == "simple":
            for i in range(len(data)):
                cv2.line(img, (x_coords[i], y_coords[i]), (x_coords[i + 1], y_coords[i + 1]), color, lineThickness)
        elif settings["styleVariant"] == "filled":
            polygon = np.array(
                [[(x_coords[i], y_coords[i]) for i in range(len(data))] + [(x_coords[len(data) - 1], height), (x_coords[0], height)]]
            , dtype=np.int32)
            cv2.fillPoly(img, [polygon], color)

    if (settings["polarWarp"]):
        img = polar_warp(img, settings)
    if (settings["antiAliasing"]):
        img = cv2.resize(img, (settings["width"], settings["height"]))
    return img

def initialImage(settings, bg_color):
    height = settings["height"]
    width = settings["width"]
    if (settings["antiAliasing"]):
        height = height * 2
        width = width * 2

    return np.full((height, width, 3), bg_color, dtype=np.uint8)

def hex_to_bgr(hex_color):
    rgb = mcolors.to_rgb(hex_color)
    rgb = [int(x * 255) for x in rgb] 
    return tuple(reversed(rgb))

def polar_warp(img, settings):
    original_height, original_width = img.shape[:2]
    size = min(original_height, original_width)
    center = size / 2
    min_radius, max_radius = settings["innerOuterRadius"]

    y_indices, x_indices = np.indices((size, size))
    dx = x_indices - center
    dy = y_indices - center
    distance = np.sqrt(dx**2 + dy**2)
    inner_radius = min_radius * (size / 2)
    outer_radius = max_radius * size / 2
    angle = (np.arctan2(dy, dx) + np.pi / 2) % (2 * np.pi)

    mask = (distance >= inner_radius) & (distance <= outer_radius)
    norm_radius = (distance - inner_radius) / (outer_radius - inner_radius)
    norm_radius = np.clip(norm_radius, 0, 1)

    target_y = (original_height * (1 - norm_radius)).astype(np.int32)
    target_x = (angle / (2 * np.pi) * original_width).astype(np.int32)

    target_y = np.clip(target_y, 0, original_height - 1)
    target_x = np.clip(target_x, 0, original_width - 1)

    bg_color = hex_to_bgr(settings["backgroundColor"])
    warped_img = np.full((size, size, 3), fill_value=bg_color)
    warped_img[mask] = img[target_y[mask], target_x[mask]]

    new_img = initialImage(settings, bg_color)
    offset_y = (new_img.shape[0] - size) // 2
    offset_x = (new_img.shape[1] - size) // 2
    new_img[offset_y:offset_y+size, offset_x:offset_x+size] = warped_img

    return new_img

    if (0):
        original_height, original_width = img.shape[:2]

        size = min(original_height, original_width)
        warped_img = np.zeros((size, size, 3))

        center_x = size / 2
        center_y = size / 2

        for y in range(size):
            for x in range(size):
                dx = x - center_x
                dy = y - center_y
                distance = np.sqrt(dx**2 + dy**2)
                angle = np.arctan2(dy, dx)
                adjusted_angle = (angle + np.pi/2) % (2 * np.pi)
                if (distance >= size // 2):
                    continue
                target_y = int(original_height - distance * 2)
                target_x = int(adjusted_angle / (2 * np.pi) * original_width)
                target_y = np.clip(target_y, 0, original_height - 1)
                target_x = np.clip(target_x, 0, original_width - 1)
                warped_img[y, x] = img[target_y, target_x]

        bg_color = hex_to_bgr(settings["color"])
        new_img = initialImage(settings, bg_color)
        offset_y = int((new_img.shape[0] - warped_img.shape[0]) / 2)
        offset_x = int((new_img.shape[1] - warped_img.shape[1]) / 2)
        new_img[offset_y:offset_y+warped_img.shape[0],offset_x:offset_x+warped_img.shape[1]] = warped_img

        return new_img

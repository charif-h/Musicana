"""
Image color extraction utilities for album artwork.

This module provides functions to analyze album artwork and extract
dominant colors for UI theming.
"""

import operator


def image_histogram(img):
    """
    Extract a histogram of colors from an image.
    
    Colors are quantized to reduce the number of unique colors by grouping
    similar shades together (reduces color depth by 32 levels per channel).
    
    Args:
        img: PIL Image object to analyze
        
    Returns:
        dict: Sorted dictionary of hex color codes and their frequency counts,
              ordered from most to least frequent
    """
    rgb_im = img.convert('RGB')
    hist = {}
    
    # Analyze 300x300 pixel region
    for i in range(300):
        for j in range(300):
            r, g, b = rgb_im.getpixel((i, j))
            
            # Quantize color by reducing to nearest multiple of 32
            # This groups similar colors together
            r = r - r % 32
            g = g - g % 32
            b = b - b % 32
            
            # Convert to hex color code
            key = '#%02x%02x%02x' % (r, g, b)
            
            # Count occurrences
            if key in hist:
                hist[key] += 1
            else:
                hist[key] = 1
    
    # Return sorted by frequency (most common first)
    return dict(sorted(hist.items(), key=operator.itemgetter(1), reverse=True))

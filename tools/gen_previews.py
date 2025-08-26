#!/usr/bin/env python3
import sys
import os
import glob
import argparse
import re
from PIL import Image, ImageDraw

class BDFFont:
    def __init__(self, file_path):
        self.file_path = file_path
        self.chars = {}
        self.bbx = (0, 0, 0, 0)  # width, height, x-offset, y-offset
        self.default_width = 0
        self.max_height = 0
        self.load()
    
    def load(self):
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Get font bounding box
        for i, line in enumerate(lines):
            if line.startswith('FONTBOUNDINGBOX'):
                parts = line.split()
                if len(parts) >= 5:
                    self.bbx = tuple(map(int, parts[1:5]))
                    self.default_width = self.bbx[0]
                    self.max_height = self.bbx[1]
                break
        
        # Parse each character
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('STARTCHAR'):
                char_width = self.default_width
                char_height = self.max_height
                char_code = -1
                char_bbx = None
                bitmap_lines = []
                in_bitmap = False
                
                # Process character block
                i += 1
                while i < len(lines) and not lines[i].startswith('ENDCHAR'):
                    line = lines[i].strip()
                    
                    if line.startswith('ENCODING'):
                        parts = line.split()
                        if len(parts) >= 2:
                            char_code = int(parts[1])
                    
                    elif line.startswith('BBX'):
                        parts = line.split()
                        if len(parts) >= 5:
                            char_bbx = tuple(map(int, parts[1:5]))
                            char_width = char_bbx[0]
                            char_height = char_bbx[1]
                    
                    elif line == 'BITMAP':
                        in_bitmap = True
                    
                    elif in_bitmap:
                        bitmap_lines.append(line)
                    
                    i += 1
                
                # Skip if no valid encoding
                if char_code < 0:
                    i += 1
                    continue
                
                # Process bitmap
                bitmap = []
                for hex_line in bitmap_lines:
                    try:
                        value = int(hex_line, 16)
                        row = []
                        # Calculate bit width based on character width
                        width_bytes = (char_width + 7) // 8
                        bit_width = width_bytes * 8
                        
                        for bit_pos in range(bit_width - 1, -1, -1):
                            bit = (value >> bit_pos) & 1
                            # Only include bits within the actual character width
                            if bit_width - bit_pos <= char_width:
                                row.append(bit)
                        
                        bitmap.append(row)
                    except ValueError:
                        # Skip invalid hex lines
                        continue
                
                self.chars[char_code] = {
                    'bitmap': bitmap,
                    'width': char_width,
                    'height': char_height,
                    'bbx': char_bbx or self.bbx
                }
            
            i += 1
    
    def render_char(self, char_code, draw, x, y, color='black'):
        if char_code not in self.chars:
            return 0  # Return 0 width for missing chars
        
        char_data = self.chars[char_code]
        bitmap = char_data['bitmap']
        width = char_data['width']
        
        for row_idx, row in enumerate(bitmap):
            for col_idx, bit in enumerate(row):
                if bit:
                    draw.point((x + col_idx, y + row_idx), fill=color)
        
        return width  # Return the character width

def render_font_preview(input_filename, output_filename):
    try:
        print(f"Loading font from {input_filename}...")
        font = BDFFont(input_filename)
        
        # Generate character list from printable ASCII range (32-126)
        # Only include characters that actually exist in the font
        specimen_chars = []
        for code in range(32, 127):  # Space (32) to ~ (126)
            if code in font.chars:
                specimen_chars.append(chr(code))
        
        # If we have very few printable characters, try extended range
        if len(specimen_chars) < 20:
            for code in range(1, 256):
                if code in font.chars and chr(code) not in specimen_chars:
                    specimen_chars.append(chr(code))
        
        specimen = ''.join(specimen_chars)
        
        # Get average character metrics
        avg_width = font.default_width
        font_height = font.max_height
        
        # Increase size for better visibility
        scale = 1
        if avg_width < 8 or font_height < 8:
            scale = 3
        elif avg_width < 16 or font_height < 16:
            scale = 2
        
        # Calculate image dimensions
        chars_per_row = 16  # Changed from 20 to match systematic character display
        num_rows = (len(specimen) + chars_per_row - 1) // chars_per_row
        
        char_spacing = 2  # Space between characters
        row_spacing = 5   # Space between rows
        separator_width = 20 * scale  # Space between normal and inverted columns
        
        # Calculate width for two columns
        column_width = chars_per_row * (avg_width + char_spacing) * scale
        img_width = 2 * column_width + separator_width
        img_height = num_rows * (font_height + row_spacing) * scale
        
        # Add margins - ensure enough space for characters that extend below baseline
        margin = 10 * scale
        bottom_margin = (font_height + 5) * scale  # Extra space for character height plus padding
        img_width += 2 * margin
        img_height += margin + bottom_margin
        
        # Create a new image with white background
        image = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Add font name at the top
        font_name = os.path.basename(input_filename)
        draw.text((margin, margin//2), font_name, fill='black')
        
        # Calculate column positions
        left_column_start = margin
        right_column_start = margin + column_width + separator_width
        
        # Draw black background for the entire right half including margins
        black_bg_x1 = left_column_start + column_width + (separator_width // 2)
        black_bg_y1 = 0
        black_bg_x2 = img_width
        black_bg_y2 = img_height
        draw.rectangle([black_bg_x1, black_bg_y1, black_bg_x2, black_bg_y2], fill='black')
        
        # Add the font name in white on the black background
        draw.text((right_column_start, margin//2), font_name, fill='white')
        
        # Render each character in both columns
        for i, char in enumerate(specimen):
            row = i // chars_per_row
            col = i % chars_per_row
            
            # Calculate positions
            char_x_offset = col * (avg_width + char_spacing) * scale
            char_y_offset = (row * (font_height + row_spacing) + font_height) * scale
            
            # Left column (normal): black on white
            left_x = left_column_start + char_x_offset
            left_y = margin + char_y_offset
            
            # Right column (inverted): white on black  
            right_x = right_column_start + char_x_offset
            right_y = margin + char_y_offset
            
            # Draw the character in both columns
            if ord(char) in font.chars:
                char_bitmap = font.chars[ord(char)]['bitmap']
                
                for row_idx, bitmap_row in enumerate(char_bitmap):
                    for col_idx, bit in enumerate(bitmap_row):
                        if bit:
                            # Draw scaled pixel in left column (black)
                            for sx in range(scale):
                                for sy in range(scale):
                                    draw.point((left_x + col_idx*scale + sx, left_y + row_idx*scale + sy), fill='black')
                            
                            # Draw scaled pixel in right column (white)
                            for sx in range(scale):
                                for sy in range(scale):
                                    draw.point((right_x + col_idx*scale + sx, right_y + row_idx*scale + sy), fill='white')
        
        # Save the image
        print(f"Saving preview to {output_filename}...")
        image.save(output_filename)
        print(f"Preview saved successfully")
        return True
        
    except Exception as e:
        print(f"Error processing font {input_filename}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def generate_all_previews():
    # Directory where the previews will be saved
    output_dir = "previews"
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all BDF font files in current directory
    font_files = glob.glob("*.bdf")
    
    if not font_files:
        print("No BDF font files found in the current directory.")
        return False
    
    success_count = 0
    failure_count = 0
    
    for font_file in font_files:
        print(f"\nProcessing font: {font_file}")
        
        # Get full path to the font file
        font_path = os.path.abspath(font_file)
        
        # Output path
        output_path = os.path.join(output_dir, f"{font_file}.png")
        
        # Generate the preview
        if render_font_preview(font_path, output_path):
            success_count += 1
        else:
            failure_count += 1
    
    print(f"\nPreview generation complete.")
    print(f"Successfully generated: {success_count} preview(s)")
    print(f"Failed: {failure_count} preview(s)")
    print(f"All previews saved in: {os.path.abspath(output_dir)}")
    
    return failure_count == 0

def main():
    parser = argparse.ArgumentParser(description='Generate preview images for BDF fonts')
    parser.add_argument('--single', help='Process only a single BDF font file')
    parser.add_argument('--output', help='Custom output PNG image file (for single mode)')
    
    args = parser.parse_args()
    
    if args.single:
        # Process a single font file
        input_file = args.single
        output_file = args.output or os.path.join("previews", f"{os.path.basename(input_file)}.png")
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        success = render_font_preview(input_file, output_file)
    else:
        # Process all font files
        success = generate_all_previews()
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()
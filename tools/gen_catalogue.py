#!/usr/bin/env python3
import sys
import os
import glob
import argparse
from datetime import datetime

class BDFFontInfo:
    def __init__(self, file_path):
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.file_size = os.path.getsize(file_path)
        self.metadata = {}
        self.char_count = 0
        self.load_metadata()
    
    def load_metadata(self):
        """Extract metadata from BDF file"""
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            char_widths = []  # Track character widths for monospace detection
            
            # Extract key metadata fields
            for line in lines:
                line = line.strip()
                
                if line.startswith('FONT '):
                    self.metadata['font_name'] = line[5:].strip()
                elif line.startswith('SIZE '):
                    parts = line.split()
                    if len(parts) >= 2:
                        self.metadata['point_size'] = parts[1]
                    if len(parts) >= 4:
                        self.metadata['resolution_x'] = parts[2]
                        self.metadata['resolution_y'] = parts[3]
                elif line.startswith('FONTBOUNDINGBOX '):
                    parts = line.split()
                    if len(parts) >= 5:
                        self.metadata['bbox_width'] = parts[1]
                        self.metadata['bbox_height'] = parts[2]
                        self.metadata['bbox_x_offset'] = parts[3]
                        self.metadata['bbox_y_offset'] = parts[4]
                elif line.startswith('CHARS '):
                    parts = line.split()
                    if len(parts) >= 2:
                        self.char_count = int(parts[1])
                elif line.startswith('COPYRIGHT '):
                    self.metadata['copyright'] = line[10:].strip(' "')
                elif line.startswith('FAMILY_NAME '):
                    self.metadata['family_name'] = line[12:].strip(' "')
                elif line.startswith('WEIGHT_NAME '):
                    self.metadata['weight_name'] = line[12:].strip(' "')
                elif line.startswith('SLANT '):
                    self.metadata['slant'] = line[6:].strip(' "')
                elif line.startswith('SPACING '):
                    self.metadata['spacing'] = line[8:].strip(' "')
                elif line.startswith('PIXEL_SIZE '):
                    self.metadata['pixel_size'] = line[11:].strip()
                elif line.startswith('POINT_SIZE '):
                    self.metadata['point_size_tenths'] = line[11:].strip()
                elif line.startswith('RESOLUTION_X '):
                    self.metadata['resolution_x'] = line[13:].strip()
                elif line.startswith('RESOLUTION_Y '):
                    self.metadata['resolution_y'] = line[13:].strip()
                elif line.startswith('AVERAGE_WIDTH '):
                    self.metadata['average_width'] = line[14:].strip()
                elif line.startswith('CHARSET_REGISTRY '):
                    self.metadata['charset_registry'] = line[17:].strip(' "')
                elif line.startswith('CHARSET_ENCODING '):
                    self.metadata['charset_encoding'] = line[17:].strip(' "')
                elif line.startswith('DWIDTH '):
                    # Collect character widths for monospace detection
                    parts = line.split()
                    if len(parts) >= 2:
                        char_widths.append(int(parts[1]))
            
            # Analyze character widths for monospace detection
            if char_widths:
                unique_widths = set(char_widths)
                self.metadata['detected_monospace'] = len(unique_widths) == 1
                self.metadata['char_widths_analyzed'] = len(char_widths)
            
        except Exception as e:
            print(f"Warning: Could not read metadata from {self.filename}: {e}")
    
    def get_spacing_type(self):
        """Determine if font is monospaced or proportional"""
        # First check explicit SPACING field
        if 'spacing' in self.metadata:
            spacing = self.metadata['spacing'].upper()
            if spacing in ['M', 'C']:  # M = Monospace, C = Character cell (also monospace)
                return "Monospace"
            elif spacing == 'P':
                return "Proportional"
        
        # Fallback to character width analysis
        if 'detected_monospace' in self.metadata:
            if self.metadata['detected_monospace']:
                return "Monospace"
            else:
                return "Proportional"
        
        return "Unknown"
    
    def get_weight_style(self):
        """Determine font weight and style (normal/bold/italic)"""
        weight_parts = []
        
        # Check WEIGHT_NAME field
        if 'weight_name' in self.metadata:
            weight = self.metadata['weight_name'].lower()
            if 'bold' in weight or weight in ['bold', 'black', 'heavy']:
                weight_parts.append("Bold")
            elif 'light' in weight or weight in ['light', 'thin']:
                weight_parts.append("Light")
            elif weight in ['medium', 'regular', 'normal']:
                weight_parts.append("Medium")
        
        # Check SLANT field
        if 'slant' in self.metadata:
            slant = self.metadata['slant'].upper()
            if slant == 'I':
                weight_parts.append("Italic")
            elif slant == 'O':
                weight_parts.append("Oblique")
            # 'R' = Roman (normal) - don't add anything
        
        # Fallback: analyze font name for style indicators
        if not weight_parts and 'font_name' in self.metadata:
            font_name = self.metadata['font_name'].lower()
            if 'bold' in font_name:
                weight_parts.append("Bold")
            if 'italic' in font_name or 'oblique' in font_name:
                weight_parts.append("Italic")
        
        # Default to Normal if nothing detected
        if not weight_parts:
            weight_parts.append("Normal")
        
        return " ".join(weight_parts)
    
    def get_display_name(self):
        """Get a human-readable font name"""
        if 'font_name' in self.metadata:
            return self.metadata['font_name']
        elif 'family_name' in self.metadata:
            family = self.metadata['family_name']
            weight = self.metadata.get('weight_name', '')
            return f"{family} {weight}".strip()
        else:
            return self.filename.replace('.bdf', '')
    
    def get_size_description(self):
        """Get font size description"""
        parts = []
        if 'pixel_size' in self.metadata:
            parts.append(f"{self.metadata['pixel_size']}px")
        if 'point_size' in self.metadata:
            parts.append(f"{self.metadata['point_size']}pt")
        elif 'point_size_tenths' in self.metadata:
            pt_size = int(self.metadata['point_size_tenths']) / 10
            parts.append(f"{pt_size}pt")
        if 'bbox_width' in self.metadata and 'bbox_height' in self.metadata:
            parts.append(f"{self.metadata['bbox_width']}x{self.metadata['bbox_height']}")
        
        return " / ".join(parts) if parts else "Unknown size"
    
    def format_file_size(self):
        """Format file size in human readable format"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}" if unit != 'B' else f"{int(size)} {unit}"
            size /= 1024.0
        return f"{size:.1f} GB"

def generate_html_catalogue(fonts, output_file="font_catalogue.html"):
    """Generate HTML catalogue of all fonts"""
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BDF Font Catalogue</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #007acc;
            padding-bottom: 10px;
        }}
        .filters {{
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border: 1px solid #ddd;
        }}
        .filter-row {{
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 15px;
        }}
        .filter-group {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .filter-group label {{
            font-weight: bold;
            color: #333;
        }}
        .filter-group input, .filter-group select {{
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }}
        .clear-filters {{
            background-color: #007acc;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        }}
        .clear-filters:hover {{
            background-color: #005c99;
        }}
        .results-info {{
            margin: 10px 0;
            font-weight: bold;
            color: #666;
        }}
        .font-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        .font-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            background-color: #fafafa;
        }}
        .font-card.hidden {{
            display: none;
        }}
        .font-name {{
            font-size: 1.4em;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        .font-descriptor {{
            font-size: 0.8em;
            color: #666;
            font-family: monospace;
            margin-bottom: 10px;
            word-break: break-all;
        }}
        .font-preview {{
            text-align: center;
            margin: 15px 0;
        }}
        .font-preview img {{
            max-width: 100%;
            border: 1px solid #ccc;
            border-radius: 4px;
        }}
        .metadata-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 0.9em;
        }}
        .metadata-table th,
        .metadata-table td {{
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .metadata-table th {{
            background-color: #f0f0f0;
            font-weight: bold;
            width: 40%;
        }}
        .download-link {{
            display: inline-block;
            background-color: #007acc;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 4px;
            margin-top: 10px;
        }}
        .download-link:hover {{
            background-color: #005c99;
        }}
        .generated-info {{
            color: #666;
            font-size: 0.9em;
            text-align: center;
            margin-top: 40px;
            border-top: 1px solid #ddd;
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>BDF Font Catalogue</h1>
        <p>A collection of {len(fonts)} bitmap fonts in BDF format.</p>
        
        <div class="filters">
            <div class="filter-row">
                <div class="filter-group">
                    <label for="searchText">Search:</label>
                    <input type="text" id="searchText" placeholder="Search font names..." style="min-width: 200px;">
                </div>
                <div class="filter-group">
                    <label for="spacingFilter">Spacing:</label>
                    <select id="spacingFilter">
                        <option value="">All</option>
                        <option value="Monospace">Monospace</option>
                        <option value="Proportional">Proportional</option>
                    </select>
                </div>
                <div class="filter-group">
                    <input type="checkbox" id="boldFilter">
                    <label for="boldFilter">Bold fonts only</label>
                </div>
                <div class="filter-group">
                    <input type="checkbox" id="italicFilter">
                    <label for="italicFilter">Italic fonts only</label>
                </div>
                <button class="clear-filters" onclick="clearAllFilters()">Clear Filters</button>
            </div>
        </div>
        
        <div class="results-info" id="resultsInfo">
            Showing {len(fonts)} fonts
        </div>
        
        <div class="font-grid" id="fontGrid">
"""
    
    for font in fonts:
        preview_image = f"previews/{font.filename}.png"
        preview_exists = os.path.exists(preview_image)
        
        spacing_type = font.get_spacing_type()
        weight_style = font.get_weight_style()
        is_bold = "Bold" in weight_style
        is_italic = "Italic" in weight_style or "Oblique" in weight_style
        
        html_content += f"""
            <div class="font-card" 
                 data-filename="{font.filename.lower()}" 
                 data-fontname="{font.get_display_name().lower()}" 
                 data-spacing="{spacing_type}" 
                 data-bold="{str(is_bold).lower()}" 
                 data-italic="{str(is_italic).lower()}">
                <div class="font-name">{font.filename.replace('.bdf', '')}</div>
                <div class="font-descriptor">{font.metadata.get('font_name', 'No descriptor available')}</div>
                
                <div class="font-preview">
"""
        
        if preview_exists:
            html_content += f'                    <img src="{preview_image}" alt="Preview of {font.filename}" loading="lazy">\n'
        else:
            html_content += '                    <p><em>Preview not available</em></p>\n'
        
        html_content += """                </div>
                
                <table class="metadata-table">
"""
        
        # Add metadata rows
        html_content += f'                    <tr><th>Filename</th><td>{font.filename}</td></tr>\n'
        html_content += f'                    <tr><th>File Size</th><td>{font.format_file_size()}</td></tr>\n'
        html_content += f'                    <tr><th>Characters</th><td>{font.char_count}</td></tr>\n'
        html_content += f'                    <tr><th>Size</th><td>{font.get_size_description()}</td></tr>\n'
        html_content += f'                    <tr><th>Spacing</th><td>{font.get_spacing_type()}</td></tr>\n'
        html_content += f'                    <tr><th>Weight/Style</th><td>{font.get_weight_style()}</td></tr>\n'
        
        if 'copyright' in font.metadata:
            html_content += f'                    <tr><th>Copyright</th><td>{font.metadata["copyright"]}</td></tr>\n'
        if 'charset_registry' in font.metadata and 'charset_encoding' in font.metadata:
            charset = f'{font.metadata["charset_registry"]}-{font.metadata["charset_encoding"]}'
            html_content += f'                    <tr><th>Character Set</th><td>{charset}</td></tr>\n'
        
        html_content += f"""                </table>
                
                <a href="{font.filename}" class="download-link" download>Download {font.filename}</a>
            </div>
"""
    
    html_content += f"""        </div>
        
        <div class="generated-info">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>

    <script>
        // Filter functionality
        function applyFilters() {{
            const searchText = document.getElementById('searchText').value.toLowerCase();
            const spacingFilter = document.getElementById('spacingFilter').value;
            const boldFilter = document.getElementById('boldFilter').checked;
            const italicFilter = document.getElementById('italicFilter').checked;
            
            const fontCards = document.querySelectorAll('.font-card');
            let visibleCount = 0;
            
            fontCards.forEach(card => {{
                let visible = true;
                
                // Text search filter
                if (searchText) {{
                    const filename = card.getAttribute('data-filename');
                    const fontname = card.getAttribute('data-fontname');
                    if (!filename.includes(searchText) && !fontname.includes(searchText)) {{
                        visible = false;
                    }}
                }}
                
                // Spacing filter
                if (spacingFilter && card.getAttribute('data-spacing') !== spacingFilter) {{
                    visible = false;
                }}
                
                // Bold filter
                if (boldFilter && card.getAttribute('data-bold') !== 'true') {{
                    visible = false;
                }}
                
                // Italic filter
                if (italicFilter && card.getAttribute('data-italic') !== 'true') {{
                    visible = false;
                }}
                
                if (visible) {{
                    card.classList.remove('hidden');
                    visibleCount++;
                }} else {{
                    card.classList.add('hidden');
                }}
            }});
            
            // Update results info
            const resultsInfo = document.getElementById('resultsInfo');
            const totalCount = fontCards.length;
            if (visibleCount === totalCount) {{
                resultsInfo.textContent = `Showing all ${{totalCount}} fonts`;
            }} else {{
                resultsInfo.textContent = `Showing ${{visibleCount}} of ${{totalCount}} fonts`;
            }}
        }}
        
        function clearAllFilters() {{
            document.getElementById('searchText').value = '';
            document.getElementById('spacingFilter').value = '';
            document.getElementById('boldFilter').checked = false;
            document.getElementById('italicFilter').checked = false;
            applyFilters();
        }}
        
        // Event listeners
        document.getElementById('searchText').addEventListener('input', function() {{
            // Reset other filters when user starts typing
            if (this.value.length > 0) {{
                document.getElementById('spacingFilter').value = '';
                document.getElementById('boldFilter').checked = false;
                document.getElementById('italicFilter').checked = false;
            }}
            applyFilters();
        }});
        document.getElementById('spacingFilter').addEventListener('change', applyFilters);
        document.getElementById('boldFilter').addEventListener('change', applyFilters);
        document.getElementById('italicFilter').addEventListener('change', applyFilters);
        
        // Initialize filters on page load
        document.addEventListener('DOMContentLoaded', applyFilters);
    </script>
</body>
</html>"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML catalogue saved to {{output_file}}")

def generate_markdown_catalogue(fonts, output_file="font_catalogue.md"):
    """Generate Markdown catalogue of all fonts"""
    
    md_content = f"""# BDF Font Catalogue

A collection of {len(fonts)} bitmap fonts in BDF format.

---

"""
    
    for font in fonts:
        preview_image = f"previews/{font.filename}.png"
        preview_exists = os.path.exists(preview_image)
        
        md_content += f"## {font.filename.replace('.bdf', '')}\n\n"
        
        if 'font_name' in font.metadata:
            md_content += f"*{font.metadata['font_name']}*\n\n"
        
        if preview_exists:
            md_content += f"![Preview of {font.filename}]({preview_image})\n\n"
        else:
            md_content += "*Preview not available*\n\n"
        
        md_content += f"**Download:** [{font.filename}]({font.filename})\n\n"
        
        # Metadata table
        md_content += "| Property | Value |\n"
        md_content += "|----------|-------|\n"
        md_content += f"| Filename | `{font.filename}` |\n"
        md_content += f"| File Size | {font.format_file_size()} |\n"
        md_content += f"| Characters | {font.char_count} |\n"
        md_content += f"| Size | {font.get_size_description()} |\n"
        md_content += f"| Spacing | {font.get_spacing_type()} |\n"
        md_content += f"| Weight/Style | {font.get_weight_style()} |\n"
        
        if 'copyright' in font.metadata:
            md_content += f"| Copyright | {font.metadata['copyright']} |\n"
        if 'charset_registry' in font.metadata and 'charset_encoding' in font.metadata:
            charset = f'{font.metadata["charset_registry"]}-{font.metadata["charset_encoding"]}'
            md_content += f"| Character Set | {charset} |\n"
        
        md_content += "\n---\n\n"
    
    md_content += f"\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Markdown catalogue saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Generate HTML and Markdown catalogues for BDF fonts')
    parser.add_argument('--html-only', action='store_true', help='Generate only HTML catalogue')
    parser.add_argument('--md-only', action='store_true', help='Generate only Markdown catalogue')
    parser.add_argument('--output-dir', default='.', help='Output directory for catalogue files')
    
    args = parser.parse_args()
    
    # Find all BDF font files
    font_files = glob.glob("*.bdf")
    
    if not font_files:
        print("No BDF font files found in the current directory.")
        return False
    
    print(f"Found {len(font_files)} BDF font files")
    
    # Load font information
    fonts = []
    for font_file in font_files:
        print(f"Processing {font_file}...")
        font_info = BDFFontInfo(font_file)
        fonts.append(font_info)
    
    # Sort fonts by filename for consistent output
    fonts.sort(key=lambda x: x.filename.lower())
    
    # Generate catalogues
    os.makedirs(args.output_dir, exist_ok=True)
    
    if not args.md_only:
        html_output = os.path.join(args.output_dir, "font_catalogue.html")
        generate_html_catalogue(fonts, html_output)
    
    if not args.html_only:
        md_output = os.path.join(args.output_dir, "font_catalogue.md")
        generate_markdown_catalogue(fonts, md_output)
    
    print("\nCatalogue generation complete!")
    return True

if __name__ == '__main__':
    if not main():
        sys.exit(1)
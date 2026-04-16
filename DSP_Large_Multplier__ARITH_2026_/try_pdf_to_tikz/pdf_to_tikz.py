#!/usr/bin/env python3
"""
Convert PDF figures and draw.io diagrams to TikZ format.
Generates standalone compilable LaTeX documents.
"""

import subprocess
import sys
import os
import argparse
import xml.etree.ElementTree as ET
import base64
import zlib
import urllib.parse
from pathlib import Path


def drawio_xml_to_tikz(xml_path, output_path=None, standalone=True, extra_packages=None):
    """
    Convert draw.io XML directly to TikZ code by parsing the XML structure.
    
    Args:
        xml_path: Path to input draw.io XML file
        output_path: Path to output TikZ file (optional)
        standalone: Wrap in standalone document (default: True)
        extra_packages: Additional LaTeX packages to include
    """
    xml_path = Path(xml_path)
    if output_path is None:
        output_path = xml_path.with_suffix('.tex')
    else:
        output_path = Path(output_path)
    
    try:
        # Parse the XML file
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Find mxGraphModel
        graph_model = root.find('.//mxGraphModel')
        if graph_model is None:
            print("Error: Not a valid draw.io file (missing mxGraphModel)")
            return False
        
        # Get root cell
        root_cell = graph_model.find('.//root')
        if root_cell is None:
            print("Error: Invalid draw.io structure (missing root)")
            return False
        
        # Extract all cells and collect coordinates for bounding box
        cells = root_cell.findall('mxCell')
        
        # Collect all unique colors used
        custom_colors = set()
        
        # First pass: find bounding box and collect colors
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')
        
        for cell in cells:
            # Collect colors
            style = cell.get('style', '')
            style_dict = parse_drawio_style(style)
            fill_color = style_dict.get('fillColor', '')
            stroke_color = style_dict.get('strokeColor', '')
            
            for color in [fill_color, stroke_color]:
                if color and color != 'none':
                    if color.startswith('#'):
                        color = color[1:]
                    if len(color) == 6 and color.upper() not in ['FFFFFF', 'FFFFFF', '000000', 'FF0000', '00FF00', '0000FF', 'FFFF00', 'FFA500', 'FFC0CB', 'A0A0A0']:
                        custom_colors.add(color.upper())
            
            geometry = cell.find('mxGeometry')
            if geometry is None:
                continue
            
            x = float(geometry.get('x', 0))
            y = float(geometry.get('y', 0))
            width = float(geometry.get('width', 0))
            height = float(geometry.get('height', 0))
            
            if width > 0 or height > 0:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x + width)
                max_y = max(max_y, y + height)
        
        # Calculate scaling factor to fit in reasonable TikZ dimensions (max 20cm)
        bbox_width = max_x - min_x
        bbox_height = max_y - min_y
        
        if bbox_width > 0 and bbox_height > 0:
            # Scale to fit in 20cm max dimension
            scale_factor = min(200 / bbox_width, 200 / bbox_height)
        else:
            scale_factor = 0.1
        
        # Start building TikZ code
        tikz_lines = []
        
        # Define custom colors if any
        if custom_colors:
            for color in sorted(custom_colors):
                tikz_lines.append(f"\\definecolor{{drawio{color}}}{{HTML}}{{{color}}}")
        
        tikz_lines.append("\\begin{tikzpicture}")
        
        # Process each cell with scaled coordinates
        for cell in cells:
            cell_id = cell.get('id', '')
            style = cell.get('style', '')
            value = cell.get('value', '')
            
            # Get geometry
            geometry = cell.find('mxGeometry')
            if geometry is None:
                continue
            
            # Parse raw coordinates
            raw_x = float(geometry.get('x', 0))
            raw_y = float(geometry.get('y', 0))
            raw_width = float(geometry.get('width', 0))
            raw_height = float(geometry.get('height', 0))
            
            # Scale and flip Y-axis (TikZ origin is bottom-left, draw.io is top-left)
            x = (raw_x - min_x) * scale_factor
            y = (max_y - (raw_y + raw_height) - min_y) * scale_factor  # Flip Y
            width = raw_width * scale_factor
            height = raw_height * scale_factor
            
            # Skip if no dimensions
            if width == 0 and height == 0:
                continue
            
            # Parse style
            style_dict = parse_drawio_style(style)
            
            # Determine shape type
            shape = style_dict.get('shape', 'rectangle')
            
            # Check if it's an edge (line/arrow)
            if cell.get('edge') == '1':
                # Handle edges/arrows
                source = cell.get('source', '')
                target = cell.get('target', '')
                
                # Get source and target points if available
                source_point = geometry.find('mxPoint[@as="sourcePoint"]')
                target_point = geometry.find('mxPoint[@as="targetPoint"]')
                
                if source_point is not None and target_point is not None:
                    x1 = (float(source_point.get('x', 0)) - min_x) * scale_factor
                    y1 = (float(source_point.get('y', 0)) - min_y) * scale_factor
                    x2 = (float(target_point.get('x', 0)) - min_x) * scale_factor
                    y2 = (float(target_point.get('y', 0)) - min_y) * scale_factor
                    
                    # Determine arrow style
                    arrow_style = get_arrow_style(style_dict)
                    
                    tikz_lines.append(f"    \\draw[{arrow_style}] ({x1:.2f},{y1:.2f}) -- ({x2:.2f},{y2:.2f});")
            
            # Check if it's a vertex (shape)
            elif cell.get('vertex') == '1':
                # Calculate center and corners
                cx = x + width / 2
                cy = y + height / 2
                
                # Get fill and stroke colors
                fill_color = style_dict.get('fillColor', 'white')
                stroke_color = style_dict.get('strokeColor', 'black')
                
                # Convert colors
                fill_tikz = convert_color(fill_color)
                stroke_tikz = convert_color(stroke_color)
                
                # Decode HTML entities and clean text
                import html
                import re
                text = html.unescape(value) if value else ''
                text = text.replace('<br>', '\\\\')
                # Remove HTML tags
                text = re.sub(r'<[^>]+>', '', text)
                # Escape special LaTeX characters
                text = text.replace('_', '\\_').replace('%', '\\%').replace('&', '\\&')
                text = text.replace('#', '\\#').replace('$', '\\$')
                
                # Skip invisible elements (white on white with no text)
                if not text and fill_tikz == 'white' and stroke_tikz == 'white':
                    continue
                
                # Skip very small decorative elements
                if width < 1 and height < 1 and not text:
                    continue
                
                # Draw based on shape
                if shape == 'ellipse':
                    rx = width / 2
                    ry = height / 2
                    tikz_lines.append(f"    \\draw[fill={fill_tikz},draw={stroke_tikz}] ({cx:.2f},{cy:.2f}) ellipse ({rx:.2f} and {ry:.2f});")
                    if text:
                        tikz_lines.append(f"    \\node at ({cx:.2f},{cy:.2f}) {{{text}}};")
                
                elif shape == 'rhombus' or shape == 'diamond':
                    tikz_lines.append(f"    \\node[diamond,fill={fill_tikz},draw={stroke_tikz},minimum width={width:.2f}mm,minimum height={height:.2f}mm] at ({cx:.2f},{cy:.2f}) {{{text}}};")
                
                elif shape == 'cylinder':
                    tikz_lines.append(f"    \\node[cylinder,fill={fill_tikz},draw={stroke_tikz},minimum width={width:.2f}mm,minimum height={height:.2f}mm] at ({cx:.2f},{cy:.2f}) {{{text}}};")
                
                else:  # rectangle or default
                    tikz_lines.append(f"    \\draw[fill={fill_tikz},draw={stroke_tikz}] ({x:.2f},{y:.2f}) rectangle ({x+width:.2f},{y+height:.2f});")
                    if text:
                        tikz_lines.append(f"    \\node at ({cx:.2f},{cy:.2f}) {{{text}}};")
        
        tikz_lines.append("\\end{tikzpicture}")
        
        tikz_code = '\n'.join(tikz_lines)
        
        # Wrap in standalone if requested
        if standalone:
            packages = ['shapes.geometric', 'shapes.misc']
            if extra_packages:
                packages.extend(extra_packages)
            tikz_code = wrap_in_standalone(tikz_code, packages=packages)
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write(tikz_code)
        
        print(f"✓ Converted {xml_path} to {output_path}")
        print(f"  True TikZ conversion from draw.io XML")
        return True
        
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return False
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return False


def parse_drawio_style(style_str):
    """Parse draw.io style string into a dictionary."""
    style_dict = {}
    if not style_str:
        return style_dict
    
    parts = style_str.split(';')
    for part in parts:
        if '=' in part:
            key, value = part.split('=', 1)
            style_dict[key] = value
    
    return style_dict


def get_arrow_style(style_dict):
    """Get TikZ arrow style from draw.io style."""
    arrow_parts = []
    
    # Line width
    stroke_width = style_dict.get('strokeWidth', '1')
    arrow_parts.append(f"line width={stroke_width}pt")
    
    # Arrow ends
    end_arrow = style_dict.get('endArrow', '')
    start_arrow = style_dict.get('startArrow', '')
    
    if end_arrow and end_arrow != 'none':
        if start_arrow and start_arrow != 'none':
            arrow_parts.append('<->')
        else:
            arrow_parts.append('->')
    elif start_arrow and start_arrow != 'none':
        arrow_parts.append('<-')
    
    # Dashed style
    dashed = style_dict.get('dashed', '0')
    if dashed == '1':
        arrow_parts.append('dashed')
    
    return ','.join(arrow_parts) if arrow_parts else 'thick'


def convert_color(color_str):
    """Convert draw.io color to TikZ color."""
    if not color_str or color_str == 'none':
        return 'white'
    
    # Remove # if present
    if color_str.startswith('#'):
        color_str = color_str[1:]
    
    # Common color mappings
    color_map = {
        'FFFFFF': 'white',
        'ffffff': 'white',
        '000000': 'black',
        '000000': 'black',
        'FF0000': 'red',
        'ff0000': 'red',
        '00FF00': 'green',
        '00ff00': 'green',
        '0000FF': 'blue',
        '0000ff': 'blue',
        'FFFF00': 'yellow',
        'ffff00': 'yellow',
        'FFA500': 'orange',
        'ffa500': 'orange',
        'FFC0CB': 'pink',
        'ffc0cb': 'pink',
        'A0A0A0': 'gray',
        'a0a0a0': 'gray',
    }
    
    if color_str in color_map:
        return color_map[color_str]
    
    # For other colors, define as HTML color with proper syntax
    if len(color_str) == 6:
        # Return just the color name - we'll define it in the preamble
        return f"drawio{color_str.upper()}"
    
    return 'white'


def wrap_in_standalone(tikz_content, packages=None):
    """
    Wrap TikZ content in a standalone LaTeX document.
    
    Args:
        tikz_content: The TikZ code to wrap
        packages: Additional LaTeX packages to include
    """
    if packages is None:
        packages = []
    
    # Build TikZ libraries
    tikz_libs = []
    for pkg in packages:
        if pkg in ['shapes.geometric', 'shapes.misc', 'arrows', 'arrows.meta', 'positioning', 'calc', 'patterns']:
            tikz_libs.append(pkg)
    
    tikz_library_line = ''
    if tikz_libs:
        tikz_library_line = f"\\usetikzlibrary{{{','.join(tikz_libs)}}}"
    
    # Other packages (non-tikz)
    other_packages = [pkg for pkg in packages if pkg not in tikz_libs]
    package_lines = '\n'.join([f'\\usepackage{{{pkg}}}' for pkg in other_packages])
    
    standalone_doc = f"""\\documentclass{{standalone}}
\\usepackage[dvipsnames]{{xcolor}}
\\usepackage{{tikz}}
{tikz_library_line}
\\usepackage{{graphicx}}
{package_lines}

\\begin{{document}}
{tikz_content}
\\end{{document}}
"""
    return standalone_doc


def check_command_exists(command):
    """Check if a command exists in the system."""
    try:
        subprocess.run([command, '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def pdf_to_tikz_inkscape(pdf_path, output_path=None, standalone=True, extra_packages=None):
    """
    Convert PDF to TikZ using Inkscape.
    Inkscape has built-in PDF to TikZ conversion.
    
    Args:
        pdf_path: Path to input PDF file
        output_path: Path to output TikZ file (optional)
        standalone: Wrap in standalone document (default: True)
        extra_packages: Additional LaTeX packages to include
    """
    if not check_command_exists('inkscape'):
        print("Error: Inkscape not found. Install with: brew install inkscape")
        return False
    
    pdf_path = Path(pdf_path)
    if output_path is None:
        output_path = pdf_path.with_suffix('.tex')
    
    temp_output = output_path.with_suffix('.tmp.tex') if standalone else output_path
    
    try:
        # Inkscape can export to TikZ/PGF format
        cmd = [
            'inkscape',
            str(pdf_path),
            '--export-type=tex',
            '--export-latex',
            f'--export-filename={temp_output}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            if standalone:
                # Read the generated TikZ content
                with open(temp_output, 'r') as f:
                    tikz_content = f.read()
                
                # Prepare packages list
                packages = ['pgf']
                if extra_packages:
                    packages.extend(extra_packages)
                
                # Wrap in standalone document
                standalone_doc = wrap_in_standalone(tikz_content, packages=packages)
                
                with open(output_path, 'w') as f:
                    f.write(standalone_doc)
                
                # Remove temp file
                temp_output.unlink()
            
            print(f"✓ Converted {pdf_path} to {output_path}")
            return True
        else:
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False


def pdf_to_tikz_via_svg(pdf_path, output_path=None, standalone=True, extra_packages=None):
    """
    Convert PDF to TikZ via SVG intermediate format.
    Uses pdf2svg and svg2tikz.
    
    Args:
        pdf_path: Path to input PDF file
        output_path: Path to output TikZ file (optional)
        standalone: Wrap in standalone document (default: True)
        extra_packages: Additional LaTeX packages to include
    """
    if not check_command_exists('pdf2svg'):
        print("Error: pdf2svg not found. Install with: brew install pdf2svg")
        return False
    
    pdf_path = Path(pdf_path)
    svg_path = pdf_path.with_suffix('.svg')
    
    if output_path is None:
        output_path = pdf_path.with_suffix('.tex')
    
    try:
        # Step 1: Convert PDF to SVG
        print(f"Converting {pdf_path} to SVG...")
        subprocess.run(['pdf2svg', str(pdf_path), str(svg_path)], check=True)
        
        # Step 2: Convert SVG to TikZ using svg2tikz
        print(f"Converting SVG to TikZ...")
        try:
            from svg2tikz import convert_svg
            
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            tikz_code = convert_svg(svg_content)
            
            if standalone:
                tikz_code = wrap_in_standalone(tikz_code, packages=extra_packages)
            
            with open(output_path, 'w') as f:
                f.write(tikz_code)
            
            print(f"✓ Converted {pdf_path} to {output_path}")
            
            # Clean up SVG
            svg_path.unlink()
            return True
            
        except ImportError:
            print("Error: svg2tikz not found. Install with: pip install svg2tikz")
            return False
            
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False


def pdf_to_tikz_simple_include(pdf_path, output_path=None, standalone=True, extra_packages=None):
    """
    Generate a simple TikZ wrapper that includes the PDF.
    This doesn't convert the PDF content but creates a TikZ node with the PDF.
    
    Args:
        pdf_path: Path to input PDF file
        output_path: Path to output TikZ file (optional)
        standalone: Wrap in standalone document (default: True)
        extra_packages: Additional LaTeX packages to include
    """
    pdf_path = Path(pdf_path)
    if output_path is None:
        output_path = pdf_path.with_name(f"{pdf_path.stem}_tikz.tex")
    
    tikz_code = f"""% TikZ wrapper for {pdf_path.name}
\\begin{{tikzpicture}}
    \\node[inner sep=0pt] {{
        \\includegraphics[width=\\textwidth]{{{pdf_path.name}}}
    }};
\\end{{tikzpicture}}
"""
    
    if standalone:
        tikz_code = wrap_in_standalone(tikz_code, packages=extra_packages)
    
    with open(output_path, 'w') as f:
        f.write(tikz_code)
    
    print(f"✓ Generated TikZ wrapper at {output_path}")
    print(f"Note: This includes the PDF, not a true conversion")
    return True


def drawio_to_tikz(drawio_path, output_path=None, standalone=True, extra_packages=None, method='wrapper'):
    """
    Convert draw.io file (.drawio or .xml) to TikZ.
    First converts to PDF using draw.io CLI, then applies the chosen conversion method.
    
    Args:
        drawio_path: Path to input draw.io file (.drawio or .xml)
        output_path: Path to output TikZ file (optional)
        standalone: Wrap in standalone document (default: True)
        extra_packages: Additional LaTeX packages to include
        method: Conversion method to use after PDF export
    """
    if not check_command_exists('drawio'):
        print("Error: draw.io CLI not found.")
        print("Install with: brew install --cask drawio")
        print("Or download from: https://github.com/jgraph/drawio-desktop/releases")
        return False
    
    drawio_path = Path(drawio_path)
    if output_path is None:
        output_path = drawio_path.with_suffix('.tex')
    else:
        output_path = Path(output_path)
    
    # Create PDF with proper name (same as output but .pdf extension)
    output_pdf = output_path.with_suffix('.pdf')
    
    try:
        # Step 1: Export draw.io to PDF
        print(f"Exporting {drawio_path} to PDF...")
        cmd = [
            'drawio',
            '--export',
            '--format', 'pdf',
            '--output', str(output_pdf),
            str(drawio_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error exporting draw.io file: {result.stderr}")
            return False
        
        # Step 2: Convert PDF to TikZ using chosen method
        print(f"Converting PDF to TikZ using {method} method...")
        
        if method == 'inkscape':
            success = pdf_to_tikz_inkscape(output_pdf, output_path, standalone, extra_packages)
        elif method == 'svg':
            success = pdf_to_tikz_via_svg(output_pdf, output_path, standalone, extra_packages)
        else:  # wrapper
            success = pdf_to_tikz_simple_include(output_pdf, output_path, standalone, extra_packages)
        
        if success:
            print(f"✓ Converted {drawio_path} to {output_path}")
            print(f"Note: PDF file kept at {output_pdf} for LaTeX compilation")
        
        return success
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False


def main():
    """Main function to handle command-line usage."""
    parser = argparse.ArgumentParser(
        description='Convert PDF figures to TikZ format with standalone LaTeX documents.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert PDF (uses wrapper method by default)
  %(prog)s input.pdf
  
  # Convert draw.io file
  %(prog)s diagram.drawio -o output.tex
  
  # Convert draw.io XML export
  %(prog)s diagram.xml -o output.tex
  
  # Specify output file
  %(prog)s input.pdf -o output.tex
  
  # Use different conversion method
  %(prog)s input.pdf -m svg
  
  # Generate TikZ code only (no standalone wrapper)
  %(prog)s input.pdf --no-standalone
  
  # Full example with all options
  %(prog)s diagram.pdf -o figure.tex -m inkscape --packages pgfplots,amsmath

Supported Formats:
  PDF        - Portable Document Format (.pdf)
  draw.io    - draw.io diagram files (.drawio, .xml)

Conversion Methods:
  wrapper    - Simple wrapper (recommended, just includes PDF/figure)
  inkscape   - Advanced (requires: brew install inkscape)
  svg        - Via SVG (requires: brew install pdf2svg, pip install svg2tikz)
        """
    )
    
    # Required arguments
    parser.add_argument(
        'input',
        type=str,
        help='Input PDF file to convert'
    )
    
    # Optional arguments
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output TikZ/LaTeX file (default: input filename with .tex extension)'
    )
    
    parser.add_argument(
        '-m', '--method',
        type=str,
        choices=['inkscape', 'svg', 'wrapper'],
        default='wrapper',
        help='Conversion method to use (default: wrapper, recommended for most PDFs)'
    )
    
    parser.add_argument(
        '--no-standalone',
        action='store_true',
        help='Generate only TikZ code without standalone document wrapper'
    )
    
    parser.add_argument(
        '--packages',
        type=str,
        default='',
        help='Additional LaTeX packages to include (comma-separated, e.g., "pgfplots,amsmath")'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: File '{args.input}' not found")
        sys.exit(1)
    
    # Detect file type
    input_path = Path(args.input)
    file_extension = input_path.suffix.lower()
    is_drawio = file_extension in ['.drawio', '.xml']
    
    # For XML files, check if it's actually a draw.io file
    if file_extension == '.xml':
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read(200)  # Read first 200 chars
                if 'mxfile' not in content and 'mxGraphModel' not in content:
                    print("Warning: XML file doesn't appear to be a draw.io file")
                    print("Treating as draw.io anyway...")
        except:
            pass
    
    # Determine output path
    output_path = args.output
    if output_path is None:
        output_path = Path(args.input).with_suffix('.tex')
    else:
        output_path = Path(output_path)
    
    # Parse additional packages
    extra_packages = [pkg.strip() for pkg in args.packages.split(',') if pkg.strip()]
    
    # Print conversion info
    if args.verbose:
        print(f"Input file: {args.input}")
        print(f"File type: {'draw.io' if is_drawio else 'PDF'}")
        print(f"Output file: {output_path}")
        print(f"Method: {args.method}")
        print(f"Standalone: {not args.no_standalone}")
        if extra_packages:
            print(f"Extra packages: {', '.join(extra_packages)}")
        print()
    
    standalone = not args.no_standalone
    
    # Perform conversion based on file type and method
    if is_drawio:
        # Draw.io file - convert XML directly to TikZ
        success = drawio_xml_to_tikz(args.input, output_path, standalone, extra_packages)
    else:
        # PDF file - direct conversion
        if args.method == 'inkscape':
            success = pdf_to_tikz_inkscape(args.input, output_path, standalone, extra_packages)
        elif args.method == 'svg':
            success = pdf_to_tikz_via_svg(args.input, output_path, standalone, extra_packages)
        elif args.method == 'wrapper':
            success = pdf_to_tikz_simple_include(args.input, output_path, standalone, extra_packages)
        else:
            print(f"Error: Unknown method '{args.method}'")
            success = False
    
    # Fallback on failure (only for PDF files)
    if not success and not is_drawio:
        print("\nFalling back to simple wrapper method...")
        pdf_to_tikz_simple_include(args.input, output_path, standalone, extra_packages)
    
    # Final success message
    if standalone:
        print(f"\n✓ Generated standalone LaTeX document: {output_path}")
        print(f"  Compile with: pdflatex {output_path}")
    else:
        print(f"\n✓ Generated TikZ code: {output_path}")
        print(f"  Include in your document with: \\input{{{output_path}}}")


if __name__ == '__main__':
    main()

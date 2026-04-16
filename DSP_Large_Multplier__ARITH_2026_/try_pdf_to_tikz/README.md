# PDF/Draw.io to TikZ Converter

A Python tool to convert PDF figures and draw.io diagrams into standalone TikZ/LaTeX documents that can be compiled independently.

## Features

- **Multiple Input Formats**: PDF, draw.io (.drawio), and draw.io XML exports (.xml)
- **Multiple Conversion Methods**: Inkscape, SVG intermediate, or simple wrapper
- **Standalone Documents**: Generates complete LaTeX files ready to compile
- **Flexible Output**: Create standalone documents or just TikZ code snippets

## Installation

### Required: Python 3

The script requires Python 3.6+.

### Optional: Install draw.io CLI (for .drawio and .xml files)

```bash
brew install --cask drawio
```

Or download from: https://github.com/jgraph/drawio-desktop/releases

### Optional: Install Inkscape (Advanced Conversion)

```bash
brew install inkscape
```

### Optional: Install SVG Method Dependencies

```bash
brew install pdf2svg
pip install svg2tikz
```

## Supported File Formats

| Format | Extensions | Notes |
|--------|------------|-------|
| PDF | `.pdf`or draw.io file to a standalone TikZ document:

```bash
# Convert PDF
python pdf_to_tikz.py your_figure.pdf

# Convert draw.io file
python pdf_to_tikz.py diagram.drawio

# Convert draw.io XML export
python pdf_to_tikz.py diagram.xml
```

This creates a `.tex` file

Convert a PDF to a standalone TikZ document:

```bash
python pdf_to_tikz.py your_figure.pdf
```

This creates `your_figure.tex` which you can compile directly:

```bash
pdflatex your_figure.tex
```

### Command-Line Options
file to convert (PDF, .drawio, or .xml from draw.io)

optional arguments:
  -h, --help            Show help message
  -o OUTPUT, --output OUTPUT
                        Output TikZ/LaTeX file (default: input filename with .tex extension)
  -m {wrapper,inkscape,svg}, --method {wrapper,inkscape,svg}
                        Conversion method to use (default: wrapper)
  --no-standalone       Generate only TikZ code without standalone document wrapper
  --packages PACKAGES   Additional LaTeX packages to include (comma-separated)
  -v, --verbose         Enable verbose output
```

### Examples

```bash
# Basic PDF conversion (default wrapper method)
python pdf_to_tikz.py figure.pdf

# Convert draw.io diagram
python pdf_to_tikz.py flowchart.drawio -o flowchart.tex

# Convert draw.io XML export
python pdf_to_tikz.py diagram.xml

# Specify output file
python pdf_to_tikz.py input.pdf -o output.tex

# Use different conversion method for PDF
python pdf_to_tikz.py figure.pdf -m svg

# Use wrapper method for draw.io
python pdf_to_tikz.py diagram.drawio
python pdf_to_tikz.py input.pdf -o output.tex

# Use different conversion method
python pdf_to_tikz.py figure.pdf -m svg

# Use wrapper method
python pdf_to_tikz.py figure.pdf -m wrapper

# Generate TikZ code only (no standalone wrapper)
python pdf_to_tikz.py figure.pdf --no-standalone

# Add extra LaTeX packages
python pdf_to_tikz.py diagram.pdf --packages pgfplots,amsmath

# Full example with all optionsBest For |
|--------|---------|-------|--------------|----------|
| `wrapper` | ⭐⭐⭐ | Fast | None | Quick inclusion, preserves original quality |
| `inkscape` | ⭐⭐⭐⭐ | Medium | Inkscape | Vector graphics, complex figures |
| `svg` | ⭐⭐⭐⭐ | Slow | pdf2svg, svg2tikz | Simple graphics |

**Note**: For draw.io files, the file is first exported to PDF, then the selected method is applied.

| Method | Quality | Speed | Requirements | Notes |
|--------|---------|-------|--------------|-------|
| `inkscape` | ⭐⭐⭐⭐⭐ | Medium | Inkscape | Best for complex figures |
| `svg` | ⭐⭐⭐⭐ | Slow | pdf2svg, svg2tikz | Good for simple graphics |
| `wrapper` | ⭐⭐ | Fast | None | Just wraps PDF, doesn't convert |

## Output

The tool generates a complete LaTeX document with:

- `\documentclass{standalone}` for standalone compilation
- Required packages: `tikz`, `graphicx`, `xcolor`, `pgf`
- Ready-to-compile TikZ code

### Example Output Structure

```latex
\documentclass{standalone}
\usepackage{tikz}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{pgf}

\begin{document}
% Your TikZ code here
\end{document}
```

## Examples

### Convert and Compile

```bash
# Convert PDF to TikZ
python pdf_to_tikz.py diagram.pdf

# Compile the output
pdflatex diagram.tex
```

##Convert all draw.io files
for drawio in *.drawio; do
    python pdf_to_tikz.py "$drawio" -v
done

# With specific method
for pdf in *.pdf; do
    python pdf_to_tikz.py "$pdf" -m wrapper
# Convert all PDFs in current directory
for pdf in *.pdf; do
    python pdf_to_tikz.py "$pdf"
done

# With specific method
for pdf in *.pdf; do
    python pdf_to_tikz.py "$pdf" -m inkscape -v
done
```

### Using Different Methods

```bash
# Try Inkscape first (best quality)
python pdf_to_tikz.py chart.pdf -m inkscape

# Fall back to SVG method if needed
python pdf_to_tikz.py chart.pdf -m svg
draw.io CLI not found:**
```bash
brew install --cask drawio
```

**Inkscape not found:**
```bash
brew install inkscape
```

**pdf2svg not found:**
```bash
brew install pdf2svg
```

**svg2tikz not found:**
```bash
pip install svg2tikz
```

**draw.io XML file not recognized:**
Make sure the XML file is exported from draw.io and contains `mxfile` or `mxGraphModel` tags.bash
brew install pdf2svg
```

**svg2tikz not found:**
```bash
pip install svg2tikz
```

## License

Free to use and modify.

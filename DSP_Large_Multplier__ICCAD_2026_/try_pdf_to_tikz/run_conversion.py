#!/usr/bin/env python3
"""Quick test script to run the conversion"""

from pathlib import Path
from pdf_to_tikz import drawio_xml_to_tikz

xml_file = Path('cascade_p_to_c_dsp_slice.drawio.xml')
output_file = Path('p_to_c_standalone_fixed.tex')

print(f"Converting {xml_file} to {output_file}...")
result = drawio_xml_to_tikz(xml_file, output_file, standalone=True)
print(f"Result: {result}")

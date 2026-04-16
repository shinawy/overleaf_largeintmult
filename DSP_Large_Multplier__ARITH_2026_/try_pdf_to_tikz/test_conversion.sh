#!/bin/bash
cd "/Users/elshenma/Dropbox/Apps/Overleaf/DSP Large Multplier (2025)/try_pdf_to_tikz"
rm -f test_real_tikz.tex test_real_tikz.pdf
python pdf_to_tikz.py cascade_p_to_c_dsp_slice.drawio.xml -o test_real_tikz.tex -v
echo ""
echo "=== First 40 lines of generated TikZ file ==="
head -40 test_real_tikz.tex
echo ""
echo "=== Checking for actual TikZ code (not PDF inclusion) ==="
if grep -q "\\\\draw" test_real_tikz.tex; then
    echo "✓ SUCCESS: Found actual TikZ \\draw commands!"
elif grep -q "includegraphics" test_real_tikz.tex; then
    echo "✗ FAIL: Still using PDF inclusion, not true TikZ conversion"
fi

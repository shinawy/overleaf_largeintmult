# ArithV Minted Setup Guide

This document describes how to set up and use the custom ArithV syntax highlighting with minted in this LaTeX project.

## Overview

This project uses **minted** for syntax highlighting of ArithV code. Minted requires:
1. The `minted` LaTeX package
2. Python with Pygments installed
3. A custom Pygments lexer for ArithV syntax
4. Compilation with `-shell-escape` flag

## Files Added

- **arithvlexer.py**: Custom Pygments lexer defining ArithV syntax (keywords, operations, attributes)
- **setup.py**: Python package setup file for registering the lexer with Pygments
- **sections/General/utils.tex**: Contains minted configuration for ArithV
- **makefile**: Updated to support `LATEXFLAGS` for passing compiler flags

## Initial Setup

### Step 1: Install the ArithV Lexer

The custom lexer must be installed for the Python version that your LaTeX distribution uses.

#### Find Your System's Pygments

```bash
which pygmentize
```

Common locations:
- `/Library/TeX/texbin/pygmentize` (MacTeX)
- `/usr/local/bin/pygmentize` (Linux/custom install)
- `/usr/bin/pygmentize` (System default)

#### Check Which Python Version It Uses

```bash
head -1 $(which pygmentize)
```

Example output: `#!/opt/homebrew/opt/python@3.10/bin/python3.10`

#### Install the Lexer for the Correct Python

Navigate to the project directory and install:

```bash
cd "/Users/elshenma/Dropbox/Apps/Overleaf/DSP Large Multplier (2025)"

# If pygmentize uses /opt/homebrew/opt/python@3.10/bin/python3.10:
/opt/homebrew/opt/python@3.10/bin/python3.10 -m pip install -e . --user

# Or for the system default Python:
pip3 install -e . --user

# Or with sudo for global installation:
sudo pip3 install -e .
```

#### Verify Installation

```bash
pygmentize -L lexers | grep -i arithv
```

Expected output:
```
* arithv:
    ArithV (filenames *.arithv)
```

### Step 2: Compile with Shell-Escape

Minted requires the `-shell-escape` flag to run Pygments during compilation.

#### Using the Makefile

```bash
# Compile with minted support
make LATEXFLAGS=-shell-escape run

# With bibliography
make LATEXFLAGS=-shell-escape run-with-bib

# Keep auxiliary files for debugging
make LATEXFLAGS=-shell-escape run-keep
```

#### Direct Command Line

```bash
pdflatex -shell-escape egg_dsp.tex
```

## Usage in LaTeX

The `\arithvinputlisting` command works like `\lstinputlisting`:

```latex
\begin{figure}[t]
\centering
\arithvinputlisting{arithvfiles/test_arithvaddertree.arithv}
\caption{ArithV code example.}
\label{lst:addertree}
\end{figure}
```

Or with resize for column width:

```latex
\begin{figure}[t]
\centering
\resizebox{\columnwidth}{!}{%
\begin{minipage}{\textwidth}
\arithvinputlisting{arithvfiles/test_arithvaddertree.arithv}
\end{minipage}
}
\caption{ArithV code example.}
\label{lst:addertree}
\end{figure}
```

## Syntax Highlighting Features

The ArithV lexer highlights:

- **Type Keywords** (blue): `input`, `output`, `variable`, `TestBench`, `Module`
- **Operations** (purple/magenta): `Add`, `Sub`, `Mul`, `Shl`, `Shr`, `And`, `Or`, `Xor`, `Not`, `Concat`, `Slice`, `PrimMul`, `PrimAdd`
- **Attributes** (orange): `is_signed`, `op_mode`
- **Comments**: Lines starting with `#`
- **Strings**: Single and double quoted strings

## Common Errors and Solutions

### Error 1: Missing Pygments Output

```
! Package minted Error: Missing Pygments output; \inputminted was
probably given a file that does not exist--otherwise, you may need 
the outputdir package option, or may be using an incompatible build tool,
or may be using frozencache with a missing file.
```

**Causes:**
1. Forgot to compile with `-shell-escape`
2. ArithV lexer not installed
3. File path is incorrect
4. Lexer installed for wrong Python version

**Solutions:**
1. Add `-shell-escape` flag: `make LATEXFLAGS=-shell-escape run`
2. Verify lexer installation: `pygmentize -L lexers | grep arithv`
3. Check file exists: `ls arithvfiles/test_arithvaddertree.arithv`
4. Reinstall lexer for correct Python version (see Step 1)

### Error 2: Frame Style 'tb' Not Defined

```
! FancyVerb Error:
  Frame style `tb' not defined.
```

**Cause:** Minted uses different frame style names than lstlisting

**Solution:** Already fixed in `utils.tex`. Minted uses `frame=lines` instead of `frame=tb`

### Error 3: Line Break Symbols Appearing

**Cause:** Default minted behavior shows symbols when lines wrap

**Solution:** Already configured in `utils.tex`:
```latex
breaksymbolleft={},
breaksymbolright={},
```

### Error 4: Lexer Not Found After Installation

```
Error: no lexer for alias 'arithv' found
```

**Cause:** Lexer installed for different Python than LaTeX uses

**Solution:**
1. Find which Python LaTeX uses: `head -1 $(which pygmentize)`
2. Install for that specific Python version
3. Verify: `$(which pygmentize) -L lexers | grep arithv`

## Overleaf Usage

**Good News:** On Overleaf, you don't need to install anything!

1. Upload `arithvlexer.py` and `setup.py` to your project
2. Overleaf automatically enables `-shell-escape`
3. The lexer should work via the `-x` flag in minted

If issues occur on Overleaf, you may need to use the Python lexer or text lexer instead:

```latex
\newcommand{\arithvinputlisting}[2][]{%
  \inputminted[#1]{python}{#2}%
}
```

## Configuration Details

### Minted Settings in utils.tex

```latex
\newmintedfile[arithvfile]{arithv}{%
  breaklines=true,          % Allow line breaking
  fontsize=\small,          % Small font size
  fontfamily=tt,            % Typewriter (monospace) font
  frame=lines,              % Top and bottom lines
  linenos=true,             % Show line numbers
  numbersep=1em,            % Space between numbers and code
  xleftmargin=3em,          % Left margin
  autogobble=true,          % Remove common indentation
  breaksymbolleft={},       % No break symbols
  breaksymbolright={},      % No break symbols
}
```

## Updating the Lexer

If you need to add more keywords or change syntax highlighting:

1. Edit `arithvlexer.py`
2. Reinstall: `pip3 install -e . --user --force-reinstall`
3. Recompile your document

## Security Note

**Important:** The `-shell-escape` flag allows LaTeX to execute external programs. Only use it with trusted documents, as it can potentially run arbitrary code during compilation.

## Troubleshooting Checklist

- [ ] ArithV lexer installed: `pygmentize -L lexers | grep arithv`
- [ ] Compiling with `-shell-escape` flag
- [ ] File path is correct and file exists
- [ ] Pygments version ≥ 2.0 installed
- [ ] Using the correct Python version for your LaTeX distribution

## Alternative: Reverting to lstlisting

If minted causes issues, you can revert to lstlisting by changing in your tex files:

```latex
% Replace:
\arithvinputlisting{arithvfiles/file.arithv}

% With:
\lstinputlisting[style=arithvstyle]{arithvfiles/file.arithv}
```

The lstlisting definition is already configured in `utils.tex` and works without shell-escape.

## Additional Resources

- [Minted Documentation](https://ctan.org/pkg/minted)
- [Pygments Lexer Development](https://pygments.org/docs/lexerdevelopment/)
- [Custom Pygments Lexers](https://pygments.org/docs/plugins/)

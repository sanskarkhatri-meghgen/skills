#!/usr/bin/env python3
"""
Generate a draw.io editable URL from a .drawio XML file.

Format: https://app.diagrams.net/?libs={libs}#R{base64(raw_deflate(encodeURIComponent(xml)))}

Usage:
    python3 gen_drawio_url.py <file.drawio>
    python3 gen_drawio_url.py <file.drawio> --libs gcp2
    python3 gen_drawio_url.py <file.drawio> --libs "gcp2;aws4"
"""
import sys
import zlib
import base64
import urllib.parse
import argparse

def generate_drawio_url(filepath, libs=None):
    with open(filepath, 'r') as f:
        xml = f.read()

    # URI-encode (equivalent to JS encodeURIComponent)
    encoded = urllib.parse.quote(xml, safe='')

    # Raw deflate compress — single compressor instance
    compressor = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -15)
    compressed = compressor.compress(encoded.encode('utf-8'))
    compressed += compressor.flush()

    # Base64 encode
    b64 = base64.b64encode(compressed).decode('utf-8')

    # Build URL with optional libs parameter
    if libs:
        return f"https://app.diagrams.net/?libs={libs}#R{b64}"
    else:
        return f"https://app.diagrams.net/#R{b64}"

def auto_detect_libs(filepath):
    """Auto-detect required libraries by scanning the XML for shape references."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    libs = []
    if 'mxgraph.gcp2.' in content:
        libs.append('gcp2')
    if 'img/lib/aws4/' in content:
        libs.append('aws4')
    
    return ';'.join(libs) if libs else None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate draw.io URL from .drawio file')
    parser.add_argument('file', help='Path to .drawio XML file')
    parser.add_argument('--libs', help='draw.io shape libraries to load (e.g. gcp2, aws4, "gcp2;aws4")')
    parser.add_argument('--auto', action='store_true', help='Auto-detect required libraries from XML content')
    args = parser.parse_args()

    libs = args.libs
    if args.auto and not libs:
        libs = auto_detect_libs(args.file)
    
    print(generate_drawio_url(args.file, libs))

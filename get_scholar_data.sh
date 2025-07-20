#!/bin/bash

# Get google scholar stats stored in my personal webpage repo

# Step 1: Download the JSON file
curl -sSL "https://raw.githubusercontent.com/b-fg/b-fg.github.io/refs/heads/main/.scholar_cache/scholar_data.json" -o scholar_data.json

citations=$(jq '.citations' scholar_data.json)
hindex=$(jq '.h_index' scholar_data.json)
i10index=$(jq '.i10_index' scholar_data.json)

# Write LaTeX commands into a separate file
cat <<EOF > scholar_data.tex
\\newcommand{\\citations}{$citations}
\\newcommand{\\hindex}{$hindex}
\\newcommand{\\iindex}{$i10index}
EOF
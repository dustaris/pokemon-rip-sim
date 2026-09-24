#!/bin/sh
# Builds the standalone GitHub Pages copy in docs/ from index.html (which is written for the Claude artifact wrapper).
set -e
cd "$(dirname "$0")/.."
rm -rf docs && mkdir -p docs/img
{
  printf '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  printf '<meta name="description" content="Rip virtual Pokémon TCG 30th Celebration packs at real pull rates and see the TCGplayer market value of your pulls. An unofficial fan project by WD Card Shop.">\n'
  printf '<link rel="icon" href="img/duck.png">\n'
  printf '<style>body{margin:0}img{max-width:100%%}[hidden]{display:none!important}</style>\n</head>\n<body>\n'
  grep -v '^<meta charset="utf-8">$' index.html
  printf '\n</body>\n</html>\n'
} > docs/index.html
cp data.js docs/
cp -R img/c img/duck.png docs/img/
touch docs/.nojekyll

#!/bin/sh
# Etiquetage colorimetrique de assets/lezard.mp4 — sans reencodage.
#
# Sans balises, chaque decodeur devine : ffmpeg a extrait les images en
# matrice BT.601, Chrome relisait le meme fichier en BT.709. Le decor de la
# video sortait alors 10/255 plus clair que la plaque, et le cadre video se
# voyait comme un rectangle pose sur le fond.
#
# Deux corrections, dans cet ordre :
#   matrix_coefficients=6 (smpte170m)  -> meme matrice YUV->RGB que ffmpeg
#   colour_primaries=1, transfer=13    -> primaires et courbe sRGB
# La seconde compte autant que la premiere : etiquetees en 601, les primaires
# declenchent une conversion de gestion des couleurs a l'affichage, et le
# rectangle reapparait (invisible, lui, dans une lecture canvas).
#
# Ecart mesure apres etiquetage : 1,6/255 en moyenne, 4 au pire.

set -e
cd "$(dirname "$0")/.."
ffmpeg -v error -y -i build/lezard-sans-tags.mp4 -c copy \
  -bsf:v "h264_metadata=colour_primaries=1:transfer_characteristics=13:matrix_coefficients=6:video_full_range_flag=0" \
  assets/lezard.mp4
ffprobe -v error -select_streams v:0 \
  -show_entries stream=color_range,color_space,color_primaries,color_transfer \
  -of default=noprint_wrappers=1 assets/lezard.mp4

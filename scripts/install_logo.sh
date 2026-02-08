#!/usr/bin/env sh
# Copy logo from project root or uploads to app static folder so Flask can serve it.
set -e
SRC1="uploads/logo.png"
SRC2="logo.png"
DST="app/static/logo.png"
mkdir -p app/static
if [ -f "$SRC1" ]; then
  cp "$SRC1" "$DST"
  echo "Copied $SRC1 -> $DST"
elif [ -f "$SRC2" ]; then
  cp "$SRC2" "$DST"
  echo "Copied $SRC2 -> $DST"
else
  echo "No logo file found. Place your logo at $SRC1 or $SRC2 and re-run this script."
  exit 1
fi

#!/usr/bin/env bash

# Convert every source icon, continuing past individual conversion failures.
set -u

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
input_dir="$script_dir/icons"
output_dir="$input_dir/square"

if ! mkdir -p "$output_dir"; then
  printf 'error: could not create output directory: %s\n' "$output_dir" >&2
  exit 1
fi

shopt -s nullglob
icons=("$input_dir"/*.svg)

if ((${#icons[@]} == 0)); then
  printf 'No SVG files found in %s\n' "$input_dir"
  exit 0
fi

converted=0
failed=()

for icon in "${icons[@]}"; do
  output="$output_dir/$(basename -- "$icon")"
  if python3 "$script_dir/svg_icon_resizer.py" "$icon" "$output"; then
    ((converted += 1))
  else
    failed+=("$icon")
  fi
done

printf 'Converted %d of %d SVG files.\n' "$converted" "${#icons[@]}"

if ((${#failed[@]} > 0)); then
  printf 'Failed conversions:\n' >&2
  printf '  %s\n' "${failed[@]}" >&2
  exit 1
fi

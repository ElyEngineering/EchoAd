# Echo Ad: design notes

Static mockup of a quarter-page (5 x 8 in) Ely Echo ad, built as a 1000 x 1600 px artboard. There's no build step: Vercel serves `index.html` as is.

- `index.html`, `styles.css`: the ad
- `photos/square/*.jpg`: 1200 x 1200 grayscale headshots, cropped with face detection so every face has the same zoom (`*_color.jpg` are the color versions)
- `photos/canoe_banner.jpg`: Boundary Waters canoe photo by Daniel Ziegler, CC BY-SA 4.0
- `photos/originals/`: untouched source images, plus `sources.json` with each image's source page, size, rights notes and crop box
- `photos/facecrop.py`: rebuilds the headshot crops from the originals

Placeholders and print notes:
- "Prepared and paid for by ________" is a placeholder. Minnesota requires a disclaimer.
- The Zupek, Kannas and Weise headshots are low-res crops from Ely Echo group photos and are not print-ready. Get the originals from the Ely Echo or from the candidates.
- The Campbell and Forsman city portraits are about 300 px, so they're borderline for print.
- The ballot spells the name "Mark Zupec". The ad keeps "Zupek" as requested.

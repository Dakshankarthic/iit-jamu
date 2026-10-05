# Chanda Mama (चन्दमामा) — Sanskrit Restoration & OCR Dataset

A comprehensive digital restoration, transcription, and visual audit repository for the historic **Chanda Mama (Sanskrit Edition)** children's magazine (68 pages complete).

---

## 📌 Repository Contents

`
├── image/                                 # 68 original high-resolution scanned magazine pages (JPEG)
│   ├── Chanda_Mama_01.jpg
│   └── ...
├── ocr_output/
│   ├── text/                              # 68 pure text transcriptions (UTF-8 Devanagari)
│   │   ├── Chanda_Mama_01.txt
│   │   └── ...
│   ├── json/                              # 68 metadata files with polygon coordinates, baselines & confidences
│   ├── visualized/                        # 136 high-resolution visual comparison panels
│   │   ├── Chanda_Mama_XX_comparison.jpg  # Side-by-side: Original Scan vs. Recognized Text
│   │   └── Chanda_Mama_XX_overlay.jpg     # Direct overlay with detected text polygon boundaries
│   ├── viewer.html                        # Interactive web application for browsing all 68 pages
│   └── combined_transcription_first_68_pages.txt  # Complete continuous transcript of the whole book
├── CHANDA_MAMA_ALL_IN_ONE_A3_VISUAL.jpg   # High-resolution (300 DPI) master A3 visual audit poster
└── CHANDA_MAMA_ALL_IN_ONE_A3_VISUAL.png   # Lossless master A3 visual comparison grid
`

---

## 🔍 Visual OCR Viewer

Open ocr_output/viewer.html in any web browser to:
- Browse all **68 pages** via an intuitive page navigation ribbon.
- Switch between **Side-by-Side Comparison**, **Line Polygon Overlays**, and **Original Scans**.
- Inspect line-by-line Sanskrit transcription with model confidence scores.
- Copy transcribed text for any page with one click.

---

## 📊 Summary Metrics

- **Total Pages Processed**: 68 / 68 (100% Complete)
- **Script**: Devanagari (Sanskrit / Awadhi)
- **Pipeline Architecture**: Kraken BLLA Topline Segmenter + PP-OCRv6 Line Recognizer
- **Export Resolution**: Print-Ready A3 (4960 × 3508 @ 300 DPI)

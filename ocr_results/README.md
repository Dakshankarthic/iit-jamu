# Column-aware OCR results

These are new **Tesseract 5.5.0** results for all 68 Chanda Mama scans. **Surya has not been run.** Original scans and the original OCR dataset are unchanged.

## Results

- [OCR review index](tesseract/index.html): source scans alongside new OCR text.
- [Combined 68-page transcription](tesseract/combined_transcription_68_pages.txt).
- `tesseract/text/`: 68 UTF-8 transcriptions.
- `tesseract/json/`: 68 files with text, block reading order, source-coordinate line boxes, confidence, warnings and engine metadata.
- `tesseract/run-summary.json`: execution outcomes and model checksum.
- `segmentation/`: 53 draft layouts (49 narrative two-column pages and 4 alternating-panel pages), JSON and annotated HTML.
- [Visual gallery, pages 1–40](visual_pages_01_40/gallery.html).
- [Visual PDF, pages 1–40](visual_pages_01_40/OCR_Visual_Pages_01-40.pdf).
- [40 comparison images ZIP](visual_pages_01_40/OCR_Visual_Pages_01-40.zip).
- [OCR text/JSON ZIP, all 68 pages](OCR_Text_JSON_68_Pages.zip).

The HTML viewers reference the existing `image/` directory. Serve the repository root with `python3 -m http.server 8000` to review them locally; GitHub does not render interactive HTML directly.

## Quality and scope

All 68 images were processed. On 53 pages, columns or comic panels were recognized separately, in reading order. Other pages used automatic layout. Pages 1 and 4 required sparse-text detection and have low-confidence results, including potential false characters from artwork.

**These outputs are not proofread or ground truth.** Spelling errors remain. The manually selected text blocks and pixel-based line segmentation are drafts; some full-width headings and marginal text may be omitted. Their geometry has not been exhaustively validated. Successful OCR execution does not establish accurate or complete transcription. Confidence scores across OCR engines are not directly comparable.

The review visuals show newly recognized Tesseract line boxes, rather than the preliminary pixel-based line boxes. Blue/orange outlines distinguish columns or panel groups.

## Reproduce

Requires Python 3, Pillow, NumPy and Tesseract 5.5.0. Sanskrit recognition uses the official `tessdata_best` model; pages 3, 65 and 66 also use the installed English model. Downloaded models belong in ignored `.cache/tessdata/`; they are not committed.

From the repository root:

```sh
mkdir -p ocr_results/.cache/tessdata
curl --fail --location --output ocr_results/.cache/tessdata/san.traineddata https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/san.traineddata
cp /usr/share/tesseract-ocr/5/tessdata/eng.traineddata ocr_results/.cache/tessdata/eng.traineddata
```

Expected Sanskrit model SHA-256: `5fbc152e7946b3b8201a2a557864bd23b521db4102b521f3e95169c82c5d0b0d`. Verify this matches before running; a changed upstream model can change results.

```sh
python3 ocr_results/scripts/segment_columns.py
python3 ocr_results/scripts/run_ocr.py --workers 4
```

`run_ocr.py --pages 45 --workers 1` runs a subset, but replaces the run-summary file with that subset's execution outcomes. The visual PDF/JPEG exports are saved artifacts, not recreated by the OCR command.

Temporary contact sheets, debug logs, browser caches and downloaded model weights are omitted from this commit.

# New OCR results

All 68 source scans were processed using Tesseract 5.5.0. The Sanskrit model was fetched from the official tesseract-ocr/tessdata_best repository over verified HTTPS. English also used on pages 3, 65, and 66.

53 pages use independently recognized columns or comic-panel text blocks. The remaining 15 pages use automatic page layout. Column reading order is left top-to-bottom, then right top-to-bottom. Comic panels follow panel order.

text/: one UTF-8 transcription per page.
json/: engine metadata, source-coordinate word-group line boxes, confidence and text, organized by column/panel.
pages/: source image and new OCR text for review; these HTML files use source images from the existing checkout.
combined_transcription_68_pages.txt: combined text in page order.
run-summary.json: execution outcomes and model SHA-256.

These are machine transcriptions, not proofread text. OCR contains spelling errors. Hand-selected text blocks may omit full-width headings and marginal text. Covers, illustrations and tables require special review; successful execution does not establish transcription accuracy or complete text coverage.

Reproduce with: python3 ocr_results/scripts/run_ocr.py --workers 4
Original repository files were not changed.

Pages 1 and 4 returned no text with automatic page segmentation, then were processed using sparse-text mode (PSM 11). Their output has low confidence and can include false text detected in artwork; manual review is required.

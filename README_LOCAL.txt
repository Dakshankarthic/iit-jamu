CHANDA MAMA — LOCAL WINDOWS PACKAGE

This package contains all 68 original scans, the original OCR dataset, the new
Tesseract results, visual comparisons, the original A3 posters, and the latest
PowerPoint. No cloud connection is needed to view these saved files.

QUICK START: VIEW THE PROJECT
1. Extract the ZIP, for example to C:\OCR\Chanda_Mama_Local.
2. Install Python 3.12 or newer if it is not already on your Windows PC.
   Official download: https://www.python.org/downloads/windows/
3. Double-click START_VIEWER.cmd. Keep its terminal window open.
4. The browser opens LOCAL_HOME.html with links to scans and OCR results.
   If it opens before the server is ready, refresh the page.
   If port 8000 is busy, close the previous viewer server you started and retry.
5. Press Ctrl+C in the terminal to stop the server.

RUN NEW SURYA OCR LOCALLY (WINDOWS + WSL2)
Surya has been installed and its CPU backend checked in the cloud, but recognition
has NOT run because the cloud network blocked its Hugging Face model download.
The package contains no Surya recognition results or model weights. Your local
machine still needs to install Surya and download its public model over the
Internet. An NVIDIA GPU is not required for this CPU setup. Allow several GB of
free space for WSL, Python dependencies and model files. CPU recognition is slower
than GPU recognition. The scripts target Intel/AMD x64 PCs.

1. Open PowerShell as Administrator and run:
   wsl --install -d Ubuntu-24.04
   Restart Windows if prompted and complete Ubuntu's account setup.
   Existing WSL2 Ubuntu 24.04 or newer installations can be reused.

2. Open Ubuntu and install prerequisites:
   sudo apt-get update
   sudo apt-get install -y python3-venv python3-pip libgomp1

3. In Ubuntu, go to the extracted project folder, for example:
   cd /mnt/c/OCR/Chanda_Mama_Local
   Replace that path if you extracted elsewhere. Quote paths containing spaces.

4. Install the pinned Surya 0.22.1 CPU environment:
   bash local_tools/setup_surya_wsl.sh
   Python packages/model caches are kept in Ubuntu under:
   ~/.local/share/chanda-mama-surya
   The official llama.cpp binary's SHA-256 is checked before use.

5. Check the setup without downloading or running the OCR model:
   bash local_tools/run_surya_wsl.sh check

6. Run five representative pages: 3, 15, 35, 39 and 45:
   bash local_tools/run_surya_wsl.sh pilot
   First use downloads the public model from Hugging Face. No paid API key is
   required. Output: surya_results/pilot/ (including results.json and visuals).
   Review spelling, missing text and column/panel order before a full run.

7. Run all 68 pages:
   bash local_tools/run_surya_wsl.sh all
   Output: surya_results/all_pages/.

8. The --keep_server option keeps llama-server running to avoid repeated loading.
   Stop only that Surya server when you finish. To find its PID in Ubuntu:
   pgrep -af llama-server
   Identify the process using the chanda-mama-surya model, then: kill <PID>

RESULTS AND LIMITATIONS
- ocr_results/tesseract/: 68 new machine transcriptions and JSON metadata.
- ocr_results/segmentation/: 53 draft column/panel layouts.
- ocr_results/visual_pages_01_40/: 40 visual comparison pages, PDF and ZIP.
- presentation.pptx: latest plain presentation with five input/output examples
  and the original A3 poster overview/detail.
- CHANDA_MAMA_ALL_IN_ONE_A3_VISUAL.jpg/.png: original A3 poster for pages 1–20;
  it is not a new Surya output.
- OCR text is unproofread. Some headings/marginal text may be missed. Tesseract
  pages 1 and 4 have particularly poor results.

LOCAL TEST STATUS
The viewer files and references were verified in the cloud. The Surya package,
CPU backend and helper-script checks were verified on Linux. The Windows .cmd
launcher and WSL installation cannot be executed on your physical PC from this
session; they must be run there. Full Surya OCR remains unverified until model
access and inference succeed on your machine.

The ZIP excludes Git history, Python environments, downloaded model weights,
browser caches, debug contact sheets and temporary logs. It does not delete or
move anything out of the cloud. The saved files can be viewed offline after
extraction; new Surya OCR needs Internet access for its initial model download.

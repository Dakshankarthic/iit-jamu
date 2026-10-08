#!/usr/bin/env bash
set -euo pipefail
if [[ "$(uname -m)" != "x86_64" ]]; then
  echo 'This installer targets Intel/AMD x64. An ARM machine needs a matching llama.cpp binary.' >&2
  exit 1
fi
task_runtime_root="${LOCAL_OCR_RUNTIME:-$HOME/.local/share/chanda-mama-surya}"
mkdir -p "$task_runtime_root"
python3 -c 'import sys; assert sys.version_info >= (3,12), "Use Ubuntu 24.04 or newer with Python 3.12+"'
python3 -m venv "$task_runtime_root/.venv"
"$task_runtime_root/.venv/bin/python" -m pip install 'torch==2.14.1+cpu' 'torchvision==0.29.1+cpu' --index-url https://download.pytorch.org/whl/cpu
"$task_runtime_root/.venv/bin/python" -m pip install 'surya-ocr==0.22.1'
"$task_runtime_root/.venv/bin/python" - "$task_runtime_root" <<'PY'
import sys,hashlib,tarfile
from pathlib import Path
from urllib.request import urlopen
root=Path(sys.argv[1]);archive=root/'llama-b11429.tar.gz'
url='https://github.com/ggml-org/llama.cpp/releases/download/b11429/llama-b11429-bin-ubuntu-x64.tar.gz'
sha='f6d25dde8f51133143d1453da4fd5f73b145127177612a283bf7995957af3392'
if not archive.exists() or hashlib.sha256(archive.read_bytes()).hexdigest()!=sha:
 with urlopen(url,timeout=60) as response,archive.open('wb') as out:
  while data:=response.read(1024*1024):out.write(data)
assert hashlib.sha256(archive.read_bytes()).hexdigest()==sha,'Binary checksum mismatch'
dest=root/'llama';dest.mkdir(exist_ok=True)
with tarfile.open(archive) as data:data.extractall(dest,filter='data')
PY
"$task_runtime_root/llama/llama-b11429/llama-server" --version
"$task_runtime_root/.venv/bin/surya_ocr" --help
printf '\nInstalled Surya in %s\nThe OCR model will download on first use.\n' "$task_runtime_root"

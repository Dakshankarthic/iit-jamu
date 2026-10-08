#!/usr/bin/env bash
set -euo pipefail
task_project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
task_runtime_root="${LOCAL_OCR_RUNTIME:-$HOME/.local/share/chanda-mama-surya}"
if [[ ! -x "$task_runtime_root/.venv/bin/surya_ocr" ]]; then
 echo 'Run bash local_tools/setup_surya_wsl.sh first.' >&2
 exit 1
fi
export HF_HOME="$task_runtime_root/cache/huggingface"
export XDG_CACHE_HOME="$task_runtime_root/cache"
export MODEL_CACHE_DIR="$task_runtime_root/cache/datalab/models"
export SURYA_INFERENCE_BACKEND=llamacpp
export SURYA_INFERENCE_PARALLEL=1
export SURYA_INFERENCE_CTX_SIZE=16384
export LLAMA_CPP_BINARY="$task_runtime_root/llama/llama-b11429/llama-server"
export LLAMA_CPP_NGL=0
task_threads="$(nproc)"
if (( task_threads > 8 )); then task_threads=8; fi
export LLAMA_CPP_EXTRA_ARGS="--threads $task_threads --threads-batch $task_threads"
export OMP_NUM_THREADS="$task_threads"
case "${1:-pilot}" in
 pilot|check)
  task_input="$task_runtime_root/samples"
  mkdir -p "$task_input"
  python3 - "$task_project_root" "$task_input" <<'PY'
import sys
from pathlib import Path
root=Path(sys.argv[1]);samples=Path(sys.argv[2])
for n in [3,15,35,39,45]:
 source=root/'image'/f'Chanda_Mama_{n:02d}.jpg'
 assert source.is_file(),f'Missing scan: {source}'
 target=samples/source.name
 if target.is_symlink() or target.exists():
  assert target.resolve()==source.resolve(),f'Existing sample points elsewhere: {target}'
 else:target.symlink_to(source)
print('Verified 5 pilot images.')
PY
  task_output="$task_project_root/surya_results/pilot"
  ;;
 all)
  task_input="$task_project_root/image"
  task_output="$task_project_root/surya_results/all_pages"
  ;;
 *) echo 'Usage: bash local_tools/run_surya_wsl.sh [pilot|all|check]' >&2;exit 1;;
esac
if [[ "${1:-pilot}" == "check" ]]; then
 "$LLAMA_CPP_BINARY" --version
 "$task_runtime_root/.venv/bin/surya_ocr" --help
 exit 0
fi
mkdir -p "$task_output"
exec "$task_runtime_root/.venv/bin/surya_ocr" "$task_input" --images --output_dir "$task_output" --keep_server

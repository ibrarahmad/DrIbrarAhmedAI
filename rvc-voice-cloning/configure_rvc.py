#!/usr/bin/env python3
"""Configure companion config.yaml for official RVC library (+ optional WebUI).

Upstream library (required for convert):
  https://github.com/RVC-Project/Retrieval-based-Voice-Conversion
  pip install git+https://github.com/RVC-Project/Retrieval-based-Voice-Conversion
  rvc init && rvc dlmodel
  rvc infer -m model.pth -i in.wav -o out.wav

WebUI (recommended for TRAINING):
  https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

from _lib import ROOT, load_config, which


def _find_infer_cli(webui: Path) -> Path | None:
    for rel in ("tools/infer_cli.py", "infer_cli.py", "tools/infer-web.py"):
        p = webui / rel
        if p.is_file():
            return p
    return None


def _first_pth(model_dir: Path) -> Path | None:
    return next(iter(sorted(model_dir.glob("*.pth"))), None)


def _first_index(model_dir: Path) -> Path | None:
    return next(iter(sorted(model_dir.glob("*.index"))), None)


def _library_installed() -> bool:
    return importlib.util.find_spec("rvc") is not None or which("rvc") is not None


def _set_key(src: str, key: str, value: str) -> str:
    pat = re.compile(rf"(?m)^{re.escape(key)}:\s*.*$")
    line = f"{key}: {value}"
    if pat.search(src):
        return pat.sub(line, src)
    return src.rstrip() + f"\n{line}\n"


def write_config(
    root: Path,
    *,
    webui: Path | None,
    rvc_lib: Path | None,
    device: str,
    f0method: str,
    prefer_library: bool = True,
) -> Path:
    cfg_path = root / "config.yaml"
    text = cfg_path.read_text(encoding="utf-8") if cfg_path.is_file() else ""

    model_dir = root / "models" / "rvc"
    model_dir.mkdir(parents=True, exist_ok=True)
    pth = _first_pth(model_dir)
    index = _first_index(model_dir)

    # Always wire the bridge - it prefers library API/CLI, then WebUI.
    convert_cmd = (
        f'"python3 {root / "rvc_infer_bridge.py"} '
        f'{{base_wav}} {{out_wav}} {{model_dir}}"'
    )
    webui_root = f'"{webui}"' if webui and webui.is_dir() else '""'
    backend = "library" if prefer_library or _library_installed() else "webui"
    notes: list[str] = []

    if _library_installed():
        notes.append("official RVC library detected (pip / rvc CLI)")
    else:
        notes.append(
            "RVC library not importable yet - run bash setup_rvc.sh "
            "(pip install git+https://github.com/RVC-Project/...)"
        )

    if webui and webui.is_dir():
        cli = _find_infer_cli(webui)
        notes.append(f"WebUI train/infer fallback: {webui}")
        if cli:
            notes.append(f"WebUI infer_cli: {cli}")
    elif rvc_lib and rvc_lib.is_dir():
        notes.append(f"RVC source tree noted: {rvc_lib}")

    text = _set_key(text or "# auto-configured\n", "rvc_model_dir", '"models/rvc"')
    text = _set_key(text, "rvc_webui_root", webui_root)
    text = _set_key(text, "rvc_convert_command", convert_cmd)
    text = _set_key(text, "rvc_backend", f'"{backend}"')
    text = _set_key(text, "rvc_device", f'"{device}"')
    text = _set_key(text, "rvc_f0method", f'"{f0method}"')

    cfg_path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")

    print("WROTE", cfg_path.relative_to(root))
    print(f"  rvc_backend:        {backend}")
    print(f"  rvc_webui_root:     {webui_root}")
    print(f"  rvc_convert_command:{convert_cmd}")
    print(f"  rvc_device:         {device}")
    print(f"  rvc_f0method:       {f0method}")
    print(f"  models/rvc pth:     {pth.name if pth else 'MISSING - train then copy .pth here'}")
    print(f"  models/rvc index:   {index.name if index else 'optional .index'}")
    for n in notes:
        print(f"  note: {n}")
    print("")
    print("VERIFY:")
    print("  python configure_rvc.py --check")
    print("  python demo_complete.py")
    return cfg_path


def check(root: Path) -> int:
    cfg = load_config(root)
    webui = Path(str(cfg.get("rvc_webui_root") or "")).expanduser()
    cmd = str(cfg.get("rvc_convert_command") or "").strip()
    backend = str(cfg.get("rvc_backend") or "library")
    model_dir = root / str(cfg.get("rvc_model_dir") or "models/rvc")
    pth = _first_pth(model_dir)
    index = _first_index(model_dir)
    lib_ok = _library_installed()
    # Must match setup_rvc.sh / video Slide 4
    webui_pin = "c1e005f0e226a3c2a10adfc8a9be03a6944506d0"

    print("CONFIG CHECK")
    print(f"  ffmpeg:             {'yes' if which('ffmpeg') else 'NO - brew install ffmpeg'}")
    print(f"  rvc library:        {'yes' if lib_ok else 'NO - bash setup_rvc.sh'}")
    print(f"  rvc CLI:            {which('rvc') or 'not on PATH'}")
    print(f"  rvc_backend:        {backend}")
    print(f"  rvc_webui_root:     {webui if webui.as_posix() not in {'', '.'} else 'NOT SET (optional for train)'}")
    if webui.as_posix() not in {"", "."}:
        print(f"  webui exists:       {webui.is_dir()}")
        cli = _find_infer_cli(webui) if webui.is_dir() else None
        print(f"  infer_cli:          {cli or 'missing'}")
        head = ""
        git_dir = webui / ".git"
        if webui.is_dir() and git_dir.exists():
            import subprocess

            try:
                head = subprocess.check_output(
                    ["git", "-C", str(webui), "rev-parse", "HEAD"],
                    text=True,
                ).strip()
            except Exception:
                head = ""
        if head:
            ok = head == webui_pin
            print(f"  webui pin:          {head[:12]}{' OK' if ok else ' MISMATCH — re-run bash setup_rvc.sh'}")
            if not ok:
                print(f"  expected pin:       {webui_pin[:12]}")
        req = webui / "requirements.txt"
        dl = webui / "tools" / "download_models.py"
        print(f"  webui requirements: {'yes' if req.is_file() else 'MISSING'}")
        print(f"  download_models.py: {'yes' if dl.is_file() else 'MISSING'}")
    print(f"  rvc_convert_command:{'SET' if cmd else 'EMPTY'}")
    print(f"  speaker.pth:        {pth.name if pth else 'MISSING'}")
    print(f"  speaker.index:      {index.name if index else 'none'}")
    print(f"  .env / assets:      {(root / '.env').is_file()} / {(root / 'assets').is_dir()}")

    if not which("ffmpeg"):
        print("  STATUS: FAIL - install ffmpeg")
        return 1
    if not cmd:
        print("  STATUS: PARTIAL - run: python configure_rvc.py --prefer-library")
        return 1
    if not lib_ok and not (webui.is_dir() and _find_infer_cli(webui)):
        print("  STATUS: CONFIGURED - next: bash setup_rvc.sh (install RVC library)")
        print("           then train → copy .pth → models/rvc/")
        return 0
    if not pth:
        print("  STATUS: CONFIGURED - train (WebUI) → copy .pth → models/rvc/")
        print("           guide: docs/TRAIN_WEBUI.md")
        print("           then: python next_step.py")
        return 0
    print("  STATUS: weights ready")
    print("  NEXT: python infer.py --text-file scripts/clone_prove.txt --out output/clone_prove.wav")
    print("        python play_clone.py --wav output/clone_prove.wav")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--webui",
        type=Path,
        default=None,
        help="Path to Retrieval-based-Voice-Conversion-WebUI (train UI)",
    )
    parser.add_argument(
        "--rvc-lib",
        type=Path,
        default=None,
        help="Optional path to RVC library source clone",
    )
    parser.add_argument(
        "--prefer-library",
        action="store_true",
        default=True,
        help="Prefer official pip library for convert (default)",
    )
    parser.add_argument("--prefer-webui", action="store_true", help="Prefer WebUI convert backend")
    parser.add_argument("--device", type=str, default="cpu")
    parser.add_argument("--f0method", type=str, default="rmvpe")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.check:
        return check(args.root)

    parent = args.root.parent
    webui = args.webui
    if webui is None:
        guess = parent / "Retrieval-based-Voice-Conversion-WebUI"
        webui = guess if guess.is_dir() else None
    rvc_lib = args.rvc_lib
    if rvc_lib is None:
        guess = parent / "Retrieval-based-Voice-Conversion"
        rvc_lib = guess if guess.is_dir() else None

    prefer_library = not args.prefer_webui
    # Always write config - library may be installed via pip without local clone.
    if webui is None and rvc_lib is None and not _library_installed():
        print("RVC not found yet - writing library-first convert command anyway.")
        print("Next: bash setup_rvc.sh")
        print("  https://github.com/RVC-Project/Retrieval-based-Voice-Conversion")

    write_config(
        args.root,
        webui=webui,
        rvc_lib=rvc_lib,
        device=args.device,
        f0method=args.f0method,
        prefer_library=prefer_library,
    )
    return check(args.root)


if __name__ == "__main__":
    sys.exit(main())

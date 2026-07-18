#!/usr/bin/env python3
"""Configure companion config.yaml to use a local RVC / WebUI install.

Upstream library:
  https://github.com/RVC-Project/Retrieval-based-Voice-Conversion
Training / infer UI (recommended):
  https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _lib import ROOT, load_config, which


DEFAULT_WEBUI_CMD = (
    'python "{webui}/tools/infer_cli.py" '
    "--input_path {base_wav} --opt_path {out_wav} "
    "--model_name {{model}} --index_path {{index}} "
    "--f0method rmvpe --device cpu"
)


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


def write_config(
    root: Path,
    *,
    webui: Path | None,
    rvc_lib: Path | None,
    device: str,
    f0method: str,
) -> Path:
    cfg_path = root / "config.yaml"
    text = cfg_path.read_text(encoding="utf-8") if cfg_path.is_file() else ""

    model_dir = root / "models" / "rvc"
    model_dir.mkdir(parents=True, exist_ok=True)
    pth = _first_pth(model_dir)
    index = _first_index(model_dir)

    convert_cmd = '""'
    webui_root = '""'
    notes: list[str] = []

    if webui and webui.is_dir():
        webui_root = f'"{webui}"'
        cli = _find_infer_cli(webui)
        if cli:
            # Keep placeholders for infer.py template: {base_wav} {out_wav} {model_dir}
            # Bridge-style: run a small helper that picks *.pth from model_dir
            convert_cmd = (
                f'"python {root / "rvc_infer_bridge.py"} '
                f'{{base_wav}} {{out_wav}} {{model_dir}}"'
            )
            notes.append(f"WebUI infer CLI found: {cli}")
        else:
            notes.append(
                f"WebUI at {webui} but infer_cli.py not found — "
                "set rvc_convert_command manually after WebUI install."
            )
            convert_cmd = '""'
    elif rvc_lib and rvc_lib.is_dir():
        # Library-style: prefer `rvc infer` if on PATH after pip install
        convert_cmd = (
            '"rvc infer -m {model_dir}/*.pth -i {base_wav} -o {out_wav}"'
        )
        notes.append(f"RVC library path noted: {rvc_lib} (adjust CLI if needed)")

    # Patch YAML keys (simple replace / append)
    def set_key(src: str, key: str, value: str) -> str:
        import re

        pat = re.compile(rf"(?m)^{re.escape(key)}:\s*.*$")
        line = f"{key}: {value}"
        if pat.search(src):
            return pat.sub(line, src)
        return src.rstrip() + f"\n{line}\n"

    text = set_key(text or "# auto-configured\n", "rvc_model_dir", '"models/rvc"')
    text = set_key(text, "rvc_webui_root", webui_root)
    text = set_key(text, "rvc_convert_command", convert_cmd)
    text = set_key(text, "rvc_device", f'"{device}"')
    text = set_key(text, "rvc_f0method", f'"{f0method}"')

    cfg_path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")

    print("WROTE", cfg_path.relative_to(root))
    print(f"  rvc_webui_root:     {webui_root}")
    print(f"  rvc_convert_command:{convert_cmd}")
    print(f"  rvc_device:         {device}")
    print(f"  rvc_f0method:       {f0method}")
    print(f"  models/rvc pth:     {pth.name if pth else 'MISSING — train then copy .pth here'}")
    print(f"  models/rvc index:   {index.name if index else 'optional .index'}")
    for n in notes:
        print(f"  note: {n}")
    print("")
    print("VERIFY:")
    print("  python configure_rvc.py --check")
    return cfg_path


def check(root: Path) -> int:
    cfg = load_config(root)
    webui = Path(str(cfg.get("rvc_webui_root") or "")).expanduser()
    cmd = str(cfg.get("rvc_convert_command") or "").strip()
    model_dir = root / str(cfg.get("rvc_model_dir") or "models/rvc")
    pth = _first_pth(model_dir)
    index = _first_index(model_dir)

    print("CONFIG CHECK")
    print(f"  ffmpeg:             {'yes' if which('ffmpeg') else 'NO — brew install ffmpeg'}")
    print(f"  rvc_webui_root:     {webui if webui.as_posix() not in {'', '.'} else 'NOT SET'}")
    if webui.as_posix() not in {"", "."}:
        print(f"  webui exists:       {webui.is_dir()}")
        cli = _find_infer_cli(webui) if webui.is_dir() else None
        print(f"  infer_cli:          {cli or 'missing'}")
    print(f"  rvc_convert_command:{'SET' if cmd else 'EMPTY (Edge TTS baseline only)'}")
    print(f"  speaker.pth:        {pth.name if pth else 'MISSING'}")
    print(f"  speaker.index:      {index.name if index else 'none'}")

    ok = True
    if not which("ffmpeg"):
        ok = False
    if not cmd:
        print("  STATUS: PARTIAL — build/configure RVC, then re-run configure_rvc.py")
        ok = False
    elif not pth:
        print("  STATUS: CONFIGURED — next train in WebUI and copy .pth into models/rvc/")
    else:
        print("  STATUS: READY — python infer.py --text-file scripts/sample_line.txt")
    return 0 if ok or cmd else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--webui",
        type=Path,
        default=None,
        help="Path to Retrieval-based-Voice-Conversion-WebUI clone",
    )
    parser.add_argument(
        "--rvc-lib",
        type=Path,
        default=None,
        help="Path to Retrieval-based-Voice-Conversion library clone",
    )
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

    if webui is None and rvc_lib is None:
        print("RVC not found nearby.")
        print("Build it first:")
        print("  bash setup_rvc.sh")
        print("Or:")
        print("  git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion")
        print("  git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI")
        print("Then:")
        print('  python configure_rvc.py --webui /path/to/Retrieval-based-Voice-Conversion-WebUI')
        return 1

    write_config(
        args.root,
        webui=webui,
        rvc_lib=rvc_lib,
        device=args.device,
        f0method=args.f0method,
    )
    return check(args.root)


if __name__ == "__main__":
    sys.exit(main())

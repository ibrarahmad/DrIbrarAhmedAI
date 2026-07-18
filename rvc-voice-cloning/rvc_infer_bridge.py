#!/usr/bin/env python3
"""Bridge: companion infer → RVC-WebUI infer_cli (configured by configure_rvc.py)."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from _lib import ROOT, find_rvc_weights, load_config


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) < 3:
        print("Usage: rvc_infer_bridge.py <base_wav> <out_wav> <model_dir>")
        return 2
    base_wav, out_wav, model_dir = map(Path, argv[:3])
    cfg = load_config(ROOT)
    webui = Path(str(cfg.get("rvc_webui_root") or "")).expanduser()
    if not webui.is_dir():
        print(f"rvc_webui_root not set or missing: {webui}")
        print("Run: bash setup_rvc.sh && python configure_rvc.py --webui /path/to/WebUI")
        return 1

    cli = webui / "tools" / "infer_cli.py"
    if not cli.is_file():
        # older layouts
        for rel in ("infer_cli.py", "tools/infer-web.py"):
            alt = webui / rel
            if alt.is_file():
                cli = alt
                break
    if not cli.is_file():
        print(f"infer_cli.py not found under {webui}")
        return 1

    model_dir = Path(model_dir)
    pth, index = find_rvc_weights(model_dir)
    if pth is None:
        print(f"No *.pth in {model_dir} — train in WebUI then copy weights here")
        return 1

    device = str(cfg.get("rvc_device") or os.environ.get("RVC_DEVICE") or "cpu")
    f0method = str(cfg.get("rvc_f0method") or os.environ.get("RVC_F0METHOD") or "rmvpe")

    # WebUI CLI flags vary by version — try the common infer_cli interface.
    cmd = [
        sys.executable,
        str(cli),
        "--input_path",
        str(base_wav),
        "--opt_path",
        str(out_wav),
        "--model_name",
        pth.name,
        "--f0method",
        f0method,
        "--device",
        device,
    ]
    if index is not None:
        cmd.extend(["--index_path", str(index)])

    env = os.environ.copy()
    env["RVC_ROOT"] = str(webui)
    print("[rvc-bridge]", " ".join(cmd))
    # Run with cwd=webui so relative pretrained/asset paths resolve.
    proc = subprocess.run(cmd, cwd=str(webui), env=env)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())

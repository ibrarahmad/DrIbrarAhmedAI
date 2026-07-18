#!/usr/bin/env python3
"""
Convert audio with the official RVC library:
  https://github.com/RVC-Project/Retrieval-based-Voice-Conversion

Primary:  Python API  (rvc.modules.vc.modules.VC)
Fallback: CLI         (rvc infer -m … -i … -o …)
Optional: WebUI       tools/infer_cli.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from _lib import ROOT, find_rvc_weights, load_config, preset_knobs, which


def _run_library_api(base_wav: Path, out_wav: Path, pth: Path, index: Path | None, knobs: dict) -> bool:
    try:
        from dotenv import load_dotenv
        from scipy.io import wavfile
        from rvc.modules.vc.modules import VC
    except Exception as exc:
        print(f"[rvc-lib] API import failed: {exc}")
        return False

    env_path = ROOT / ".env"
    if env_path.is_file():
        load_dotenv(env_path)
    else:
        load_dotenv()

    print(f"[rvc-lib] API  model={pth.name} index={index.name if index else 'none'}")
    vc = VC()
    vc.get_vc(str(pth))
    # Official README: sid=1, Path input; knobs match rvc infer CLI
    kwargs = {
        "f0_up_key": int(knobs.get("f0up_key") or 0),
        "f0_method": str(knobs.get("f0method") or "rmvpe"),
        "index_rate": float(knobs.get("index_rate") or 0.75),
        "filter_radius": int(knobs.get("filter_radius") or 3),
        "protect": float(knobs.get("protect") or 0.33),
    }
    if index is not None:
        kwargs["index_file"] = index
    tgt_sr, audio_opt, _times, _ = vc.vc_inference(1, Path(base_wav), **kwargs)
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(str(out_wav), tgt_sr, audio_opt)
    print(f"[rvc-lib] wrote {out_wav}")
    return out_wav.is_file()


def _run_library_cli(base_wav: Path, out_wav: Path, pth: Path, index: Path | None, knobs: dict) -> bool:
    rvc_bin = which("rvc")
    if not rvc_bin:
        # poetry script may be available as python -m
        cmd_base = [sys.executable, "-m", "rvc.wrapper.cli.cli", "infer"]
    else:
        cmd_base = [rvc_bin, "infer"]

    cmd = [
        *cmd_base,
        "-m",
        str(pth),
        "-i",
        str(base_wav),
        "-o",
        str(out_wav),
        "-fm",
        str(knobs.get("f0method") or "rmvpe"),
        "-fu",
        str(int(knobs.get("f0up_key") or 0)),
        "-ir",
        str(float(knobs.get("index_rate") or 0.8)),
        "-fr",
        str(int(knobs.get("filter_radius") or 3)),
        "-p",
        str(float(knobs.get("protect") or 0.4)),
    ]
    if index is not None:
        cmd.extend(["-if", str(index)])

    print("[rvc-lib] CLI ", " ".join(cmd))
    env = os.environ.copy()
    if (ROOT / ".env").is_file():
        env["DOTENV_PATH"] = str(ROOT / ".env")
    proc = subprocess.run(cmd, cwd=str(ROOT), env=env)
    return proc.returncode == 0 and out_wav.is_file()


def _run_webui(base_wav: Path, out_wav: Path, model_dir: Path, pth: Path, index: Path | None, knobs: dict, webui: Path) -> bool:
    infer_cli = webui / "tools" / "infer_cli.py"
    if not infer_cli.is_file():
        print(f"[rvc-webui] missing {infer_cli}")
        return False

    weights = webui / "assets" / "weights"
    weights.mkdir(parents=True, exist_ok=True)
    dest_pth = weights / pth.name
    if dest_pth.resolve() != pth.resolve():
        shutil.copy2(pth, dest_pth)
    index_arg = None
    if index is not None:
        dest_idx = weights / index.name
        if dest_idx.resolve() != index.resolve():
            shutil.copy2(index, dest_idx)
        index_arg = str(dest_idx)

    device = str(load_config(ROOT).get("rvc_device") or "cpu")
    cmd = [
        sys.executable,
        str(infer_cli),
        "--input_path",
        str(base_wav.resolve()),
        "--opt_path",
        str(out_wav.resolve()),
        "--model_name",
        pth.name,
        "--f0method",
        str(knobs.get("f0method") or "rmvpe"),
        "--device",
        device,
        "--index_rate",
        str(float(knobs.get("index_rate") or 0.8)),
        "--filter_radius",
        str(int(knobs.get("filter_radius") or 3)),
        "--protect",
        str(float(knobs.get("protect") or 0.4)),
        "--f0up_key",
        str(int(knobs.get("f0up_key") or 0)),
    ]
    if index_arg:
        cmd.extend(["--index_path", index_arg])

    print("[rvc-webui]", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(webui))
    return proc.returncode == 0 and out_wav.is_file()


def convert(base_wav: Path, out_wav: Path, model_dir: Path | None = None) -> str:
    """Run RVC convert. Returns backend name used."""
    cfg = load_config(ROOT)
    knobs = preset_knobs(cfg)
    model_dir = Path(model_dir or (ROOT / str(cfg.get("rvc_model_dir") or "models/rvc")))
    pth, index = find_rvc_weights(model_dir)
    if pth is None:
        raise SystemExit(
            f"No *.pth in {model_dir}. Train (WebUI) then copy speaker.pth here.\n"
            "See docs/RVC_SETUP.md"
        )

    prefer = str(cfg.get("rvc_backend") or "library").lower()
    webui = Path(str(cfg.get("rvc_webui_root") or "")).expanduser()

    order = []
    if prefer == "webui":
        order = ["webui", "library_api", "library_cli"]
    else:
        order = ["library_api", "library_cli", "webui"]

    for backend in order:
        ok = False
        if backend == "library_api":
            ok = _run_library_api(base_wav, out_wav, pth, index, knobs)
        elif backend == "library_cli":
            ok = _run_library_cli(base_wav, out_wav, pth, index, knobs)
        elif backend == "webui" and webui.is_dir():
            ok = _run_webui(base_wav, out_wav, model_dir, pth, index, knobs, webui)
        if ok:
            return backend

    raise SystemExit(
        "RVC convert failed on all backends.\n"
        "1) pip install git+https://github.com/RVC-Project/Retrieval-based-Voice-Conversion.git@develop\n"
        "2) bash setup_rvc.sh && python configure_rvc.py --check\n"
        "3) Ensure models/rvc/*.pth exists"
    )


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) < 3:
        print("Usage: rvc_infer_bridge.py <base_wav> <out_wav> <model_dir>")
        return 2
    base_wav, out_wav, model_dir = map(Path, argv[:3])
    backend = convert(base_wav, out_wav, model_dir)
    print(f"[rvc] backend={backend} OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from pathlib import Path
import webbrowser

import agentpy as ap
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.animation import writers


def _is_notebook_runtime() -> bool:
    try:
        from IPython.core.getipython import get_ipython

        return get_ipython() is not None
    except Exception:
        return False


class AnimationRenderer:
    def __init__(self, mode: str = "browser", output_dir: Path | None = None):
        self.mode = (mode or "browser").strip().lower()
        self.output_dir = output_dir
        self.runtime_is_notebook = _is_notebook_runtime()
        self._counter = 0
        self._active_animations = []
        self._artifacts: list[dict[str, str]] = []
        self._ffmpeg_available = writers.is_available("ffmpeg")
        self._configure_backend()

    def _configure_backend(self) -> None:
        if self.runtime_is_notebook:
            return
        if self.mode in {"off", "none", "0", "false", "browser", "html"}:
            return

        for backend in ("TkAgg", "QtAgg"):
            try:
                matplotlib.use(backend, force=True)
                return
            except Exception:
                continue

    def _save_animation_artifact(self, animation, scenario_name: str) -> None:
        if self.output_dir is None:
            return

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._counter += 1
        safe_name = scenario_name.replace(" ", "_").replace("/", "_").lower()
        prefix = f"{self._counter:02d}_{safe_name}"

        # Prefer mp4 video with controls; fall back to gif if ffmpeg is unavailable.
        if self._ffmpeg_available:
            output_path = self.output_dir / f"{prefix}.mp4"
            animation.save(output_path, writer="ffmpeg", dpi=90)
            self._artifacts.append(
                {
                    "scenario": scenario_name,
                    "kind": "video",
                    "file": output_path.name,
                }
            )
        else:
            output_path = self.output_dir / f"{prefix}.gif"
            animation.save(output_path, writer="pillow", dpi=90)
            self._artifacts.append(
                {
                    "scenario": scenario_name,
                    "kind": "image",
                    "file": output_path.name,
                }
            )

    def finalize(self) -> None:
        if self.runtime_is_notebook:
            return
        if self.mode not in {"browser", "html"}:
            return
        if self.output_dir is None or not self._artifacts:
            return

        cards: list[str] = []
        for artifact in self._artifacts:
            scenario = artifact["scenario"]
            file_name = artifact["file"]
            if artifact["kind"] == "video":
                media = f"<video controls loop preload='metadata' style='width:100%;max-height:360px'><source src='{file_name}' type='video/mp4'></video>"
            else:
                media = f"<img src='{file_name}' alt='{scenario}' style='width:100%;max-height:360px;object-fit:contain'/>"
            cards.append(
                "<section style='background:#1b1b1b;padding:12px;border-radius:10px'>"
                f"<h3 style='margin:0 0 8px 0;font:600 16px sans-serif;color:#eee'>{scenario}</h3>"
                f"{media}"
                "</section>"
            )

        html = (
            "<!doctype html><html><head><meta charset='utf-8'><title>UrbanMobility Animations</title></head>"
            "<body style='margin:0;padding:16px;background:#111;color:#ddd'>"
            "<h1 style='font:700 22px sans-serif;margin:0 0 12px 0'>UrbanMobility Animation Dashboard</h1>"
            "<p style='font:400 14px sans-serif;color:#aaa;margin:0 0 14px 0'>Generated from the latest script run.</p>"
            "<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px'>"
            + "".join(cards)
            + "</div></body></html>"
        )
        index_path = self.output_dir / "index.html"
        index_path.write_text(html, encoding="utf-8")
        webbrowser.open(index_path.resolve().as_uri())

    def render(self, animation, scenario_name: str):
        try:
            if self.mode in {"off", "none", "0", "false"}:
                return None

            if not self.runtime_is_notebook:
                if self.mode in {"browser", "html"}:
                    self._save_animation_artifact(animation, scenario_name)
                else:
                    self._active_animations.append(animation)
                    plt.show()
                return None

            try:
                from IPython.display import HTML

                return HTML(animation.to_jshtml())
            except Exception:
                return None
        finally:
            try:
                plt.close(animation._fig)
            except Exception:
                pass

    def animate_model(self, model, animation_plot, scenario_name: str, figsize=(8, 6)):
        if self.mode in {"off", "none", "0", "false"}:
            return None

        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
        animation = ap.animate(model, fig, ax, animation_plot)
        return self.render(animation, scenario_name)

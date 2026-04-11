from pathlib import Path
import webbrowser

import agentpy as ap
import matplotlib
from matplotlib import pyplot as plt


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

    def _write_animation_html(self, animation, scenario_name: str) -> None:
        if self.output_dir is None:
            return

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._counter += 1
        safe_name = scenario_name.replace(" ", "_").replace("/", "_").lower()
        output_path = self.output_dir / f"{self._counter:02d}_{safe_name}.html"

        # Prefer HTML5 video controls when ffmpeg is available.
        # Fall back to jshtml if video encoding is unavailable.
        extra_script = ""
        try:
            video_html = animation.to_html5_video()
        except Exception:
            video_html = animation.to_jshtml(default_mode="loop")
            extra_script = (
                "<script>window.addEventListener('load',function(){"
                "const btns=document.querySelectorAll('button');"
                "const play=Array.from(btns).find(b=>/play/i.test(b.textContent||''));"
                "if(play){play.click();}"
                "});</script>"
            )
        page_html = (
            "<!doctype html><html><head><meta charset='utf-8'><title>UrbanMobility Animation</title></head>"
            f"<body style='margin:0;padding:1rem;background:#111;color:#ddd'>{video_html}{extra_script}</body></html>"
        )
        output_path.write_text(page_html, encoding="utf-8")
        webbrowser.open(output_path.resolve().as_uri())

    def render(self, animation, scenario_name: str):
        try:
            if self.mode in {"off", "none", "0", "false"}:
                return None

            if not self.runtime_is_notebook:
                if self.mode in {"browser", "html"}:
                    self._write_animation_html(animation, scenario_name)
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

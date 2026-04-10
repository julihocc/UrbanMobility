from matplotlib import pyplot as plt
import numpy as np

from visual.AnimationUtils import plot_city


def _count_heatmap(cell_sets):
    return np.array([[len(cell) for cell in row] for row in cell_sets])


def load_heatmaps(model):
    mc = model.metrics_collector
    return {
        "walker_count": _count_heatmap(mc.walker_count_hm),
        "driver_count": _count_heatmap(mc.driver_count_hm),
        "walker_speed": np.array(mc.walker_speed_hm),
        "driver_speed": np.array(mc.driver_speed_hm),
    }


def generate_heatmaps(city, heatmaps, figsize=(12, 10), show=True):
    fig, axes = plt.subplots(2, 2, figsize=figsize, constrained_layout=True)
    plots = [
        ("Walker Count", heatmaps["walker_count"], "Greens"),
        ("Driver Count", heatmaps["driver_count"], "Blues"),
        ("Walker Speed", heatmaps["walker_speed"], "YlGn"),
        ("Driver Speed", heatmaps["driver_speed"], "YlOrRd"),
    ]

    for ax, (title, values, cmap) in zip(axes.flat, plots):
        plot_city(city, ax, alpha="55")
        image = ax.imshow(values, cmap=cmap, alpha=0.65)
        ax.set_title(title)
        ax.figure.colorbar(image, ax=ax, fraction=0.046, pad=0.04)

    if show:
        plt.show()

    return fig, axes

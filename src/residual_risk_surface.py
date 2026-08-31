import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

from risk_data import color_of, load_data

TICKS = [0, 10, 20, 30, 40, 50, 63]


def facet_colors(z_values, rules):
    colors = np.empty(z_values.shape, dtype=object)
    rows, cols = z_values.shape
    for i in range(rows):
        for j in range(cols):
            i2, j2 = min(i + 1, rows - 1), min(j + 1, cols - 1)
            worst = max(z_values[i, j], z_values[i2, j], z_values[i, j2], z_values[i2, j2])
            colors[i, j] = color_of(worst, rules)
    return colors


def draw(axes, x_axis, y_axis, z_values, rules, facets, evenly_spaced, title):
    grid_x = np.arange(len(x_axis), dtype=float) if evenly_spaced else x_axis
    mesh_x, mesh_y = np.meshgrid(grid_x, y_axis)

    axes.plot_surface(
        mesh_x, mesh_y, z_values,
        facecolors=facets,
        rstride=1, cstride=1,
        shade=False, antialiased=True,
        edgecolor="0.30", linewidth=0.35,
    )
    axes.scatter(
        mesh_x.ravel(), mesh_y.ravel(), z_values.ravel(),
        c=[color_of(value, rules) for value in z_values.ravel()],
        s=18, edgecolor="black", linewidth=0.4, depthshade=False,
    )

    axes.set_xlabel("Initial risk  Ri", labelpad=12, fontweight="bold")
    axes.set_ylabel("Control index  C", labelpad=8, fontweight="bold")
    axes.set_zlabel("Residual risk  Rr", labelpad=8, fontweight="bold")
    axes.set_title(title, fontsize=11, pad=2)

    if evenly_spaced:
        axes.set_xticks(grid_x[::2])
        axes.set_xticklabels([f"{value:g}" for value in x_axis[::2]], fontsize=8)
    else:
        axes.set_xticks(TICKS[1:])
    axes.set_yticks(y_axis)
    axes.set_zticks(TICKS)
    axes.view_init(elev=24, azim=-126)
    axes.set_box_aspect((1.55, 1, 1.05))
    axes.tick_params(labelsize=8)


def main():
    parser = argparse.ArgumentParser(
        description="3D surface of the residual risk Rr = ROUNDUP(Ri / C, 0)."
    )
    parser.add_argument("--workbook", type=Path, default=None)
    parser.add_argument("--sheet", default="Sheet1")
    parser.add_argument("--column", default="D")
    parser.add_argument("--output", type=Path, default=Path("output/residual_risk_3d.png"))
    parser.add_argument("--dpi", type=int, default=170)
    args = parser.parse_args()

    x_axis, y_axis, z_values, rules = load_data(args.workbook, args.sheet, args.column)
    facets = facet_colors(z_values, rules)

    figure = plt.figure(figsize=(15, 6.3))
    figure.suptitle(
        "Residual risk  Rr = ROUNDUP(Ri / C, 0)",
        fontsize=14, fontweight="bold", y=0.97,
    )

    draw(figure.add_subplot(121, projection="3d"), x_axis, y_axis, z_values, rules,
         facets, False, "Ri axis on its true numeric scale")
    draw(figure.add_subplot(122, projection="3d"), x_axis, y_axis, z_values, rules,
         facets, True, "Ri axis as evenly spaced steps (readability)")

    figure.legend(
        handles=[Patch(facecolor=color, edgecolor="black", label=label)
                 for _, color, label in rules],
        title="Residual risk level", ncol=4,
        loc="lower center", bbox_to_anchor=(0.5, 0.005), framealpha=0.95,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.10, wspace=0.02)
    figure.savefig(args.output, dpi=args.dpi)

    print(f"Figure saved: {args.output}")
    print(f"{len(x_axis)} Ri values x {len(y_axis)} C values = {z_values.size} points")
    print("Rules used:", [label for _, _, label in rules])


if __name__ == "__main__":
    main()

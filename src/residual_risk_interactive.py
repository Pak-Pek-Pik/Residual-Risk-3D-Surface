import argparse
import webbrowser
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from risk_data import DEFAULT_COLOR, category_of, load_data

HOVER = ("Ri = %{customdata[0]:g}<br>C = %{customdata[1]:g}"
         "<br><b>Rr = %{customdata[2]:g}</b><extra></extra>")


def color_scale(palette):
    steps = []
    count = len(palette)
    for index, color in enumerate(palette):
        steps.append([index / count, color])
        steps.append([(index + 1) / count, color])
    return steps


def build_traces(x_axis, y_axis, z_values, categories, palette, scale, evenly_spaced):
    grid_x = np.arange(len(x_axis), dtype=float) if evenly_spaced else x_axis
    mesh_x, mesh_y = np.meshgrid(grid_x, y_axis)
    real_x = np.meshgrid(x_axis, y_axis)[0]

    surface = go.Surface(
        x=grid_x, y=y_axis, z=z_values,
        surfacecolor=categories + 0.5,
        colorscale=scale, cmin=0, cmax=len(palette),
        showscale=False,
        opacity=1.0,
        lighting=dict(ambient=1.0, diffuse=0.0, specular=0.0, roughness=1.0),
        customdata=np.dstack([real_x, mesh_y, z_values]),
        hovertemplate=HOVER,
        name="surface", showlegend=False,
    )

    markers = go.Scatter3d(
        x=mesh_x.ravel(), y=mesh_y.ravel(), z=z_values.ravel(),
        mode="markers",
        marker=dict(
            size=3,
            color=[palette[int(index)] for index in categories.ravel()],
            line=dict(color="black", width=1),
        ),
        customdata=np.stack([real_x.ravel(), mesh_y.ravel(), z_values.ravel()], axis=-1),
        hovertemplate=HOVER,
        name="points", showlegend=False,
    )

    line_x, line_y, line_z = [], [], []
    for i in range(z_values.shape[0]):
        line_x += list(grid_x) + [None]
        line_y += [y_axis[i]] * len(grid_x) + [None]
        line_z += list(z_values[i, :]) + [None]
    for j in range(z_values.shape[1]):
        line_x += [grid_x[j]] * len(y_axis) + [None]
        line_y += list(y_axis) + [None]
        line_z += list(z_values[:, j]) + [None]

    wireframe = go.Scatter3d(
        x=line_x, y=line_y, z=line_z, mode="lines",
        line=dict(color="rgba(50,50,50,0.6)", width=1),
        hoverinfo="skip", name="wireframe", showlegend=False,
    )
    return surface, wireframe, markers


def main():
    parser = argparse.ArgumentParser(
        description="Interactive 3D surface of the residual risk Rr = ROUNDUP(Ri / C, 0)."
    )
    parser.add_argument("--workbook", type=Path, default=None)
    parser.add_argument("--sheet", default="Sheet1")
    parser.add_argument("--column", default="D")
    parser.add_argument("--output", type=Path, default=Path("output/residual_risk_3d.html"))
    parser.add_argument("--plotlyjs", choices=["bundle", "cdn"], default="bundle")
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()

    x_axis, y_axis, z_values, rules = load_data(args.workbook, args.sheet, args.column)

    categories = np.vectorize(lambda value: category_of(value, rules))(z_values).astype(float)
    palette = [color for _, color, _ in rules] + [DEFAULT_COLOR]
    labels = [label for _, _, label in rules] + ["other"]
    scale = color_scale(palette)

    figure = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "surface"}, {"type": "surface"}]],
        subplot_titles=("Ri axis on its true numeric scale",
                        "Ri axis as evenly spaced steps (readability)"),
        horizontal_spacing=0.02,
    )

    for column, evenly_spaced in ((1, False), (2, True)):
        for trace in build_traces(x_axis, y_axis, z_values, categories,
                                  palette, scale, evenly_spaced):
            figure.add_trace(trace, row=1, col=column)

    for color, label in zip(palette, labels):
        figure.add_trace(
            go.Scatter3d(
                x=[None], y=[None], z=[None], mode="markers",
                marker=dict(size=12, symbol="square", color=color,
                            line=dict(color="black", width=1)),
                name=label, showlegend=True, hoverinfo="skip",
            ),
            row=1, col=1,
        )

    camera = dict(eye=dict(x=-1.07, y=-1.48, z=0.81))
    shared_axes = dict(
        zaxis=dict(title=dict(text="Residual risk  Rr"),
                   tickvals=[0, 10, 20, 30, 40, 50, 63]),
        yaxis=dict(title=dict(text="Control index  C"), tickvals=list(y_axis)),
        aspectmode="manual", aspectratio=dict(x=1.55, y=1, z=1.05),
        camera=camera,
    )

    figure.update_layout(
        title=dict(
            text="<b>Residual risk  Rr = ROUNDUP(Ri / C, 0)</b>",
            x=0.5, xanchor="center", font=dict(size=18),
        ),
        scene=dict(xaxis=dict(title=dict(text="Initial risk  Ri")), **shared_axes),
        scene2=dict(
            xaxis=dict(
                title=dict(text="Initial risk  Ri"),
                tickmode="array",
                tickvals=list(np.arange(len(x_axis))[::2]),
                ticktext=[f"{value:g}" for value in x_axis[::2]],
            ),
            **shared_axes,
        ),
        legend=dict(title=dict(text="Residual risk level"),
                    orientation="h", x=0.5, xanchor="center", y=-0.02),
        margin=dict(l=10, r=10, t=70, b=10),
        height=720,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(
        args.output,
        include_plotlyjs=True if args.plotlyjs == "bundle" else "cdn",
        config={"scrollZoom": True, "displaylogo": False,
                "toImageButtonOptions": {"format": "png", "scale": 3,
                                         "filename": "residual_risk_3d"}},
    )

    print(f"Interactive figure saved: {args.output}")
    print(f"{len(x_axis)} Ri values x {len(y_axis)} C values = {z_values.size} points")
    print("Rules used:", [label for _, _, label in rules])

    if args.open:
        try:
            webbrowser.open(args.output.resolve().as_uri())
        except Exception:
            pass


if __name__ == "__main__":
    main()

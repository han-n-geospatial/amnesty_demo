import numpy as np
import pandas as pd
from math import pi

from bokeh.models import (
    ColorBar, LinearColorMapper, HoverTool, CustomJSTickFormatter,
    ColumnDataSource, DataTable, TableColumn, Div, NumeralTickFormatter,
)
from bokeh.palettes import Viridis9
from bokeh.plotting import figure
from bokeh.layouts import column

from config import BG, PANEL, ACCENT, TEXT, SUBTEXT, GRID, PALETTE


# ── Theme helpers ─────────────────────────────────────────────────────────────

def style_figure(p, title: str = "") -> object:
    p.background_fill_color = PANEL
    p.border_fill_color = BG
    p.outline_line_color = None
    p.title.text = title
    p.title.text_color = TEXT
    p.title.text_font_size = "13px"
    p.title.text_font_style = "bold"
    p.axis.axis_label_text_color = SUBTEXT
    p.axis.major_label_text_color = SUBTEXT
    p.axis.axis_line_color = GRID
    p.axis.major_tick_line_color = GRID
    p.axis.minor_tick_line_color = None
    p.grid.grid_line_color = GRID
    p.grid.grid_line_alpha = 0.6
    return p


def style_legend(legend) -> None:
    legend.location = "top_left"
    legend.label_text_font_size = "10px"
    legend.label_text_color = TEXT
    legend.background_fill_color = PANEL
    legend.border_line_color = GRID
    legend.glyph_height = 12
    legend.glyph_width = 12
    legend.spacing = 2
    legend.padding = 6


# ── Layout components ─────────────────────────────────────────────────────────

def header(text: str, width: int = 1100) -> Div:
    return Div(text=f"""
        <div style="border-left:4px solid {PALETTE[0]};padding:8px 14px;
                    color:{TEXT};font-size:14px;font-weight:700;
                    letter-spacing:0.04em;margin:10px 0 4px 0;
                    background:{PANEL};border-radius:0 4px 4px 0;">
            {text}
        </div>""", width=width)


def title_div(width: int = 1100) -> Div:
    return Div(text=f"""
        <div style="padding:18px 0 8px 0;border-bottom:2px solid {PALETTE[0]};margin-bottom:8px;">
            <span style="color:{ACCENT};font-size:24px;font-weight:800;
                         letter-spacing:0.04em;">
                Sri Lanka OSM Building Data Dashboard
            </span><br/>
            <span style="color:{SUBTEXT};font-size:13px;margin-top:4px;display:block;">
                OSM building footprints &nbsp;·&nbsp; (n = 3,379,369)
            </span>
        </div>""", width=width)


# ── Map ───────────────────────────────────────────────────────────────────────

def make_choropleth_map(map_data: dict, x_range: tuple, y_range: tuple) -> object:
    mapper = LinearColorMapper(
        palette=Viridis9,
        low=min(map_data["building_count"]),
        high=max(map_data["building_count"]),
    )
    hover = HoverTool(tooltips=[
        ("Province", "@name"),
        ("Buildings", "@building_count{,}"),
    ])
    p = figure(
        title="Building Counts by Province (Admin Level 5)",
        tools=["pan", "wheel_zoom", "reset", "save", hover],
        x_axis_location=None, y_axis_location=None,
        x_range=x_range, y_range=y_range,
        width=560, height=760,
    )
    p.background_fill_color = PANEL
    p.border_fill_color = BG
    p.outline_line_color = None
    p.title.text_color = TEXT
    p.title.text_font_size = "13px"
    p.title.text_font_style = "bold"
    p.grid.grid_line_color = None
    p.hover.point_policy = "follow_mouse"

    p.patches(
        "x", "y", source=map_data,
        fill_color={"field": "building_count", "transform": mapper},
        fill_alpha=0.85, line_color="#ffffff", line_width=0.8,
    )
    color_bar = ColorBar(
        color_mapper=mapper, label_standoff=8, width=12, location=(0, 0),
        formatter=CustomJSTickFormatter(code="return (tick / 1e5).toFixed(1) + ' ×10⁵'"),
        major_label_text_color=SUBTEXT, bar_line_color=None,
        background_fill_color=PANEL,
    )
    p.add_layout(color_bar, "right")
    return p


# ── Attribute charts ──────────────────────────────────────────────────────────

def make_histogram(series: pd.Series, title: str, x_label: str,
                   color: str, bins: int = 40) -> object:
    hist, edges = np.histogram(series.dropna(), bins=bins)
    p = figure(width=320, height=240, tools="")
    style_figure(p, title)
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
           fill_color=color, fill_alpha=0.85, line_color=PANEL, line_width=0.5)
    p.xaxis.axis_label = x_label
    p.yaxis.formatter = NumeralTickFormatter(format="0a")
    return p


def make_pie(series: pd.Series, title: str) -> object:
    counts = series.dropna().value_counts()
    data = pd.DataFrame({"label": counts.index, "value": counts.values})
    data["angle"] = data["value"] / data["value"].sum() * 2 * pi
    data["color"] = (PALETTE * 4)[:len(data)]
    data["pct"]   = (data["value"] / data["value"].sum() * 100).round(1).astype(str) + "%"

    p = figure(width=380, height=340, tools="hover",
               tooltips="@label: @pct", toolbar_location=None,
               x_range=(-1.35, 1.35), y_range=(-1.1, 1.1))
    style_figure(p, title)
    p.axis.visible = False
    p.grid.grid_line_color = None

    angle = 0.0
    for _, seg in data.iterrows():
        src = ColumnDataSource({"label": [seg["label"]], "pct": [seg["pct"]]})
        p.wedge(x=0, y=0, radius=0.75,
                start_angle=angle, end_angle=angle + seg["angle"],
                fill_color=seg["color"], line_color=PANEL, line_width=1.5,
                legend_label=seg["label"], source=src)
        angle += seg["angle"]

    style_legend(p.legend[0])
    return p


def make_stacked_bar(df: pd.DataFrame, x_col: str, stack_col: str, title: str) -> object:
    stack_cats = sorted(df[stack_col].dropna().unique().tolist())
    pivot = (
        df.dropna(subset=[x_col, stack_col])
        .groupby([x_col, stack_col])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=stack_cats, fill_value=0)
    )
    src = ColumnDataSource(dict(
        x=pivot.index.tolist(),
        **{cat: pivot[cat].tolist() for cat in stack_cats},
    ))
    p = figure(
        x_range=pivot.index.tolist(),
        width=680, height=300,
        tools="hover",
        tooltips=[(cat, f"@{{{cat}}}{{,}}") for cat in stack_cats],
        toolbar_location=None,
    )
    style_figure(p, title)
    p.vbar_stack(stack_cats, x="x", width=0.7,
                 color=(PALETTE * 4)[:len(stack_cats)],
                 source=src, legend_label=stack_cats)
    p.xaxis.axis_label = x_col.replace("_", " ").title()
    p.yaxis.axis_label = "Count"
    p.yaxis.formatter = NumeralTickFormatter(format="0a")
    p.xaxis.major_label_orientation = 0.6
    style_legend(p.legend[0])
    return p


# ── Tables ────────────────────────────────────────────────────────────────────

def make_continuous_stats_table(df: pd.DataFrame, columns: list) -> DataTable:
    rows = []
    for col in columns:
        s = df[col].dropna()
        rows.append({
            "variable": col.replace("_", " ").title(),
            "mean":     f"{s.mean():.1f}",
            "median":   f"{s.median():.1f}",
            "std":      f"{s.std():.1f}",
            "min":      f"{s.min():.1f}",
            "max":      f"{s.max():.1f}",
            "missing":  f"{df[col].isna().mean()*100:.1f}%",
        })
    return DataTable(
        source=ColumnDataSource(pd.DataFrame(rows)),
        columns=[
            TableColumn(field="variable", title="Variable", width=180),
            TableColumn(field="mean",     title="Mean",     width=80),
            TableColumn(field="median",   title="Median",   width=80),
            TableColumn(field="std",      title="Std Dev",  width=80),
            TableColumn(field="min",      title="Min",      width=80),
            TableColumn(field="max",      title="Max",      width=80),
            TableColumn(field="missing",  title="Missing",  width=80),
        ],
        width=680, height=110,
        background=PANEL, index_position=None,
        stylesheets=[f":host {{ color: {TEXT}; font-size: 13px; }}"],
    )


def make_discrete_stats_table(df: pd.DataFrame, columns: list) -> DataTable:
    rows = []
    for col in columns:
        valid = df[col].notna().sum()
        missing_pct = df[col].isna().mean() * 100
        for cat, cnt in df[col].value_counts().items():
            rows.append({
                "variable": col.replace("_", " ").title(),
                "category": str(cat),
                "count":    f"{cnt:,}",
                "pct":      f"{cnt / valid * 100:.1f}%",
                "missing":  f"{missing_pct:.1f}%",
            })
    return DataTable(
        source=ColumnDataSource(pd.DataFrame(rows)),
        columns=[
            TableColumn(field="variable", title="Variable",   width=160),
            TableColumn(field="category", title="Category",   width=180),
            TableColumn(field="count",    title="Count",      width=100),
            TableColumn(field="pct",      title="% of Valid", width=100),
            TableColumn(field="missing",  title="Missing %",  width=100),
        ],
        width=660, height=220,
        background=PANEL, index_position=None,
        stylesheets=[f":host {{ color: {TEXT}; font-size: 12px; }}"],
    )

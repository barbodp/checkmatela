"""Size charts for the Antonio Uomo products, one entry per chart the supplier shows in a product's "Size Chart" pop-up.

Each product in tools/catalog/antonio-uomo.json carries the id of the chart its supplier page pops up (`chart`, read by au_fetch.py), and
gen_antonio.py renders that product's own pop-up from CHARTS below — there is deliberately no site-wide size guide for these pieces.
To add a chart: transcribe the supplier's table here under its id (the image file name, e.g. SIZE-CHART-MAY-3). Values are exactly as printed (inches).
"""

CHARTS = {
    # "ANTONIO UOMO SLIM SIZE RECOMMENDATION CHART (IN INCH)" — the only chart the supplier uses; it pops up on all 145 products
    "SIZE-CHART-MAY-3": dict(
        title="Antonio Uomo slim size recommendation chart",
        unit="All measurements are in inches.",
        sizes=[("XS", "36R"), ("S", "40R"), ("M", "42R"), ("L", "44R"), ("XL", "46R"), ("XXL", "48R"), ("3XL", "52R"), ("4XL", "56R")],
        groups=[
            ("Jacket", [
                ("Shoulder", [17.73, 18.68, 19.15, 19.62, 20.09, 20.57, 21.55, 22.58]),
                ("Chest", [38.61, 42.16, 43.73, 45.7, 47.67, 49.25, 52.8, 55.95]),
                ("Jacket length", [28.37, 29.16, 29.55, 29.94, 30.34, 30.73, 31.52, 32.31]),
                ("Sleeve length", [24.23, 24.63, 24.82, 25.02, 25.22, 25.41, 26, 26.4]),
            ]),
            ("Pants", [
                ("Pants waist", [31.52, 35.46, 37.43, 39.4, 41.37, 43.34, 47.28, 51.22]),
                ("Pants inseam length", [35.66, 36.05, 36.05, 36.05, 36.45, 36.45, 36.84, 36.84]),
            ]),
        ],
        notice="Please choose a jacket chest at least 2–3 inches bigger than your actual chest circumference, measured without outerwear.",
        points=[("Shoulder width", "Across the back, from one shoulder seam to the other."), ("Chest", "Around the fullest part of the chest."),
                ("Sleeve length", "From the shoulder seam down to the cuff."), ("Pants waist", "Around the waistband."),
                ("Pants inseam length", "From the crotch seam down to the hem.")],
    ),
}


def fmt(v):
    return f"{v:g}"


def chart_html(chart_id):
    """Inner HTML of the pop-up for one chart (title, table, notice, where each measurement is taken)."""
    c = CHARTS[chart_id]
    head = "".join(f'<th scope="col"><b>{l}</b><span>{n}</span></th>' for l, n in c["sizes"])
    body = ""
    for group, rows in c["groups"]:
        body += f'<tr class="au-size__group"><th scope="rowgroup" colspan="{len(c["sizes"]) + 1}">{group}</th></tr>'
        for name, vals in rows:
            body += f'<tr><th scope="row">{name}</th>' + "".join(f"<td>{fmt(v)}</td>" for v in vals) + "</tr>"
    # phones: the same numbers turned on their side (one row per size) so nothing has to scroll sideways
    cols = [(g, name) for g, rows in c["groups"] for name, _ in rows]
    vals = [v for _, rows in c["groups"] for _, v in rows]
    grp_head = "".join(f'<th colspan="{len(rows)}" scope="colgroup">{g}</th>' for g, rows in c["groups"])
    short = lambda n: {"Jacket length": "Length"}.get(n, n.replace("Pants ", "").replace(" length", "").capitalize())
    tall_head = "".join(f'<th scope="col">{short(n)}</th>' for _, n in cols)
    tall_rows = "".join(f'<tr><th scope="row"><b>{l}</b><span>{n}</span></th>' + "".join(f"<td>{fmt(v[i])}</td>" for v in vals) + "</tr>" for i, (l, n) in enumerate(c["sizes"]))
    tall = (f'<div class="table-wrap au-size-tall"><table class="au-size au-size--tall"><thead><tr><th rowspan="2" scope="col">Size</th>{grp_head}</tr><tr>{tall_head}</tr></thead><tbody>{tall_rows}</tbody></table></div>')
    points = "".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in c["points"])
    return (f'<h2 class="au-chart__title" id="auChartTitle">{c["title"]}</h2><p class="au-chart__unit">{c["unit"]}</p>'
            f'<div class="table-wrap au-size-wide"><table class="au-size"><thead><tr><th scope="col"><span class="visually-hidden">Measurement</span></th>{head}</tr></thead><tbody>{body}</tbody></table></div>{tall}'
            f'<p class="au-size__note"><b>Notice:</b> {c["notice"]}</p>'
            f'<h3 class="au-chart__sub">Where each measurement is taken</h3><ul class="au-how">{points}</ul>')

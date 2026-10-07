"""Antonio Uomo slim-fit size chart, rebuilt as a simple table. Numbers are the supplier's measurements (inches), rounded to one decimal.
Used by gen_antonio.py (product pages) and gen_info_pages.py (size-guide.html)."""

SIZES = [("XS", "36R"), ("S", "40R"), ("M", "42R"), ("L", "44R"), ("XL", "46R"), ("XXL", "48R"), ("3XL", "52R"), ("4XL", "56R")]
ROWS = [
    ("Jacket", [
        ("Shoulder", [17.73, 18.68, 19.15, 19.62, 20.09, 20.57, 21.55, 22.58]),
        ("Chest", [38.61, 42.16, 43.73, 45.7, 47.67, 49.25, 52.8, 55.95]),
        ("Length", [28.37, 29.16, 29.55, 29.94, 30.34, 30.73, 31.52, 32.31]),
        ("Sleeve", [24.23, 24.63, 24.82, 25.02, 25.22, 25.41, 26, 26.4]),
    ]),
    ("Trousers", [
        ("Waist", [31.52, 35.46, 37.43, 39.4, 41.37, 43.34, 47.28, 51.22]),
        ("Inseam", [35.66, 36.05, 36.05, 36.05, 36.45, 36.45, 36.84, 36.84]),
    ]),
]
NOTE = "Pick a jacket chest 2–3 inches bigger than your own chest (measured without a coat on)."
HOW = [("Chest", "Around the fullest part of your chest, under your arms."),
       ("Waist", "Around your natural waist, just above the hip bones."),
       ("Inseam", "From the crotch to where you want the trouser hem to land."),
       ("Sleeve", "From the shoulder seam to the wrist bone, arm relaxed.")]


def table_html(cls="au-size"):
    head = "".join(f"<th scope=\"col\"><b>{l}</b><span>{n}</span></th>" for l, n in SIZES)
    body = ""
    for group, rows in ROWS:
        body += f'<tr class="au-size__group"><th scope="rowgroup" colspan="{len(SIZES) + 1}">{group}</th></tr>'
        for name, vals in rows:
            body += f'<tr><th scope="row">{name}</th>' + "".join(f"<td>{v:.1f}</td>" for v in vals) + "</tr>"
    return (f'<div class="table-wrap"><table class="{cls}"><caption>Antonio Uomo slim fit, in inches</caption>'
            f'<thead><tr><th scope="col"><span class="visually-hidden">Measurement</span></th>{head}</tr></thead><tbody>{body}</tbody></table></div>'
            f'<p class="au-size__note"><b>Good to know:</b> {NOTE}</p>')


def how_html():
    return '<ul class="au-how">' + "".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in HOW) + "</ul>"

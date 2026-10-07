"""Product information shared by every suit page (gen_antonio.py): the scraped Antonio Uomo pieces and "The Openings" from king.json.
Copy comes from the supplier's product pages (fabric, care, design text) — the same on every suit. Edit here and re-run gen_antonio.py."""

CHART_ID = "SIZE-CHART-MAY-3"                       # key into au_sizes.CHARTS: the pop-up size chart
SIZES = [str(n) for n in range(34, 58, 2)]          # jacket sizes 34-56
LENGTHS = ["Short", "Regular", "Long"]
LEDE = "Upgrade your wardrobe today with an Antonio Uomo Suit. Achieve the classic, refined look you've been seeking."
BULLETS = ["68% Polyester 29% Viscose, 3% Spandex", "Button closure", "Dry Clean Only", "Imported"]

# the supplier's "Our Suits Mean Business" copy by number of pieces (lightly edited: it called the fabric wool, which doesn't match the fabric listed)
DESIGN = {
    2: ["Elevate your style for those memorable moments, from proms and weddings to graduations and more, with a two-piece suit designed to leave a lasting impression.",
        ("Jacket", "A slim, modern cut flatters your silhouette, and the notch lapel adds a touch of contemporary flair. The jacket has double vents for ease of movement and multiple interior pockets for your convenience."),
        ("Trousers", "A flat front, slim legs and meticulous stitching. The adjustable waistband and cuffed hems help the fit, while the concealed zip fly and hook-and-bar closure keep a sleek, streamlined look.")],
    3: ["Elevate your style for those memorable moments, from proms and weddings to graduations and more, with a three-piece ensemble designed to leave a lasting impression.",
        ("Jacket", "A slim, contemporary cut enhances your silhouette, and the notch lapel adds a modern touch. The jacket has double vents for effortless movement and multiple interior pockets for your convenience."),
        ("Vest", "Made from the same fabric as the jacket, the vest adds depth and character to the look. A classic button front and an adjustable back belt give a tailored fit, and it works worn on its own or under the jacket."),
        ("Trousers", "A flat front, slim leg and precision stitching. The adjustable waistband and cuffed hems help the fit, while the concealed zip fly and hook-and-bar closure keep a sleek, streamlined look.")],
}
# King catalog style -> pieces in the set (tuxedos are jacket + trousers)
KING_PIECES = {"Three-piece": 3, "Two-piece": 2, "Tuxedo": 2}

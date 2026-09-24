/* Reviews, keyed by product id (the card's data-id: "king/<slug>" or "pawn/<line>/<colour>").
   Every entry below is a SAMPLE written as a placeholder (sample:true → a "Sample review" tag is shown).
   Replace them with real reviews and drop the flag. Fields:
     n name · r rating 1-5 · t title · b body · d date (YYYY-MM-DD)
     King:  height, build, size, fit ("Runs small" | "True to size" | "Runs large"), occasion
     Pawn:  age, height, size, fit, occasion
   The reviewer-attribute filters in the Quick View are built from whichever of these fields the reviews have. */
window.CHECKMATELA_REVIEWS = {
  "king/sicilian-onyx-tux": [
    { n: "Marcus T.", r: 5, t: "Exactly what black tie should look like", b: "Wore it to a charity gala and got compliments all night. The shawl lapel sits perfectly and the trousers break cleanly on the shoe.", d: "2026-03-14", height: "6'1\"", build: "Athletic", size: "42R", fit: "True to size", occasion: "Black tie", sample: true },
    { n: "Daniel R.", r: 4, t: "Sharp, but cut slim", b: "Beautiful fabric and construction. I'm on the slimmer side and it fit great; if you're broader, size up.", d: "2026-02-02", height: "5'9\"", build: "Slim", size: "38R", fit: "Runs small", occasion: "Wedding", sample: true },
    { n: "Andre W.", r: 5, t: "Prom-night ready", b: "Bought this for my son's prom and he wouldn't take it off. The free alterations made the sleeves perfect.", d: "2026-04-21", height: "5'11\"", build: "Average", size: "40R", fit: "True to size", occasion: "Prom", sample: true },
    { n: "Luis M.", r: 4, t: "Great tuxedo, ordered a size up", b: "Broader through the chest so I went up to a 46L. Once tailored it looked custom.", d: "2026-01-19", height: "6'3\"", build: "Broad", size: "46L", fit: "Runs small", occasion: "Wedding", sample: true },
    { n: "Kevin P.", r: 5, t: "Worth every dollar", b: "Feels far more expensive than it is. The satin on the lapel catches the light beautifully.", d: "2025-12-06", height: "5'8\"", build: "Athletic", size: "38S", fit: "True to size", occasion: "Black tie", sample: true }
  ],
  "king/ruy-lopez-three-piece": [
    { n: "Jordan S.", r: 5, t: "The waistcoat makes it", b: "Wore it as a groomsman. The three-piece looked polished from the ceremony to the last dance.", d: "2026-05-10", height: "5'10\"", build: "Average", size: "40R", fit: "True to size", occasion: "Wedding", sample: true },
    { n: "Ethan B.", r: 4, t: "Great for the office too", b: "Versatile enough to wear to client meetings. Trousers came a little long, hemmed free.", d: "2026-03-02", height: "6'0\"", build: "Athletic", size: "42L", fit: "True to size", occasion: "Business", sample: true },
    { n: "Omar H.", r: 4, t: "Roomy in the jacket", b: "Comfortable and looks sharp. I'd size down if you like a close fit.", d: "2026-02-11", height: "5'7\"", build: "Slim", size: "38R", fit: "Runs large", occasion: "Formal", sample: true },
    { n: "Chris L.", r: 5, t: "Looks like a custom suit", b: "The fit through the shoulders is spot on.", d: "2025-11-28", height: "5'11\"", build: "Athletic", size: "40R", fit: "True to size", occasion: "Wedding", sample: true }
  ],
  "king/kings-gambit-royal-plaid": [
    { n: "Tyler G.", r: 5, t: "Bold without being loud", b: "The royal blue plaid gets noticed but still looks refined. Paired with a white shirt and a navy tie.", d: "2026-04-05", height: "6'0\"", build: "Athletic", size: "42R", fit: "True to size", occasion: "Wedding", sample: true },
    { n: "Sam K.", r: 4, t: "Prom hit", b: "My son loved the colour. A touch long in the sleeve, fixed at the fitting.", d: "2026-05-18", height: "5'9\"", build: "Slim", size: "38R", fit: "True to size", occasion: "Prom", sample: true },
    { n: "Victor A.", r: 5, t: "Standout piece", b: "Great fabric weight — comfortable for a long evening.", d: "2026-01-30", height: "5'10\"", build: "Average", size: "40R", fit: "True to size", occasion: "Formal", sample: true }
  ],
  "king/italian-game-bordeaux": [
    { n: "Nate F.", r: 5, t: "Bordeaux done right", b: "Rich colour, black satin lapel, and it photographs beautifully.", d: "2026-02-14", height: "6'2\"", build: "Athletic", size: "44L", fit: "True to size", occasion: "Black tie", sample: true },
    { n: "Isaiah C.", r: 4, t: "Runs slightly small", b: "Loved it, but go up a size if you're between sizes.", d: "2026-03-22", height: "5'8\"", build: "Broad", size: "42R", fit: "Runs small", occasion: "Prom", sample: true },
    { n: "Ben D.", r: 5, t: "Wedding favourite", b: "Wore it as the groom. Unforgettable.", d: "2026-04-30", height: "5'11\"", build: "Average", size: "40R", fit: "True to size", occasion: "Wedding", sample: true }
  ],
  "pawn/slim-fit/navy": [
    { n: "Priya N.", r: 5, t: "Sharp for a first suit", b: "My 8-year-old wore it to a family wedding and looked so grown up. Fabric isn't itchy.", d: "2026-04-11", age: "8", height: "50\"", size: "8", fit: "True to size", occasion: "Wedding", sample: true },
    { n: "Michelle O.", r: 4, t: "Tapered but comfortable", b: "Ordered a size up for room to grow; jacket sleeves were adjusted at the fitting.", d: "2026-03-08", age: "10", height: "56\"", size: "12", fit: "Runs small", occasion: "Family photos", sample: true },
    { n: "Carlos V.", r: 5, t: "School concert win", b: "Held up through a full day of play. Still looks crisp.", d: "2026-05-02", age: "6", height: "45\"", size: "6", fit: "True to size", occasion: "School event", sample: true },
    { n: "Aisha J.", r: 5, t: "Great value", b: "The whole set looks premium and the vest makes it feel special.", d: "2026-01-25", age: "12", height: "59\"", size: "14", fit: "True to size", occasion: "Church", sample: true }
  ],
  "pawn/tuxedo/full-black": [
    { n: "Rachel P.", r: 5, t: "Ring bearer approved", b: "Sharp shawl lapel and the bow tie is easy to clip on. Photos looked fantastic.", d: "2026-05-15", age: "5", height: "42\"", size: "6", fit: "Runs large", occasion: "Wedding", sample: true },
    { n: "Tom H.", r: 4, t: "Excellent for prom", b: "My teenager's first tux. Fit well through the shoulders; hemmed the trousers.", d: "2026-04-03", age: "14", height: "63\"", size: "16", fit: "True to size", occasion: "Prom", sample: true },
    { n: "Jasmine R.", r: 5, t: "Comfortable all night", b: "He danced for hours and never fussed with the collar.", d: "2026-02-20", age: "9", height: "52\"", size: "10", fit: "True to size", occasion: "Wedding", sample: true }
  ],
  "pawn/suit-vest-set/black": [
    { n: "Elena M.", r: 5, t: "Perfect for warm weather", b: "No jacket, but still dressed up. Great for an outdoor summer wedding.", d: "2026-06-01", age: "7", height: "48\"", size: "8", fit: "True to size", occasion: "Wedding", sample: true },
    { n: "Greg S.", r: 4, t: "Easy to put on", b: "Kids can get dressed quickly and it still looks smart.", d: "2026-03-17", age: "4", height: "40\"", size: "4", fit: "Runs large", occasion: "Family photos", sample: true },
    { n: "Nadia F.", r: 5, t: "Nice fabric", b: "Vest lays flat and the trousers have an adjustable waist.", d: "2026-02-08", age: "10", height: "54\"", size: "10", fit: "True to size", occasion: "Church", sample: true }
  ],
  "pawn/tuxedo-vest-set/burgundy": [
    { n: "Hannah L.", r: 5, t: "Holiday portrait hit", b: "The burgundy photographs beautifully against a green backdrop.", d: "2025-12-12", age: "6", height: "45\"", size: "6", fit: "True to size", occasion: "Family photos", sample: true },
    { n: "Diego R.", r: 4, t: "Good quality", b: "Satin trim is nice. Went up a size for growing room.", d: "2026-01-14", age: "8", height: "50\"", size: "10", fit: "True to size", occasion: "Wedding", sample: true }
  ]
};

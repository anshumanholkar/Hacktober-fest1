"""HIVE-MIND persona catalog.

55 archetypes that differ by age, maturity as a buyer, spare money, affordability and
pet peeves (not just profession). build_crowd() turns them into individual people
and makes sure the crowd is mostly made of the audience the user asked for.
"""
import random

# How a person behaves as a buyer (1 = impulsive ... 4 = seasoned)
MATURITY = {
    1: "Impulsive & price-driven",
    2: "Still learning to budget",
    3: "Considered buyer",
    4: "Seasoned & selective",
}

MATCH_SHARE = 0.8  # share of the crowd that must belong to the chosen audience (rest = outsiders)

NAMES = [
    "Aarav", "Ananya", "Rohan", "Priya", "Kabir", "Meera", "Arjun", "Isha", "Vikram", "Neha",
    "Siddharth", "Kavya", "Rahul", "Divya", "Aditya", "Pooja", "Karan", "Sneha", "Manish", "Riya",
    "Varun", "Tanvi", "Nikhil", "Shruti", "Harsh", "Ritu", "Dev", "Simran", "Yash", "Aisha",
    "Imran", "Lakshmi", "Gaurav", "Nandini", "Sameer", "Pallavi", "Tushar", "Zoya", "Mohit", "Bhavna",
]


def _a(role, e, age, mat, monthly, cap, tags, bad, buys, desc):
    return {"n": role, "role": role, "e": e, "age": age, "mat": mat, "monthly": monthly,
            "cap": cap, "tags": tags, "bad": bad, "buys": buys, "desc": desc}


ARCHETYPES = [
    # ---- students & very young ------------------------------------------------------
    _a("Broke College Student", "\U0001F392", (18, 23), 1, 1500, 149,
       ["student", "college", "campus", "hostel", "exam", "university", "study", "homework"],
       ["premium", "subscription", "enterprise", "monthly", "fee"],
       "free tiers, student discounts, cheap one-time buys",
       "Lives on pocket money or a small stipend and shares a hostel room. Impulsive about fun things, "
       "ruthless about anything with a recurring fee. Loves free trials and anything that saves time before exams."),
    _a("Final-Year Job Seeker", "\U0001F393", (21, 25), 2, 3000, 249,
       ["job", "resume", "interview", "fresher", "career", "internship", "graduate", "placement"],
       ["expensive", "subscription", "enterprise", "experience required"],
       "career boosters with a visible payoff, short paid plans",
       "About to start earning but not there yet. Anxious about the future and willing to spend small amounts "
       "if it clearly helps land the first job. Always compares with a free alternative."),
    _a("Research Scholar", "\U0001F4DA", (24, 32), 3, 6000, 399,
       ["research", "thesis", "paper", "academic", "phd", "scholar", "science"],
       ["hype", "shallow", "unverified", "gimmick"],
       "accurate tools with citations, yearly institutional plans",
       "Stipend-funded and detail-obsessed. Pays for tools that save hours of reading or writing, "
       "but wants proof of accuracy and has no patience for fluff."),
    _a("Impatient Gen-Z Scroller", "\U0001F4F1", (16, 22), 1, 1800, 99,
       ["gen z", "scroll", "social", "short", "trend", " reel", "mobile", "teen", " app "],
       ["onboarding", "setup", "form", "sign up", "tutorial"],
       "instantly fun things, tiny in-app purchases",
       "Decides in three seconds and lives on the phone. Wants instant fun with zero friction. "
       "A sign-up wall or a long tutorial and they are gone."),
    _a("Gen-Z Gamer", "\U0001F3AE", (16, 24), 1, 2500, 179,
       ["game", "gaming", "esports", "stream", "console", "gen z"],
       ["grind", "pay-to-win", "slow", "boring", "ads"],
       "skins, passes and gear that make games better",
       "Spends evenings gaming and happily pays for cosmetics and gear, but only if it feels fair. "
       "Hates pay-to-win and laggy, ad-heavy experiences."),
    _a("School-Going Teen", "\U0001F9D2", (14, 17), 1, 800, 79,
       ["school", "teen", "high-school", "kid", "homework", "tutor"],
       ["fee", "subscription", "parent approval", "boring"],
       "cheap one-off buys parents will approve",
       "Has a small allowance and needs a parent's say for anything bigger. Influenced by friends and trends, "
       "easily bored, very sensitive to price."),
    _a("Anime & Pop-Culture Fan", "\U0001F38C", (15, 28), 1, 2500, 149,
       ["anime", "manga", "cosplay", "fandom", "comic", "pop-culture"],
       ["generic", "fake", "overpriced merch", "low quality"],
       "merch, collectibles, fandom communities",
       "Saves up for the next drop or convention. Passionate and loyal, but spots cheap knock-offs and "
       "cash-grabs instantly."),
    # ---- early career & creators ----------------------------------------------------
    _a("Content Creator", "\U0001F3AC", (19, 30), 2, 8000, 599,
       ["creator", "youtube", "instagram", "video", "content", "podcast", "influencer"],
       ["watermark", "slow", "generic", "limits"],
       "tools that save editing time and grow reach",
       "Posts weekly and chases growth. Income is uneven, so spends on tools that save time or boost reach, "
       "and drops anything with watermarks or hard limits."),
    _a("Busy Young Professional", "\U0001F4BC", (24, 30), 2, 15000, 599,
       ["professional", "productivity", "commute", "salary", "office", "young", "work"],
       ["time-consuming", "manual", "complex", "learn"],
       "time-savers and convenience, paid monthly or yearly",
       "Earns decently and is short on time. Happily pays to save hours, hates learning curves "
       "and anything that adds admin to the day."),
    _a("Freelancer & Gig Worker", "\U0001F9FE", (23, 38), 2, 9000, 449,
       ["freelanc", "gig", "invoice", "client", "contract", "remote"],
       ["per-seat", "lock-in", "unreliable", "hidden fee"],
       "pay-as-you-go tools that help win or bill clients",
       "Income swings month to month, so every fixed cost hurts. Loves tools that win clients or get invoices "
       "paid faster, and avoids per-seat or lock-in pricing."),
    _a("Freelance Designer", "\U0001F3A8", (22, 38), 2, 9000, 449,
       ["design", "figma", "creative", "portfolio", " art ", "illustrat"],
       ["ugly", "clunky", "rigid", "template", "cookie-cutter"],
       "beautiful, flexible tools worth showing clients",
       "Cares deeply about how things look and feel. Pays for craft and flexibility, "
       "walks away from clunky or templated products."),
    _a("Midnight Indie Hacker", "\U0001F319", (20, 35), 2, 7000, 399,
       ["indie", "hacker", "side project", "open source", "developer", "code", "maker"],
       ["closed-source", "vendor-lock", "proprietary", "bloatware"],
       "open, hackable tools at fair one-time prices",
       "Builds side projects at 2 a.m. on a tight budget. Loves open, hackable, fairly priced tools "
       "and hates lock-in."),
    _a("Frugal Bootstrapper", "\U0001FA99", (23, 40), 2, 5000, 199,
       ["bootstrap", "frugal", " free ", "side hustle"],
       ["expensive", "enterprise", "per-seat", "recurring", "overpriced"],
       "free tiers and one-time pricing",
       "Every rupee comes from their own pocket. Allergic to per-seat and recurring costs, "
       "loves free tiers, and needs a clear payback before spending."),
    # ---- business owners & founders -------------------------------------------------
    _a("Startup Founder", "\U0001F4A1", (24, 38), 3, 25000, 999,
       ["startup", "founder", "launch", "mvp", "fundrais", "saas"],
       ["unproven", "generic", "clone", "simple"],
       "leverage: tools that save weeks or win customers",
       "Always hunting leverage. Pays well for speed and differentiation, ruthless about clones "
       "and vague pitches."),
    _a("Local Shopkeeper", "\U0001F3EA", (35, 55), 3, 12000, 499,
       ["shop", "store", "kirana", "retail", "inventory", "billing", "small business", "local", "customers"],
       ["technical", "api", "code", "complex", "developer"],
       "simple things that bring customers or save effort",
       "Runs a shop, not a tech team. Wants it to just work, without jargon. Judges everything by "
       "whether it brings customers or saves daily effort."),
    _a("Online Seller", "\U0001F4E6", (22, 40), 2, 12000, 599,
       ["ecommerce", "seller", "marketplace", "listing", "dropship", "amazon", "online store"],
       ["commission", "slow", "manual", "hidden fee"],
       "automation that saves hours and lifts sales",
       "Lives on thin margins and marketplace fees. Spends only where it clearly boosts sales or saves hours."),
    # ---- tech & corporate -----------------------------------------------------------
    _a("Skeptical Senior Engineer", "\U0001F9D1\u200D\U0001F4BB", (30, 45), 4, 45000, 799,
       ["developer", "code", "api", "github", "devops", "programming", "engineer", "software"],
       ["ai-powered", "revolutionary", "disrupt", "blockchain", "magic"],
       "boring, reliable tools that work",
       "10+ years of shipping software. Well paid but has seen every hype cycle, hates buzzwords "
       "and trusts only concrete, working things."),
    _a("Early-Adopter Techie", "\U0001F680", (22, 34), 2, 12000, 799,
       ["gadget", "beta", "tech", "smart", "early adopter", "innovation", "wearable"],
       ["boring", "traditional", "basic", "legacy"],
       "new, novel things before anyone else",
       "Loves trying things first and tolerates rough edges for novelty. Bored by safe me-too products."),
    _a("Data-Driven Marketer", "\U0001F4C8", (26, 38), 3, 20000, 849,
       ["marketer", "marketing", " ads", "seo", "campaign", "growth", "brand", "analytics", "analyst", "dashboard", "data"],
       ["niche", "static", "manual", "offline", "unmeasurable"],
       "measurable tools with clear ROI",
       "Needs numbers, attribution and measurable ROI. Pays well for tools that prove their value "
       "and dismisses anything that cannot be measured."),
    _a("Mid-Career Manager", "\U0001F9ED", (32, 42), 3, 30000, 1499,
       ["manager", "team", "meeting", "career", "remote", "work"],
       ["clunky", "unreliable", "learning curve", "micromanage"],
       "reliable team tools with support",
       "Responsible for a team and a budget. Buys for reliability and support, not novelty, "
       "and needs to justify every purchase upward."),
    _a("Sales Professional", "\U0001F4DE", (23, 40), 2, 14000, 699,
       ["sales", "crm", "leads", "pipeline", "outreach"],
       ["slow", "manual", "data entry", "complex"],
       "anything that closes more deals with less admin",
       "Paid on targets, so buys tools that turn into commission. Hates data entry and slow software."),
    _a("HR & Recruiter", "\U0001F9D1\u200D\U0001F4BC", (27, 45), 3, 22000, 899,
       ["hiring", "recruit", "talent", " hr ", "interview"],
       ["spammy", "manual", "unfair", "biased"],
       "tools that speed up screening and hiring",
       "Drowning in resumes. Pays for anything that shortens time-to-hire, and is wary of tools that look biased."),
    _a("Enterprise CTO", "\U0001F3E2", (40, 55), 4, 150000, 2500,
       ["enterprise", "cto", "saas", "cloud", "integration", "compliance", "b2b", "it leader"],
       ["free", "students", "hobby", "simple", "toy"],
       "secure, scalable, supported platforms",
       "Buys for thousands of employees. Cares about security, scale, integrations and support. "
       "Toys and tiny prices look unserious."),
    _a("Corporate Procurement Lead", "\U0001F4D1", (35, 50), 4, 80000, 2200,
       ["procure", "vendor", "bulk", "b2b", "enterprise", "corporate"],
       ["beta", "untested", "individual", "freemium", "indie"],
       "proven vendors with contracts and bulk pricing",
       "Evaluates vendors on reliability, references and contracts. Negotiates hard on bulk pricing. "
       "Indie or beta products feel risky."),
    _a("Cybersecurity Auditor", "\U0001F6E1\uFE0F", (30, 45), 4, 50000, 1500,
       ["security", "privacy", "encrypt", "breach", "vulnerab", "audit", "cyber", "compliance"],
       ["unsecured", "public", "tracking", "vulnerable", "third-party"],
       "audited, encrypted, compliant products",
       "Looks for the weak spot first. Needs encryption, compliance and clear data handling. "
       "Vague security claims are red flags."),
    _a("Privacy-Paranoid User", "\U0001F575\uFE0F", (25, 50), 3, 10000, 299,
       ["privacy", "data", "track", "encrypt", "anonymous", "location"],
       ["data", "track", "cloud", "share", "location"],
       "local-first, no-tracking products",
       "Reads permissions and is allergic to tracking, cloud uploads and data sharing. Wants proof, not promises."),
    _a("Productivity Minimalist", "\u26A1", (25, 40), 3, 14000, 649,
       ["productivity", "minimal", "focus", "notes", "workflow"],
       ["slow", "bloated", "manual", "steps", "friction"],
       "fewer steps, not more features",
       "Wants fewer steps, not more features. Pays for focus and speed, hates bloat."),
    # ---- family & life stage --------------------------------------------------------
    _a("Budget-Conscious Parent", "\U0001F468\u200D\U0001F469\u200D\U0001F467", (30, 42), 3, 6000, 249,
       ["parent", "family", "kid", "child", "budget", "school", "save", "household"],
       ["subscription", "premium", "upsell", "addon"],
       "safe, simple things with obvious value for the family",
       "Juggles school fees, groceries and EMIs. Wants safe, simple, good value and smells an upsell from a mile away."),
    _a("New Parent", "\U0001F37C", (26, 36), 2, 7000, 349,
       ["baby", "newborn", "pregnan", "infant", "new parent", "toddler"],
       ["unsafe", "unproven", "complicated", "noisy"],
       "convenience and safety for the baby",
       "Sleep-deprived and spending more than planned. Pays for anything that makes the baby safer "
       "or the day easier, but wants it proven."),
    _a("Retired Skeptic", "\U0001F474", (62, 78), 4, 8000, 199,
       ["senior", "elder", "retire", "pension", "old age", "over 60", "grandparent"],
       ["app", "ai", "cloud", "subscription", "login"],
       "familiar, simple things from brands they trust",
       "Lives on a pension and prefers familiar, simple things. Wary of apps, logins and subscriptions. "
       "Values trust and plain language."),
    _a("Caregiver of Elderly Parents", "\U0001F91D", (35, 55), 3, 12000, 449,
       ["caregiver", "elder", "senior", "aging parent", "health", "medicine", "patient"],
       ["complicated", "unreliable", "small print", "hidden fee"],
       "reliable help that gives peace of mind",
       "Stretched between work and a parent's care. Pays for reliability and peace of mind, "
       "and has no time for complicated setups."),
    _a("First-Time Renter", "\U0001F511", (22, 30), 2, 6000, 299,
       [" rent", "apartment", " flat", "roommate", " move", "renter"],
       ["deposit", "long contract", "lock-in", "hidden fee"],
       "flexible, no-commitment buys",
       "Just moved out, shares a flat and has no long-term plans. Avoids commitments and lock-ins."),
    _a("New Homeowner", "\U0001F3E1", (30, 45), 3, 40000, 1999,
       [" home ", "homeowner", "house", "furniture", "interior", "renovat", "decor", "homeowner"],
       ["cheap", "flimsy", "temporary", "generic"],
       "durable, good-looking things for the long term",
       "Just bought a home with a big loan, but is investing in it. Buys quality that lasts, not throwaway stuff."),
    _a("Pet Owner", "\U0001F436", (24, 45), 2, 7000, 399,
       [" pet", " dog", " cat ", " vet", "puppy"],
       ["unsafe", "chemical", "cheap", "flimsy"],
       "safe, loved products for the pet",
       "Treats the pet as family and rarely says no to its needs. Pays for safety and quality, checks ingredients."),
    # ---- lifestyle ------------------------------------------------------------------
    _a("Fitness Enthusiast", "\U0001F3CB\uFE0F", (20, 38), 2, 7000, 449,
       ["fitness", "gym", "workout", "protein", "training", "health", "diet", "nutrition", "running", "sport"],
       ["gimmick", "unscientific", "slow results", "hype"],
       "gear and plans with visible results",
       "Trains most days and tracks progress. Pays for results and gear that works, sceptical of gimmicks."),
    _a("Mental-Wellness Seeker", "\U0001F9D8", (20, 40), 2, 5000, 349,
       ["mental", "stress", "therapy", "anxiety", "journal", "mood", "meditat", "mindful", "sleep", "wellness", "yoga"],
       ["pushy", "preachy", "guilt", "gimmick"],
       "gentle, trustworthy self-care tools",
       "Cares about calm and consistency. Pays for gentle, trustworthy tools and quits anything pushy or preachy."),
    _a("Home Cook & Foodie", "\U0001F373", (25, 50), 3, 8000, 349,
       ["recipe", "cook", "kitchen", "restaurant", "food", "meal", "organic", "calorie", "eater"],
       ["bland", "processed", "gimmick", "wasteful"],
       "things that make cooking easier or tastier",
       "Cooks most days and loves discovering new flavours. Pays for quality ingredients and gadgets that truly help."),
    _a("Frequent Traveler", "\u2708\uFE0F", (25, 45), 3, 20000, 1299,
       ["travel", "trip", "hotel", "flight", "tour", "visa", "vacation", "cab", "metro"],
       ["hidden fee", "delays", "unreliable", "cancellation fee"],
       "convenience and flexibility on the road",
       "On the road every month. Pays for convenience and flexibility, hates hidden fees and surprises."),
    _a("Budget Backpacker", "\U0001F9F3", (19, 28), 1, 3500, 249,
       ["backpack", "budget travel", "hostel", "trip", "travel", "adventure"],
       ["luxury", "overpriced", "tourist trap", "fee"],
       "the cheapest smart way to travel",
       "Travels on a shoestring and swaps tips with other travellers. Happy to rough it, never pays tourist prices."),
    _a("Eco-Conscious Millennial", "\U0001F331", (26, 40), 3, 9000, 349,
       ["sustainab", " eco", "green", "recycl", "plastic", "organic", "climate"],
       ["waste", "gimmick", "hype", "excessive", "plastic"],
       "genuinely sustainable products",
       "Cares about sustainability but sees through greenwashing. Pays more for real impact."),
    _a("Fashion & Beauty Fan", "\U0001F457", (18, 35), 2, 6000, 799,
       ["fashion", "sneaker", "clothing", "style", "outfit", "beauty", "skincare", "makeup", "cosmetic", "hair"],
       ["outdated", "ugly", "fake", "cheap-looking"],
       "trending looks and hero products",
       "Follows trends closely and spends on looks. Image and quality matter more than price."),
    _a("Deal-Hunting Bargain Seeker", "\U0001F3F7\uFE0F", (20, 55), 2, 4000, 129,
       ["discount", " deal", "coupon", "cashback", "offer", "cheap", "bargain", " sale"],
       ["full-price", "no-discount", "fixed", "annual", "pricy"],
       "only things on discount, coupons and cashback",
       "Never pays full price if a discount exists. Waits for sales and compares across five apps first."),
    _a("Affluent Premium Buyer", "\U0001F48E", (35, 55), 4, 100000, 5000,
       ["luxury", "premium", "affluent", "high-end", "gift", "exclusive"],
       ["cheap", "mass-market", "free", "crowded"],
       "premium, exclusive, best-in-class",
       "Money is not the constraint, quality and status are. Distrusts anything cheap or mass-market."),
    # ---- money ----------------------------------------------------------------------
    _a("First-Time Investor", "\U0001F4B9", (22, 32), 2, 10000, 399,
       ["first-time invest", "mutual fund", "savings", " sip", "personal finance", "beginner", "money", "expense", "loan", "credit", "upi", "crypto"],
       ["risky", "complicated", "hidden fee", "jargon"],
       "simple, low-fee ways to start investing",
       "Just started saving and nervous about risk. Wants simple, low-fee, jargon-free money tools."),
    _a("Seasoned Investor & Trader", "\U0001F3E6", (40, 60), 4, 60000, 1999,
       ["invest", "stock", "trading", "portfolio", "finance", "wealth", "trader", "equity"],
       ["guaranteed", "hype", "unregulated", "black box"],
       "serious tools with data, depth and regulation",
       "Decades of market experience. Pays for data and edge, and instantly distrusts guarantees and hype."),
    # ---- work in the field ----------------------------------------------------------
    _a("Gig Delivery Driver", "\U0001F6F5", (22, 45), 2, 5000, 199,
       ["driver", "delivery", "ride", "fuel", "vehicle", "gig", "cab"],
       ["fee", "commission", "slow", "data-heavy"],
       "things that save fuel or add earnings",
       "Paid per trip, so every rupee of fuel and every minute matters. Buys only what clearly adds to earnings."),
    _a("Farmer & Agri-Entrepreneur", "\U0001F33E", (30, 60), 3, 7000, 299,
       ["farm", "crop", "agri", "soil", "harvest"],
       ["complicated", "english-only", "unreliable", "subscription"],
       "practical, local-language tools with clear yield or savings",
       "Income follows the harvest. Practical and cautious, trusts tools proven by neighbours."),
    _a("Event & Wedding Planner", "\U0001F48D", (26, 45), 3, 20000, 899,
       ["wedding", "event", "venue", "party", "catering", "planner"],
       ["unreliable", "last-minute", "limited", "generic"],
       "reliable tools that impress clients",
       "Juggles vendors and deadlines. Pays for reliability and anything that impresses clients."),
    # ---- learning & hobbies ---------------------------------------------------------
    _a("Teacher & Tutor", "\U0001F34E", (26, 50), 3, 9000, 349,
       ["teach", "class", "lesson", "tutor", "education", "teacher", "course", "learn"],
       ["distracting", "complex", "expensive", "inaccurate"],
       "classroom-ready tools that save prep time",
       "Spends own money on classroom needs. Wants things that save prep time and actually help students."),
    _a("Language Learner", "\U0001F5E3\uFE0F", (18, 40), 2, 4000, 249,
       ["language", "english", "spanish", "translate", "speak"],
       ["boring", "robotic", "expensive", "streak guilt"],
       "fun, fluent-making practice",
       "Motivated in bursts and always comparing apps. Pays when progress is visible and practice feels fun."),
    _a("Musician & Music Lover", "\U0001F3B8", (18, 40), 2, 5000, 349,
       ["music", "song", "guitar", "band", "playlist", "concert"],
       ["low quality", "generic", "laggy", "overpriced"],
       "gear, lessons and tools that improve sound",
       "Spends on gear and gigs before comfort. Cares about quality of sound above all."),
    _a("Reader & Writer", "\U0001F4D6", (20, 60), 3, 5000, 299,
       ["book", " read", " write", "author", "novel", "story"],
       ["distracting", "ads", "cluttered", "pricy"],
       "quiet, distraction-free tools",
       "Reads and writes daily. Pays for calm, distraction-free tools and hates clutter and ads."),
    _a("DIY Maker", "\U0001F6E0\uFE0F", (20, 50), 2, 8000, 599,
       ["diy", "maker", "3d print", "craft", "hardware", "arduino"],
       ["locked", "fragile", "closed", "non-repairable"],
       "hackable, repairable hardware and kits",
       "Builds and fixes everything. Pays for good tools and kits, hates locked-down or non-repairable things."),
    _a("Car & Bike Enthusiast", "\U0001F3CD\uFE0F", (22, 45), 2, 12000, 999,
       [" car ", "bike", " ev ", "motor", "vehicle", " ride"],
       ["cheap", "fake", "unsafe", "gimmick"],
       "performance, safety and looks upgrades",
       "Spends on the machine first. Cares about performance, safety and looks, and spots gimmicks instantly."),
    _a("NGO & Social-Impact Worker", "\U0001F932", (25, 50), 3, 6000, 249,
       ["ngo", "charity", "donat", "social impact", "social-impact", "volunteer"],
       ["expensive", "commercial", "exploitative", "greenwash"],
       "affordable tools with clear social value",
       "Works on a nonprofit salary or grants. Needs discounts and clear social value for every rupee."),
]

# placeholder crowd used before a run (hexagons need n + e)
PERSONAS = ARCHETYPES


def _tier(monthly):
    if monthly < 3000:
        return "very tight budget"
    if monthly < 8000:
        return "modest budget"
    if monthly < 20000:
        return "comfortable"
    if monthly < 60000:
        return "well-off"
    return "deep pockets"


def _score(a, text):
    return sum(1 for t in a["tags"] if t in text)


def _person(a, name, in_aud):
    """One individual drawn from an archetype, with their own age, money and maturity."""
    age = random.randint(*a["age"])
    f = random.uniform(0.75, 1.3)
    cap = max(30, int(round(a["cap"] * f / 10)) * 10)
    monthly = max(500, int(round(a["monthly"] * f * random.uniform(0.85, 1.15) / 100)) * 100)
    mat = a["mat"]
    if random.random() < 0.25:
        mat = min(4, max(1, mat + random.choice((-1, 1))))
    tier = _tier(monthly)
    return {
        "n": f"{name}, {age} \u00b7 {a['role']}", "e": a["e"], "name": name, "age": age, "role": a["role"],
        "cap": cap, "monthly": monthly, "mat": mat, "maturity": MATURITY[mat], "bad": a["bad"],
        "buys": a["buys"], "in_aud": in_aud,
        "desc": f"{name}, {age}. {a['desc']}",
        "afford": f"Spare cash about \u20b9{monthly:,}/month ({tier}). Would pay up to \u20b9{cap:,} for something like this.",
    }


def build_crowd(aud, idea, n, share=MATCH_SHARE):
    """Return (people, mix). Most people (about `share`) belong to the audience the user asked for;
    the rest are outsiders so the pitch still meets some honest contrast."""
    n = max(1, min(20, int(n)))
    label = (aud or "").strip()
    text = " " + (label or idea or "").lower() + " "
    scored = sorted(((_score(a, text), random.random(), a) for a in ARCHETYPES), key=lambda t: (-t[0], t[1]))
    matched = [a for s, _, a in scored if s > 0]
    rest = [a for s, _, a in scored if s <= 0]
    random.shuffle(rest)
    names = random.sample(NAMES, n)

    if not matched:  # audience not recognised: fair general mix, nobody is an "outsider"
        picks = [(a, True) for a in random.sample(ARCHETYPES, n)]
        mix = {"matched": 0, "total": n, "label": label or "your idea", "general": True}
    else:
        k = n if n <= 3 else max(1, round(n * share))
        sc = {a["role"]: s for s, _, a in scored if s > 0}
        top = max(sc.values())
        best = [a for a in matched if sc[a["role"]] == top][:k]          # best-fitting archetypes first
        extra = random.choices(matched, weights=[sc[a["role"]] ** 2 for a in matched], k=k - len(best))
        picks = [(a, True) for a in best + extra]
        outsiders = rest[: n - k] or [matched[(k + i) % len(matched)] for i in range(n - k)]
        picks += [(a, False) for a in outsiders]
        mix = {"matched": k, "total": n, "label": label or "your idea", "general": False}
    random.shuffle(picks)
    return [_person(a, names[i], ia) for i, (a, ia) in enumerate(picks)], mix
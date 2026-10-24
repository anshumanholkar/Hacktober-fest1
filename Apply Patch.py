"""Upgrade hivemind_streamlit.py in place-safe fashion.

    python apply_patch.py                     # reads hivemind_streamlit.py, writes hivemind_streamlit_v2.py
    python apply_patch.py my_file.py

Needs personas.py in the same folder. Every edit is anchored on exact text from your file.
If any anchor is missing, nothing is written and the script lists what did not match.
"""
import pathlib
import sys

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "hivemind_streamlit.py")
OUT = SRC.with_name(SRC.stem + "_v2.py")
src = SRC.read_text(encoding="utf-8")
fails = []


def sub(label, old, new):
    """Replace one exact piece of text (must occur exactly once)."""
    global src
    n = src.count(old)
    if n != 1:
        fails.append(f"{label}: anchor found {n} times")
        return
    src = src.replace(old, new)


def swap(label, start, end, new):
    """Replace everything from `start` up to (not including) the next `end`."""
    global src
    if src.count(start) != 1:
        fails.append(f"{label}: start anchor found {src.count(start)} times")
        return
    i = src.index(start)
    j = src.find(end, i + len(start))
    if j < 0:
        fails.append(f"{label}: end anchor not found")
        return
    src = src[:i] + new + src[j:]


# --------------------------------------------------------------------------- imports + personas
sub("import", "import streamlit as st\n",
    "import streamlit as st\n\nfrom personas import ARCHETYPES, build_crowd\n")

swap("personas", "PERSONAS = [", "VOTES = {",
     "PERSONAS = ARCHETYPES  # 55 rich archetypes live in personas.py\n")

# --------------------------------------------------------------------------- Gemma 4
sub("engine label", '"ollama": "Gemma \\u00b7 Ollama (local)",', '"ollama": "Gemma 4 \\u00b7 Ollama (local)",')
sub("default model", '"ollama": "gemma3",', '"ollama": "gemma4",')
sub("gemma helper text", "'<code>ollama pull gemma3</code> once.</div>'",
    "'<code>ollama pull gemma4</code> once. Sizes: <code>gemma4:e2b</code>, <code>gemma4:e4b</code>, '\n"
    "                                            '<code>gemma4:26b</code>, <code>gemma4:31b</code>.</div>'")
sub("gemma badge", "Powered by Gemma<small>", "Powered by Gemma 4<small>")

swap("ollama call", '    if engine == "ollama":\n', '    if engine == "claude":\n', r'''    if engine == "ollama":
        try:
            d = _post("http://localhost:11434/api/chat",
                      {"model": model, "stream": False, "format": "json", "options": {"temperature": 0.8},
                       "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]},
                      timeout=180)
        except urllib.error.URLError as e:
            raise RuntimeError("Cannot reach Ollama on localhost:11434. Start it with 'ollama serve' and run "
                               f"'ollama pull {model}' once ({e.reason}).") from None
        return d["message"]["content"]
''')

# --------------------------------------------------------------------------- state: production cost + default engine
sub("state defaults", '"strict": 5, "engine": "rules", "sug_page": 0,',
    '"strict": 5, "engine": "ollama", "sug_page": 0, "cost": 100, "sim_cost": 100,')
sub("keep-alive", 'for k in ("idea", "aud", "aud_size", "price", "sl", "strict", "engine",',
    'for k in ("idea", "aud", "aud_size", "price", "cost", "sl", "strict", "engine",')
sub("load_recent", 'ss.idea, ss.aud, ss.price = x["idea"], x["aud"], x["price"]',
    'ss.idea, ss.aud, ss.price = x["idea"], x["aud"], x["price"]\n'
    '    ss.cost = x.get("cost", int(x["price"] * 0.4))')
sub("on_run cost", '"aud_size": int(ss.get("aud_size", 10)), "strict": int(ss.get("strict", 5)),',
    '"aud_size": int(ss.get("aud_size", 10)), "strict": int(ss.get("strict", 5)),\n'
    '                  "cost": int(ss.get("cost") or 0),')

# --------------------------------------------------------------------------- rule engine: maturity + affordability
swap("decide", "def decide(", "def _post(", r'''def pcard(p):
    """Persona details that travel with every verdict (shown in the crowd + insights views)."""
    return {"role": p.get("role", p["n"]), "maturity": p.get("maturity", ""), "afford": p.get("afford", ""),
            "desc": p.get("desc", ""), "buys": p.get("buys", ""), "in_aud": p.get("in_aud", True)}


def decide(p, idea, price, aud, strict=5):
    """Rule-based verdict. strict: 1 = generous ... 10 = ruthless.
    Maturity shapes behaviour: young buyers are erratic and fall for a steal, seasoned buyers are predictable
    and scrutinise value. People outside the target audience are less keen."""
    t = (idea + " " + aud).lower()
    hit = next((w for w in p["bad"] if w in t), None)
    mat = int(p.get("mat", 3))
    k = 1.5 - strict * 0.1                  # budget multiplier: 1.4 (generous) ... 0.5 (ruthless)
    spread = 0.6 - 0.1 * mat                # +-25% for impulsive buyers ... +-10% for seasoned ones
    wtp = p["cap"] * k * (1 - spread / 2 + random.random() * spread)
    if not p.get("in_aud", True):
        wtp *= 0.75                         # not their kind of product
    wtp = int(wtp / 10 + 0.5) * 10
    roast_at = 1.6 - strict * 0.06          # price / budget ratio that triggers a roast
    impulse = mat <= 2 and price <= wtp * 0.6 and strict < 7   # a real steal beats a pet peeve
    bothered = hit and not impulse and (strict >= 4 or price > wtp)
    word = None
    if hit and price > wtp * roast_at:
        vote, word = "Roast", hit
        quote_ = random.choice(ROAST_LINES).format(w=hit, p=price)
    elif bothered or price > wtp:
        vote, word = "Ignore", (hit if bothered else f"\u20b9{price}")
        quote_ = random.choice(IGNORE_LINES).format(w=word, p=price)
    else:
        vote = "Buy"
        quote_ = random.choice(BUY_LINES)
    return {"n": p["n"], "e": p["e"], "vote": vote, "wtp": wtp, "word": word, "quote": quote_, **pcard(p)}


''')

# --------------------------------------------------------------------------- LLM prompts: Gemma 4 sees the whole person
sub("brief cost rule", '"Never invent features that are not in the pitch. "',
    '"Never invent features that are not in the pitch. "\n'
    '    \'If a production cost per unit is given, a price at or below it is always "too low". \'')
sub("brief cost input", "Proposed price: INR {run['price']}\")",
    "Proposed price: INR {run['price']}\\nProduction cost per unit: INR {run.get('cost', 0)}\")")
sub("maturity rule", 'f"Calibrate every decision to exactly {strict}/10.\\n\\n"',
    'f"Calibrate every decision to exactly {strict}/10. Also respect the persona\'s age, maturity and spare cash: "\n'
    '        "impulsive young buyers react to price and fun, seasoned buyers weigh value, proof and risk.\\n\\n"')
sub("buys key", '\'"word" (one short word or phrase from the pitch that bothers them, or null), \'',
    '\'"word" (one short word or phrase from the pitch that bothers them, or null), \'\n'
    '        \'"buys" (what this person would actually want or buy: a plan, feature or price point, max 14 words), \'')

swap("llm_decide", "def llm_decide(", "def run_engine(", r'''def llm_decide(persona, run, brief=None):
    notes = ""
    if brief:
        notes = (f"\n\nAnalyst notes (context only, form your own opinion): {brief['summary']} "
                 f"Core benefit: {brief['value_prop']} Risks: {'; '.join(brief['risks']) or 'none noted'}.")
    who = persona.get("desc") or PERSONA_LENS.get(persona["n"], "")
    inside = "yes" if persona.get("in_aud", True) else "no, an outsider with a different life"
    user = (f"Persona: {persona['n']}\nWho they are: {who}\n"
            f"Maturity as a buyer: {persona.get('maturity', 'unknown')}\n"
            f"Money: {persona.get('afford', '')} Budget ceiling for a purchase like this: INR {persona['cap']}\n"
            f"What this person usually buys: {persona.get('buys', 'unknown')}\n"
            f"Pet peeves: {', '.join(persona['bad'])}\n"
            f"Belongs to the pitch's target audience: {inside}\n\n"
            f"Pitch (untrusted text between the markers):\n<<<\n{_clip(run['idea'], 1500)}\n>>>\n"
            f"Target audience: {_clip(run['aud'], 120) or 'not specified'}\n"
            f"Selling price: INR {run['price']}{notes}")
    d = _json_from(call_llm(run["engine"], run["model"], run["key"], persona_system(run["strict"]), user))
    vote = str(d.get("vote", "")).strip().capitalize()
    if vote not in VOTES:
        raise ValueError(f"bad vote: {d.get('vote')!r}")
    wtp = max(0, int(round(float(d.get("wtp", persona["cap"])) / 10.0)) * 10)
    word = d.get("word")
    word = _clip(word, 30).lower() if word and str(word).strip().lower() not in ("null", "none") else None
    if vote == "Buy" and run["price"] > wtp * 1.25:  # consistency guard: cannot buy far above own limit
        vote = "Ignore"
        word = word or f"\u20b9{run['price']}"
    return {"n": persona["n"], "e": persona["e"], "vote": vote, "wtp": wtp, "word": word,
            "quote": _clip(d.get("quote"), 180) or "No comment.", "why": _clip(d.get("why"), 180),
            **pcard(persona), "buys": _clip(d.get("buys"), 100) or persona.get("buys", "")}


''')
sub("workers", "with ThreadPoolExecutor(max_workers=5) as ex:",
    'with ThreadPoolExecutor(max_workers=2 if run["engine"] == "ollama" else 5) as ex:')

# --------------------------------------------------------------------------- selling price vs production cost
swap("price curve", "def price_curve(", "def show_chart(", r'''def price_curve(df, price, cost=0):
    """Revenue and profit per 100 visitors across a spread of prices (from below cost up to the crowd's ceiling)."""
    n = len(df) or 10
    top = int(df["wtp"].max()) if len(df) else 100
    lo = max(29, int(cost * 0.6))
    hi = max(int(top * 1.1), int(price * 1.2), lo + 100)
    pts = {max(10, int(round(lo * (hi / lo) ** (i / 8) / 10)) * 10) for i in range(9)}
    if price:
        pts.add(int(price))
    prices = sorted(pts)
    share = [int(pay_mask(df, c).sum()) / n for c in prices]
    curve = pd.DataFrame({"price": prices,
                          "buy_pct": [s * 100 for s in share],
                          "rev": [c * s * 100 for c, s in zip(prices, share)],
                          "profit": [(c - cost) * s * 100 for c, s in zip(prices, share)]})
    best = int(curve.loc[curve["profit"].idxmax(), "price"])
    return curve, best


def sweet_zone(curve, cost):
    """Prices where at least half the crowd buys AND you keep a 20% margin over cost."""
    ok = curve[(curve["buy_pct"] >= 50) & (curve["price"] >= cost * 1.2)]
    return (int(ok["price"].min()), int(ok["price"].max())) if len(ok) else None


def money(v):
    return f"-\u20b9{abs(v):,.0f}" if v < 0 else f"\u20b9{v:,.0f}"


def econ_html(df, p, cost, best, curve):
    row = curve.loc[curve["price"] == best].iloc[0]
    share = float(pay_mask(df, p).mean()) if len(df) else 0.0
    unit = p - cost
    margin = unit / p * 100 if p else 0
    profit_now = unit * share * 100
    zone = sweet_zone(curve, cost)
    if not cost:
        tone = "var(--cy)"
        note = "No production cost set, so profit equals revenue. Add a cost per unit to see real profit."
    elif p <= cost:
        tone = "var(--red)"
        note = (f"At \u20b9{p} you lose \u20b9{cost - p} on every unit (cost \u20b9{cost}). More sales only dig the hole "
                f"deeper. Price above \u20b9{cost}, ideally \u20b9{int(cost * 1.2) + 1} or more for a 20% margin, "
                "or cut the production cost.")
    elif margin < 20:
        tone = "var(--org)"
        note = (f"Margin is thin ({margin:.0f}%). Returns, discounts or ads can wipe it out. "
                f"A 20% margin starts at about \u20b9{int(cost * 1.25) + 1}.")
    else:
        tone = "var(--grn)"
        note = f"Healthy margin: {margin:.0f}% over your \u20b9{cost} cost."
    if row["profit"] <= 0:
        note += " No price in this crowd makes a profit: they will not pay enough over what it costs you to make."
    elif best != p:
        note += (f" The crowd earns you the most at \u20b9{best}: {row['buy_pct']:.0f}% would buy and you keep "
                 f"\u20b9{best - cost} per unit.")
    zone_txt = f"\u20b9{zone[0]} to \u20b9{zone[1]}" if zone else "none"
    zone_sub = "50%+ would buy and 20%+ margin" if zone else "too few would pay a healthy margin"
    return one_line(f"""
<div class="card econ" style="--c:{tone}"><div class="brief-h"><div class="lb"><i>{svg("rupee")}</i>Selling price vs production cost</div></div>
<div class="econ-grid">
<div class="es"><small>Your price vs cost</small><b>\u20b9{p} vs \u20b9{cost}</b><em>{money(unit)} per unit \u00b7 {margin:.0f}% margin</em></div>
<div class="es"><small>Profit at your price</small><b>{money(profit_now)}</b><em>per 100 visitors \u00b7 {share * 100:.0f}% would buy</em></div>
<div class="es"><small>Profit sweet spot</small><b style="color:var(--cy)">\u20b9{best}</b><em>{money(float(row["profit"]))} per 100 visitors \u00b7 {row["buy_pct"]:.0f}% buy</em></div>
<div class="es"><small>Safe buying zone</small><b>{zone_txt}</b><em>{zone_sub}</em></div>
</div><div class="econ-note">{note}</div></div>""")


def price_chart(curve, best):
    ymax = max(float(curve["profit"].max()), 1.0)
    ymin = min(float(curve["profit"].min()), 0.0)
    floor = ymax * 6 / 150
    recs = []
    for p, v, b in zip(curve["price"], curve["profit"], curve["buy_pct"]):
        v = float(v)
        kind = "best" if int(p) == int(best) else ("loss" if v < 0 else "normal")
        recs.append({"label": f"\u20b9{int(p)}", "val": max(v, floor) if v >= 0 else v, "profit": v,
                     "buy": float(b), "kind": kind})
    order = [r["label"] for r in recs]

    def grad(a, b):
        return alt.Gradient(gradient="linear",
                            stops=[alt.GradientStop(color=a, offset=0), alt.GradientStop(color=b, offset=1)],
                            x1=1, x2=1, y1=1, y2=0)

    base = alt.Chart(alt.Data(values=recs)).encode(
        x=alt.X("label:N", sort=order, scale=alt.Scale(paddingInner=0.25, paddingOuter=0.02),
                axis=alt.Axis(title=None, labelAngle=0, labelFontSize=11, ticks=False, domain=False,
                              labelPadding=6, labelColor=PALETTE[st.session_state.theme]["mut"])),
        y=alt.Y("val:Q", axis=None, scale=alt.Scale(domain=[ymin * 1.15, ymax])),
        tooltip=[alt.Tooltip("label:N", title="Price"),
                 alt.Tooltip("buy:Q", title="Would buy %", format=".0f"),
                 alt.Tooltip("profit:Q", title="Profit per 100 visitors (\u20b9)", format=",.0f")],
    )
    corner = dict(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
    layers = [base.transform_filter(f"datum.kind === '{k}'").mark_bar(color=grad(a, b), **corner)
              for k, a, b in (("normal", "#7C5CFF", "#3B6CF6"), ("best", "#2ED6A1", "#38D0E8"),
                              ("loss", "#FF5A7A", "#B8324F"))]
    return (alt.layer(*layers).properties(height=190)
            .configure_view(stroke=None).configure(background="transparent"))


''')

# --------------------------------------------------------------------------- crowd view: full person on hover
swap("focus card", "fcs += (f'<div class=\"fc{d}\"", "    if not shown:\n", r'''fcs += (f'<div class="fc{d}" data-i="{i}"><b>{r["e"]} {esc(r["n"])}</b><br>'
                f'<small style="color:var(--mut)">{esc(r.get("maturity", ""))}</small><br>'
                f'<small style="color:var(--mut)">{esc(r.get("desc", ""))}</small><br>'
                f'<small style="color:var(--mut)">\U0001F4B0 {esc(r.get("afford", ""))}</small><br>'
                f'{VOTES[r["vote"]]}, up to \u20b9{r["wtp"]}'
                f'<br><span style="color:var(--mut)">{hl(r)}</span>{why_html(r)}</div>')
''')

# --------------------------------------------------------------------------- Idea Lab: production cost input
swap("lab inputs", "c1, c2 = st.columns([1.4, 1])", "\n                render_suggestions()", r'''c1, c2, c3 = st.columns([1.4, 1, 1])
                    with c1:
                        with st.container(key="g_aud"):
                            st.markdown(label("users", "Who is it for?"), unsafe_allow_html=True)
                            st.text_input("Target Audience", key="aud", label_visibility="collapsed",
                                          placeholder="e.g. sleep-deprived college students...")
                    with c2:
                        with st.container(key="g_price"):
                            st.markdown(label("rupee", "Selling price (\u20b9)"), unsafe_allow_html=True)
                            st.number_input("Proposed Price", min_value=0, step=1, key="price",
                                            label_visibility="collapsed")
                    with c3:
                        with st.container(key="g_cost"):
                            st.markdown(label("rupee", "Cost to make (\u20b9/unit)"), unsafe_allow_html=True)
                            st.number_input("Production Cost", min_value=0, step=1, key="cost",
                                            label_visibility="collapsed")
''')

# --------------------------------------------------------------------------- crowd run: audience-matched crowd
sub("build crowd", "active_list = random.sample(PERSONAS, n_personas)  # fresh random crowd every run",
    'active_list, mix = build_crowd(p["aud"], p["idea"], n_personas)  # mostly the audience you asked for')
sub("run_info mix", '"failed_all": len(errors) > 0, "brief": brief}',
    '"failed_all": len(errors) > 0, "brief": brief, "mix": mix}')
sub("sim_cost", 'ss.results, ss.sim_price = results, p["price"]',
    'ss.results, ss.sim_price = results, p["price"]\n        ss.sim_cost = p["cost"]')
sub("recent cost", '"price": p["price"], "aud_size": n_personas, "strict": p["strict"],',
    '"price": p["price"], "cost": p["cost"], "aud_size": n_personas, "strict": p["strict"],')

# --------------------------------------------------------------------------- insights view
sub("crowd mix text", 'model = f" ({esc(info[\'model\'])})" if info["model"] else ""',
    'model = f" ({esc(info[\'model\'])})" if info["model"] else ""\n'
    '        mx = info.get("mix")\n'
    '        if not mx:\n'
    '            mixtxt = ""\n'
    '        elif mx.get("general"):\n'
    '            mixtxt = " \\u00b7 Crowd: general mix (audience not recognised)"\n'
    '        else:\n'
    '            mixtxt = (f\' \\u00b7 Crowd: <b>{mx["matched"]} of {mx["total"]}</b> match \\u201c{esc(mx["label"])}\\u201d\')')
sub("crowd mix line", "f' \\u00b7 Strictness <b>{info[\"strict\"]}/10</b></p>', unsafe_allow_html=True)",
    "f' \\u00b7 Strictness <b>{info[\"strict\"]}/10</b>{mixtxt}</p>', unsafe_allow_html=True)")
sub("curve call", "curve, best = price_curve(df, ss.sim_price)",
    'cost = int(ss.get("sim_cost", 0))\n    curve, best = price_curve(df, ss.sim_price, cost)')
sub("sweet spot label", "<small>Sweet-spot price</small>", "<small>Best-profit price (cost \u20b9{cost})</small>")
sub("econ card", '    with st.container(key="barscard"):',
    '    st.markdown(econ_html(df, p, cost, best, curve), unsafe_allow_html=True)\n'
    '    with st.container(key="barscard"):')
sub("chart title", "Which price makes the most money (per 100 visitors)",
    "Which price makes the most profit (per 100 visitors)")

swap("insight table", '    rows = "".join(\n', "# App\n", r'''    rows = "".join(
        f'<div class="tr"><span>{r.e} {esc(r.n)}</span><span><i class="chip {r.vote}">{r.vote}</i></span>'
        f'<span>\u20b9{r.wtp}</span><span>{"<mark>" + esc(r.word) + "</mark>" if isinstance(r.word, str) else "None"}</span>'
        f'<span>{esc(r.buys) or "-"}</span></div>'
        for r in df.itertuples())
    with st.container(key="tabwrap"):
        st.markdown(one_line(f"""
<div class="card"><div class="tr h"><span>Critic</span><span>Verdict</span><span>Would pay up to</span><span>What bugged them</span><span>What they go for</span></div>{rows}</div>"""),
                    unsafe_allow_html=True)
    st.markdown(persona_cards_html(ss.results), unsafe_allow_html=True)


def persona_cards_html(results):
    """One card per critic: who they are, how mature a buyer, what they can afford, what they said."""
    cards = ""
    for r in results:
        inside = r.get("in_aud", True)
        who = "In your target audience" if inside else "Outsider, not your target audience"
        cards += (f'<div class="pc{"" if inside else " out"}"><div class="pc-h"><span class="pc-e">{r["e"]}</span>'
                  f'<div><b>{esc(r["n"])}</b><small>{esc(r.get("maturity", ""))} \u00b7 {who}</small></div>'
                  f'<i class="chip {r["vote"]}">{r["vote"]}</i></div>'
                  f'<p>{esc(r.get("desc", ""))}</p>'
                  f'<div class="pc-f"><span>\U0001F4B0 {esc(r.get("afford", ""))}</span>'
                  f'<span>\U0001F6D2 Goes for: {esc(r.get("buys", "")) or "-"}</span></div>'
                  f'<div class="pc-q">\u201c{hl(r)}\u201d</div></div>')
    return one_line(f'<div class="eye" style="margin:28px 0 12px">WHO JUDGED YOU</div><div class="pgrid">{cards}</div>')


# ----------------------------------------------------------------------------
''')

# --------------------------------------------------------------------------- CSS
sub("table grid", ".tr{display:grid;grid-template-columns:2.2fr .9fr .8fr 1.2fr;",
    ".tr{display:grid;grid-template-columns:2.2fr .9fr .8fr 1.2fr 1.8fr;")
sub("new css", "@media(prefers-reduced-motion:reduce)", r'''/* cost vs price + persona cards */
.econ{margin:0 0 18px;border-color:color-mix(in srgb,var(--c,var(--cy)) 45%,var(--line))}
.econ-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:12px 0}
.es{background:var(--in);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.es small{display:block;color:var(--mut);font-size:11px;margin-bottom:4px}
.es b{display:block;font-size:20px;letter-spacing:-.5px}
.es em{display:block;font-style:normal;font-size:11px;color:var(--mut);margin-top:3px}
.econ-note{font-size:13px;border-left:3px solid var(--c,var(--cy));padding:2px 0 2px 12px}
.pgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.pc{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px}
.pc.out{border-style:dashed;opacity:.88}
.pc-h{display:flex;gap:12px;align-items:center;margin-bottom:8px}
.pc-e{font-size:28px;line-height:1}
.pc-h b{display:block;font-size:13px}.pc-h small{display:block;color:var(--mut);font-size:11px}
.pc-h .chip{margin-left:auto}
.pc p{font-size:12px;color:var(--mut);margin:0 0 10px;line-height:1.5}
.pc-f{display:flex;flex-direction:column;gap:4px;font-size:12px;margin-bottom:10px}
.pc-q{font-size:12px;border-top:1px dashed var(--line);padding-top:8px}
@media(max-width:900px){.econ-grid{grid-template-columns:repeat(2,1fr)}}
@media(prefers-reduced-motion:reduce)''')

# --------------------------------------------------------------------------- finish
if fails:
    print("NOTHING WRITTEN. These edits did not match your file:")
    for f in fails:
        print("  -", f)
    sys.exit(1)

compile(src, str(OUT), "exec")  # catches syntax slips before writing
OUT.write_text(src, encoding="utf-8")
print(f"OK: wrote {OUT}  (keep personas.py next to it, then: streamlit run {OUT.name})")
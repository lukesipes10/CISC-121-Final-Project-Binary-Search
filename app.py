"""
Spooky Mystery Solver: Binary Search Game
===============================================
A spooky interactive game where you perform binary search
to unmask the villain hiding in a numbered lineup.

The player narrows down suspects using binary search logic
(guess higher or lower) until the villain is caught and unmasked!

Author: Luke Sipes
Course: CISC-121
Deliverable: Final Term Project
AI Dislaimer: Portions of this program were written with assistance from Claude Opus 4.6,
in accordance with the Level 4 AI policy mandated by the project guidlines.
"""

import random
import gradio as gr

# ---------------------------------------------------------------------------
# Villain roster — each has a disguise name and a revealed identity
# ---------------------------------------------------------------------------
VILLAINS = [
    {"disguise": "The Phantom Shadow", "real": "Old Man Jenkins", "emoji": "👻"},
    {"disguise": "The Swamp Beast", "real": "Professor Grim", "emoji": "🐊"},
    {"disguise": "The Headless Specter", "real": "Farmer McBain", "emoji": "💀"},
    {"disguise": "The Cyber Ghoul", "real": "Tech Mogul Darcy", "emoji": "🤖"},
    {"disguise": "The Cursed Pirate", "real": "Captain Flintwood", "emoji": "🏴‍☠️"},
    {"disguise": "The Werewolf", "real": "Groundskeeper Lou", "emoji": "🐺"},
    {"disguise": "The Mummy", "real": "Dr. Sandoval", "emoji": "🧟"},
    {"disguise": "The Ghost Clown", "real": "Mr. Barnaby", "emoji": "🤡"},
]

# Game constants — 16 suspects, 4 guesses (exactly log₂(16))
# Perfect binary search wins every time. One wrong move? You lose.
NUM_SUSPECTS = 16
NUM_GUESSES = 4

# ---------------------------------------------------------------------------
# Helper: build a single suspect card's HTML
# ---------------------------------------------------------------------------
def _card(css_class, icon, num, label=""):
    """Return HTML for one suspect card with the given class, icon, and number."""
    lbl = f"<div class='suspect-label'>{label}</div>" if label else ""
    return (f"<div class='suspect-card {css_class}'>"
            f"<div class='suspect-icon'>{icon}</div>"
            f"<div class='suspect-num'>#{num}</div>{lbl}</div>")

# ---------------------------------------------------------------------------
# Game state management
# ---------------------------------------------------------------------------

def start_game():
    """
    Initialize a new game with fixed settings.

    Uses NUM_SUSPECTS (16) and NUM_GUESSES (4) — the exact binary search
    limit for 16 items. Perfect play wins; a single wasted guess may not.

    Returns a state dict and the opening HTML message for the UI.
    """
    secret = random.randint(1, NUM_SUSPECTS)
    villain = random.choice(VILLAINS)

    state = {
        "size": NUM_SUSPECTS, "secret": secret,
        "low": 1, "high": NUM_SUSPECTS,
        "attempts": 0, "max_attempts": NUM_GUESSES,
        "villain": villain, "game_over": False, "history": [],
    }

    mid = (1 + NUM_SUSPECTS) // 2
    v = villain

    intro = (
        f"<div class='intro-card'>"
        f"<h2>🔍 Detective Squad needs YOUR help!</h2>"
        f"<p>A villain disguised as <strong>{v['disguise']}</strong> "
        f"<span class='villain-emoji'>{v['emoji']}</span> "
        f"is hiding among <strong>{NUM_SUSPECTS}</strong> suspects. "
        f"You have exactly <strong>{NUM_GUESSES} guesses</strong> — "
        f"use binary search perfectly or the villain escapes!</p></div>"
        f"<div class='strategy-box'><h3>🧠 Binary Search Strategy</h3>"
        f"<div class='strategy-steps'>"
        + _step(1, "Always pick the <strong>MIDDLE</strong> of the remaining range")
        + _step(2, "If villain is <strong>HIGHER</strong> → ignore the left half")
        + _step(3, "If villain is <strong>LOWER</strong> → ignore the right half")
        + _step(4, "Repeat — each guess <strong>eliminates HALF</strong>!")
        + f"</div>"
        f"<div class='pivot-hint'>👉 Your first move: pick the middle → "
        f"<strong>#{mid}</strong></div></div>"
        f"{build_lineup_html(state)}"
    )
    return state, intro

def _step(n, text):
    """Return HTML for one strategy step."""
    return (f"<div class='strategy-step'><span class='step-num'>{n}</span>"
            f"<span class='step-text'>{text}</span></div>")

def build_lineup_html(state):
    """
    Build an HTML visual of the suspect lineup using styled cards.

    - Suspects inside [low, high] are shown as masked 🎭.
    - Suspects outside the range (eliminated) are shown as ❌.
    - If game over, the villain position shows unmasked/escaped emoji.
    """
    cards = []
    for i in range(1, state["size"] + 1):
        if state["game_over"] and i == state["secret"]:
            caught = "CAUGHT" in (state["history"][-1] if state["history"] else "")
            cards.append(_card("caught" if caught else "escaped",
                               "😱" if caught else "😈", i,
                               "UNMASKED!" if caught else "ESCAPED!"))
        elif i < state["low"] or i > state["high"]:
            cards.append(_card("eliminated", "❌", i))
        else:
            cards.append(_card("active", "🎭", i))
    return f"<div class='lineup-grid'>{''.join(cards)}</div>"


def make_guess(guess_text, state):
    """
    Process the player's guess using binary search logic.

    1. Validate input (integer within current search range).
    2. Compare guess to secret villain position.
    3. Narrow the search range (low/high bounds).
    4. Check win/loss conditions.
    5. Return updated display HTML and history log.
    """
    # Guard: game already finished
    if state is None or state.get("game_over"):
        return ("<div class='hint-card warning'>🚨 No active mystery! "
                "Click <strong>🔍 New Mystery</strong> to start.</div>", "", state)

    # Input validation
    try:
        guess = int(guess_text.strip())
    except (ValueError, AttributeError):
        return (f"<div class='hint-card warning'>⚠️ Please enter a valid number "
                f"between <strong>{state['low']}</strong> and "
                f"<strong>{state['high']}</strong>.</div>"
                f"{build_lineup_html(state)}", format_history(state), state)

    if guess < state["low"] or guess > state["high"]:
        return (f"<div class='hint-card warning'>⚠️ Suspect #{guess} is already "
                f"eliminated! Pick between <strong>{state['low']}</strong> "
                f"and <strong>{state['high']}</strong>.</div>"
                f"{build_lineup_html(state)}", format_history(state), state)

    state["attempts"] += 1
    att, max_att = state["attempts"], state["max_attempts"]
    v = state["villain"]

    # --- FOUND the villain ---
    if guess == state["secret"]:
        state["game_over"] = True
        state["history"].append(f"Guess {att}: #{guess} → ✅ CAUGHT!")
        return (
            f"<div class='hint-card success'>"
            f"<h2>🎉 WOW! You caught them in {att} "
            f"guess{'es' if att > 1 else ''}!</h2>"
            f"<p><strong>{v['disguise']}</strong> was really... "
            f"<strong>{v['real']}</strong> all along!</p>"
            f"<p class='quote'>\"If it weren't for you smart binary searcher, "
            f"I would have gotten away with it!\"</p>"
            f"<div class='stats-badge'>📊 Used {att}/{max_att} guesses</div>"
            f"</div>{build_lineup_html(state)}",
            format_history(state), state
        )

    # --- Wrong guess: narrow the range ---
    if guess < state["secret"]:
        state["low"] = guess + 1
        direction, explain = "HIGHER ⬆️", "Left half eliminated — villain is in the right half"
        state["history"].append(f"Guess {att}: #{guess} → Too low, go higher ⬆️")
    else:
        state["high"] = guess - 1
        direction, explain = "LOWER ⬇️", "Right half eliminated — villain is in the left half"
        state["history"].append(f"Guess {att}: #{guess} → Too high, go lower ⬇️")

    # --- Out of guesses ---
    if att >= max_att:
        state["game_over"] = True
        state["history"].append(f"Out of guesses! Villain was #{state['secret']}")
        return (
            f"<div class='hint-card fail'><h2>💨 The villain escaped!</h2>"
            f"<p>You used all <strong>{max_att}</strong> guesses.</p>"
            f"<p><strong>{v['disguise']}</strong> was at position "
            f"<strong>#{state['secret']}</strong> — it was "
            f"<strong>{v['real']}</strong>!</p>"
            f"<p class='explain'>💡 Remember: always guess the MIDDLE "
            f"of your range to use binary search optimally!</p></div>"
            f"{build_lineup_html(state)}", format_history(state), state
        )

    # --- Show clue + pivot hint for next guess ---
    mid = (state["low"] + state["high"]) // 2
    remaining = max_att - att
    return (
        f"<div class='hint-card clue'>"
        f"<h3>🔎 Suspect #{guess} is innocent!</h3>"
        f"<p>The villain is hiding in a <strong>{direction}</strong> "
        f"numbered position!</p>"
        f"<p class='explain'>{explain}</p></div>"
        f"<div class='status-strip'>"
        f"<span>🔎 Range: [ {state['low']} – {state['high']} ]</span>"
        f"<span>💭 Guesses left: <strong>{remaining}</strong></span></div>"
        f"<div class='pivot-hint'>👉 Next move: pick the middle → "
        f"<strong>#{mid}</strong> "
        f"<span class='pivot-formula'>"
        f"({state['low']} + {state['high']}) ÷ 2 = {mid}</span></div>"
        f"{build_lineup_html(state)}", format_history(state), state
    )


def format_history(state):
    """Format the guess history as a readable log."""
    if not state or not state.get("history"):
        return "No guesses yet."
    return "\n".join(state["history"])


def new_game():
    """Start a fresh mystery and return all UI updates."""
    state, intro = start_game()
    return intro, "No guesses yet.", "", state


# ---------------------------------------------------------------------------
# Custom CSS — Full-screen horizontal layout
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Creepster&family=Lilita+One&family=Nunito:wght@400;600;700;800&display=swap');

/* ---- GLOBAL ---- */
.gradio-container {
    background: linear-gradient(135deg, #1a0533 0%, #2d1b69 30%, #1a0533 60%, #0d0a1a 100%) !important;
    font-family: 'Nunito', sans-serif !important;
    color: #e2e0ff !important;
    padding: 6px 20px !important;
    max-width: 100% !important;
}
.gradio-container *:not(button):not(input):not(textarea) { color: #e2e0ff !important; }
.gradio-container button, .gradio-container button * { color: white !important; }
.gradio-container #new-mystery-btn, .gradio-container #new-mystery-btn * { color: #000 !important; }
.gradio-container input, .gradio-container textarea { color: #e2e0ff !important; }
.gradio-container .gap { gap: 4px !important; }

.gradio-container::before {
    content: ''; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse at 20% 80%, rgba(88,28,135,.15) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 20%, rgba(59,7,100,.12) 0%, transparent 50%);
    pointer-events: none; z-index: 0;
}

/* ---- HEADER ---- */
.title-banner h1 {
    font-family: 'Creepster', cursive !important; font-size: 2.6em !important;
    color: #7CFC00 !important; text-align: center !important; margin: 0 !important;
    text-shadow: 3px 3px 0 #2d1b69, 0 0 20px rgba(124,252,0,.3) !important;
    letter-spacing: 2px !important; line-height: 1.1 !important;
}
.subtitle-text p {
    font-family: 'Lilita One', cursive !important; font-size: 1.05em !important;
    color: #c4b5fd !important; text-align: center !important; margin: 0 !important;
}
.clue-car-banner { text-align: center; padding: 2px 0; margin: 0; }
.clue-car-banner p, .clue-car-banner em, .clue-car-banner span {
    color: #e879f9 !important; margin: 0 !important; font-size: 0.9em !important;
}
.flower-row { text-align: center; font-size: 1.1em; letter-spacing: 5px; line-height: 1; margin: 0; padding: 0; }
.flower-row p { margin: 0 !important; color: #f0abfc !important; }

/* ---- BLOCKS ---- */
.gradio-container .block {
    background: rgba(30,15,60,.85) !important; border: 1px solid rgba(139,92,246,.25) !important;
    border-radius: 12px !important; backdrop-filter: blur(8px) !important;
}
#mystery-board {
    background: rgba(30,15,60,.9) !important; border: 2px solid rgba(124,252,0,.2) !important;
    border-radius: 16px !important; padding: 8px 10px !important; min-height: 0 !important;
}

/* ---- STRATEGY BOX ---- */
.strategy-box {
    background: linear-gradient(135deg, rgba(30,58,138,.35), rgba(49,46,129,.3)) !important;
    border: 1px solid rgba(96,165,250,.3) !important; border-radius: 12px; padding: 10px 16px; margin: 8px 0;
}
.strategy-box h3 {
    font-family: 'Lilita One', cursive !important; color: #93c5fd !important;
    font-size: 1.05em !important; margin: 0 0 8px 0 !important;
}
.strategy-steps { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 16px; }
.strategy-step { display: flex; align-items: center; gap: 8px; }
.step-num {
    display: inline-flex; align-items: center; justify-content: center;
    width: 26px; height: 26px; min-width: 26px; border-radius: 50%;
    background: rgba(124,252,0,.2); border: 1px solid rgba(124,252,0,.45);
    color: #7CFC00 !important; font-family: 'Lilita One', cursive !important; font-size: 0.85em;
}
.step-text { color: #e2e0ff !important; font-size: 0.88em; line-height: 1.3; }
.step-text strong { color: #fbbf24 !important; }

/* ---- PIVOT HINT ---- */
.pivot-hint {
    background: rgba(124,252,0,.08) !important; border: 1px solid rgba(124,252,0,.3) !important;
    border-radius: 10px; padding: 8px 16px; margin: 8px 0; text-align: center;
    color: #bbf7d0 !important; font-size: 0.95em;
}
.pivot-hint strong { color: #7CFC00 !important; font-size: 1.15em; }
.pivot-formula {
    display: inline-block; background: rgba(0,0,0,.25); border-radius: 4px;
    padding: 1px 8px; margin-left: 6px; font-family: 'Fira Code', monospace !important;
    font-size: 0.8em; color: #86efac !important;
}

/* ---- SUSPECT GRID ---- */
.lineup-grid { display: grid; grid-template-columns: repeat(8,1fr); gap: 8px; padding: 10px 6px; margin: 8px 0; }
.suspect-card {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: 8px 4px; border-radius: 12px; transition: all .3s ease;
}
.suspect-card.active {
    background: linear-gradient(145deg,#3b1f7a,#4c1d95) !important;
    border: 2px solid #7c3aed !important; box-shadow: 0 3px 12px rgba(124,58,237,.3); cursor: pointer;
}
.suspect-card.active:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 6px 20px rgba(124,58,237,.5), 0 0 12px rgba(124,252,0,.15);
    border-color: #a78bfa !important;
}
.suspect-card.eliminated {
    background: rgba(30,15,40,.3) !important; border: 2px dashed rgba(100,80,130,.2) !important; opacity: .35;
}
.suspect-card.caught {
    background: linear-gradient(145deg,#065f46,#047857) !important;
    border: 2px solid #34d399 !important; box-shadow: 0 0 20px rgba(52,211,153,.4);
    animation: unmasked .6s ease 3;
}
.suspect-card.escaped {
    background: linear-gradient(145deg,#7f1d1d,#991b1b) !important;
    border: 2px solid #f87171 !important; box-shadow: 0 0 15px rgba(248,113,113,.3);
}
@keyframes unmasked { 0%,100%{transform:scale(1)} 50%{transform:scale(1.12) rotate(2deg)} }
.suspect-icon { font-size: 2.2em !important; line-height: 1; filter: drop-shadow(0 1px 4px rgba(0,0,0,.5)); }
.suspect-num { font-family: 'Lilita One', cursive !important; font-size: .9em; color: #c4b5fd !important; margin-top: 2px; }
.suspect-label { font-family: 'Creepster', cursive !important; font-size: .7em; color: #7CFC00 !important; letter-spacing: 1px; }

/* ---- CARDS (intro / clue / success / fail / warning) ---- */
.intro-card, .hint-card { border-radius: 12px; padding: 10px 16px; margin: 6px 0; }
.intro-card {
    background: linear-gradient(135deg, rgba(88,28,135,.45), rgba(76,29,149,.35)) !important;
    border: 1px solid rgba(167,139,250,.25) !important;
}
.intro-card h2 { font-family: 'Creepster', cursive !important; color: #7CFC00 !important; font-size: 1.3em !important; margin: 0 0 6px !important; }
.intro-card p { font-size: .92em; margin: 0 !important; line-height: 1.5; }
.intro-card strong, .hint-card.success strong, .hint-card.fail strong,
.hint-card.warning strong, .status-strip strong { color: #fbbf24 !important; }

.hint-card.clue {
    background: linear-gradient(135deg, rgba(88,28,135,.4), rgba(49,46,129,.35)) !important;
    border: 1px solid rgba(139,92,246,.25) !important;
}
.hint-card.clue h3 { font-family: 'Lilita One', cursive !important; color: #fbbf24 !important; font-size: 1.1em !important; margin: 0 0 4px !important; }
.hint-card.clue p { margin: 2px 0 !important; }

.hint-card.success {
    background: linear-gradient(135deg, rgba(6,78,59,.55), rgba(4,120,87,.35)) !important;
    border: 2px solid rgba(52,211,153,.45) !important;
}
.hint-card.success h2 { font-family: 'Creepster', cursive !important; color: #7CFC00 !important; font-size: 1.4em !important; margin: 0 0 6px !important; }
.hint-card.success p { color: #d1fae5 !important; margin: 4px 0 !important; }
.hint-card.success .quote {
    font-style: italic; color: #a7f3d0 !important; font-size: .9em;
    border-left: 3px solid #34d399; padding-left: 10px; margin: 8px 0 !important;
}

.hint-card.fail {
    background: linear-gradient(135deg, rgba(127,29,29,.45), rgba(153,27,27,.25)) !important;
    border: 2px solid rgba(248,113,113,.35) !important;
}
.hint-card.fail h2 { font-family: 'Creepster', cursive !important; color: #fca5a5 !important; margin: 0 0 6px !important; }
.hint-card.fail p { color: #fecaca !important; margin: 2px 0 !important; }

.hint-card.warning { background: rgba(120,53,15,.35) !important; border: 1px solid rgba(251,191,36,.25) !important; color: #fde68a !important; }
.explain { font-size: .82em !important; opacity: .8; font-style: italic; color: #c4b5fd !important; }

.status-strip {
    display: flex; justify-content: space-between; align-items: center;
    background: rgba(76,29,149,.3) !important; border: 1px solid rgba(139,92,246,.2) !important;
    border-radius: 10px; padding: 6px 16px; margin: 6px 0; font-size: .9em;
}
.range-badge {
    display: inline-block; background: rgba(124,252,0,.12) !important;
    border: 1px solid rgba(124,252,0,.25) !important; color: #7CFC00 !important;
    padding: 6px 14px; border-radius: 8px; font-family: 'Lilita One', cursive !important;
    font-size: .95em; margin-top: 6px;
}
.stats-badge {
    display: inline-block; background: rgba(52,211,153,.15); border: 1px solid rgba(52,211,153,.25);
    color: #6ee7b7 !important; padding: 4px 10px; border-radius: 6px; font-size: .85em; margin-top: 4px;
}
.villain-emoji { font-size: 1.2em; vertical-align: middle; }

/* ---- INPUTS ---- */
.gradio-container input[type="text"], .gradio-container textarea {
    background: rgba(30,15,60,.8) !important; border: 2px solid rgba(139,92,246,.3) !important;
    color: #e2e0ff !important; border-radius: 10px !important;
}
.gradio-container input[type="text"]:focus, .gradio-container textarea:focus {
    border-color: #7CFC00 !important; box-shadow: 0 0 8px rgba(124,252,0,.2) !important;
}

/* ---- BUTTONS ---- */
.gr-button-primary {
    background: linear-gradient(135deg,#7c3aed,#6d28d9) !important; border: 2px solid #a78bfa !important;
    color: white !important; font-family: 'Lilita One', cursive !important;
    font-size: 1em !important; border-radius: 10px !important; transition: all .3s ease !important;
}
.gr-button-primary:hover {
    background: linear-gradient(135deg,#8b5cf6,#7c3aed) !important;
    box-shadow: 0 3px 15px rgba(124,58,237,.4) !important; transform: translateY(-1px) !important;
}
#new-mystery-btn {
    background: linear-gradient(135deg,#34d399,#10b981) !important; border: 2px solid #6ee7b7 !important;
    color: #000 !important; font-family: 'Lilita One', cursive !important;
    font-size: 1em !important; border-radius: 10px !important;
    transition: all .3s ease !important; text-shadow: none !important;
}
#new-mystery-btn:hover {
    background: linear-gradient(135deg,#6ee7b7,#34d399) !important;
    box-shadow: 0 3px 15px rgba(52,211,153,.4) !important;
    transform: translateY(-1px) !important; color: #000 !important;
}

/* ---- LOG / LABELS / ACCORDION ---- */
#investigation-log textarea {
    background: rgba(15,8,30,.8) !important; color: #c4b5fd !important;
    font-size: .82em !important; border: 1px solid rgba(139,92,246,.15) !important; border-radius: 10px !important;
}
.gradio-container label, .gradio-container .label-wrap span {
    color: #c4b5fd !important; font-family: 'Lilita One', cursive !important; font-size: .9em !important;
}
.gradio-container .accordion {
    background: rgba(30,15,60,.5) !important; border: 1px solid rgba(139,92,246,.15) !important; border-radius: 10px !important;
}
.gradio-container .accordion .label-wrap { color: #c4b5fd !important; font-family: 'Lilita One', cursive !important; }
.accordion .prose, .accordion .prose p, .accordion .prose li,
.accordion .markdown-text, .accordion .markdown-text p, .accordion p, .accordion li { color: #e2e0ff !important; }
.accordion h3, .accordion .prose h3 { color: #7CFC00 !important; font-family: 'Creepster', cursive !important; }
.accordion strong, .accordion .prose strong { color: #fbbf24 !important; }
.accordion em, .accordion .prose em { color: #d8b4fe !important; }

/* ---- CODE / PRE ---- */
.gradio-container code {
    background: rgba(124,252,0,.1) !important; color: #7CFC00 !important;
    padding: 1px 6px !important; border-radius: 4px !important;
    border: 1px solid rgba(124,252,0,.15) !important; font-family: 'Fira Code', monospace !important;
}
.gradio-container pre {
    background: rgba(15,8,30,.8) !important; border: 1px solid rgba(139,92,246,.2) !important;
    border-radius: 6px !important; padding: 10px !important;
}
.gradio-container pre code { background: transparent !important; border: none !important; padding: 0 !important; }
.gradio-container output { color: #7CFC00 !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(15,8,30,.5); border-radius: 3px; }
::-webkit-scrollbar-thumb { background: #7c3aed; border-radius: 3px; }
"""

# ---------------------------------------------------------------------------
# Gradio UI — Full-screen, horizontal layout
# ---------------------------------------------------------------------------

def build_ui():
    """Build and return the Gradio app interface."""
    with gr.Blocks(
        title="Spooky Mystery Solver: Binary Search",
        theme=gr.themes.Base(
            primary_hue="purple", secondary_hue="green", neutral_hue="slate",
            font=gr.themes.GoogleFont("Nunito"), font_mono=gr.themes.GoogleFont("Fira Code"),
        ),
        css=CUSTOM_CSS,
    ) as demo:

        game_state = gr.State(value=None)

        # Header
        gr.Markdown("✿ ❀ ✿ ❀ ✿ ❀ ✿ ❀ ✿ ❀ ✿ ❀ ✿ ❀ ✿", elem_classes="flower-row")
        gr.Markdown("# Spooky Mystery Solver 🔍", elem_classes="title-banner")
        gr.Markdown("Use Binary Search to unmask the villain!", elem_classes="subtitle-text")
        gr.Markdown("🚐 *The Clue Car has arrived — we need help from a "
                     "detective who knows binary search!*", elem_classes="clue-car-banner")
        gr.Markdown("❀ ✿ ❀ ✿ ❀ ✿ ❀ ✿ ❀ ✿ ❀ ✿ ❀ ✿ ❀", elem_classes="flower-row")

        # Main area: game board (left) + log (right)
        with gr.Row():
            with gr.Column(scale=3):
                display = gr.HTML(
                    value=(
                        "<div class='intro-card'>"
                        "<h2>👋 Welcome, Binary Search Detective!</h2>"
                        "<p>A villain is hiding in a lineup of <strong>16 suspects</strong>. "
                        "Use <strong>binary search</strong> to unmask them in just "
                        "<strong>4 guesses</strong>!</p></div>"
                        "<div class='strategy-box'><h3>🧠 How Binary Search Works</h3>"
                        "<div class='strategy-steps'>"
                        "<div class='strategy-step'><span class='step-num'>1</span>"
                        "<span class='step-text'>Pick the <strong>MIDDLE</strong> of the range</span></div>"
                        "<div class='strategy-step'><span class='step-num'>2</span>"
                        "<span class='step-text'>Clue: villain is <strong>HIGHER</strong> or "
                        "<strong>LOWER</strong></span></div>"
                        "<div class='strategy-step'><span class='step-num'>3</span>"
                        "<span class='step-text'><strong>Eliminate half</strong> the suspects</span></div>"
                        "<div class='strategy-step'><span class='step-num'>4</span>"
                        "<span class='step-text'>Repeat until <strong>UNMASKED</strong> 😱</span></div>"
                        "</div></div>"
                        "<p style='text-align:center;color:#e879f9;margin:8px 0 0;font-size:.95em'>"
                        "👇 Click <strong style='color:#34d399'>🔍 New Mystery</strong> to begin!</p>"
                    ),
                    label="Mystery Board", elem_id="mystery-board"
                )
            with gr.Column(scale=1):
                history = gr.Textbox(label="📋 Investigation Log", lines=12,
                                     interactive=False, value="No guesses yet.",
                                     elem_id="investigation-log")

        # Controls: input + buttons in one row
        with gr.Row():
            guess_input = gr.Textbox(label="🔢 Suspect #", placeholder="e.g. 8", scale=2)
            guess_btn = gr.Button("🔍 Investigate!", variant="primary", scale=1)
            new_game_btn = gr.Button("🔍 New Mystery", variant="secondary", scale=1,
                                     elem_id="new-mystery-btn")

        gr.Markdown("✿ ❀ ✿ ❀ ✿ ❀ ✿ ❀ ✿ ❀ ✿ ❀ ✿ ❀ ✿", elem_classes="flower-row")

        # Educational accordion (collapsed)
        with gr.Accordion("📚 Binary Search — Full Explanation", open=False):
            gr.Markdown("""
### What is binary search?

**Binary search** finds an item in a **sorted** list by repeatedly splitting it in half.

### The algorithm step by step

1. **Start** with the full range: `[1 … N]`
2. **Calculate the pivot:** `mid = (low + high) // 2` *(integer division)*
3. **Compare** your guess to the target:
   - **Equal?** → Found it!
   - **Too low?** → Set `low = mid + 1`
   - **Too high?** → Set `high = mid - 1`
4. **Repeat** until found or `low > high`

### Why always pick the middle?

The middle is the **optimal pivot** — it guarantees you eliminate **exactly half** no matter what.

### Example: 16 suspects

- **Guess 1:** [1–16] → pick **#8** → "Too low!" → [9–16]
- **Guess 2:** [9–16] → pick **#12** → "Too high!" → [9–11]
- **Guess 3:** [9–11] → pick **#10** → "Too low!" → [11–11]
- **Guess 4:** [11–11] → pick **#11** → CAUGHT!

*4 guesses for 16 suspects — that's log₂(16) = 4!*

### Time complexity

- **Best case:** O(1) — found on first guess
- **Worst case:** O(log n) — maximum splits needed
- **Average case:** O(log n)
""")

        with gr.Accordion("Disclaimer", open=False):
            gr.Markdown("<p style='font-size:12px;opacity:.6'>"
                         "This is an original student project and is not "
                         "affiliated with any TV show or franchise.</p>")

        # Event handlers
        new_game_btn.click(fn=new_game, inputs=[], outputs=[display, history, guess_input, game_state])
        clear_input = lambda: ""
        guess_btn.click(fn=make_guess, inputs=[guess_input, game_state],
                        outputs=[display, history, game_state]).then(fn=clear_input, outputs=[guess_input])
        guess_input.submit(fn=make_guess, inputs=[guess_input, game_state],
                           outputs=[display, history, game_state]).then(fn=clear_input, outputs=[guess_input])

    return demo

if __name__ == "__main__":
    build_ui().launch()



#Portions of this program were written with assistance from Claude Opus 4.6 in accordance with the Level 4 AI policy mandated by this assignment.

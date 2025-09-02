from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ---------- 工具 ----------
def new_game():
    return {
        "step": "intro",
        "major": None,
        "age": 18,
        "int": 50,
        "health": 100,
        "happy": 50,
        "events": [],
        "game_over": False,
        "ending": None
    }

# ---------- 完整事件库 ----------
EVENTS = {
    "intro": {
        "text": "You reincarnate at DKU. Choose your major:",
        "options": [
            {"text": "Computer Science", "goto": "cs_track"},
            {"text": "Art & Humanity",   "goto": "art_track"}
        ]
    },

    # ── CS 线 ──
    "cs_track": {
        "text": "First CS class. What do you do?",
        "options": [
            {"text": "Listen carefully & ask TA", "goto": "cs_gift"},
            {"text": "Slack off in class",        "goto": "cs_miss"},
            {"text": "Play computer games",       "goto": "cs_warn"}
        ]
    },
    "cs_gift": {
        "text": "Received the 'Java Beginner's Manual' as a gift!",
        "effect": {"int": 15, "happy": 5, "health": 0},
        "goto": "cs_group"
    },
    "cs_miss": {
        "text": "You missed the key point.",
        "effect": {"int": -5, "happy": -5, "health": 0},
        "goto": "cs_group"
    },
    "cs_warn": {
        "text": "Be warned by the teacher.",
        "options": [
            {"text": "Change",      "goto": "cs_group"},
            {"text": "Unrepentant", "goto": "bad_ending1"}
        ]
    },

    "cs_group": {
        "text": "CS group assignment. How do you contribute?",
        "options": [
            {"text": "Actively split tasks",   "goto": "cs_early"},
            {"text": "Ask teammates for help", "goto": "cs_learn"},
            {"text": "Slack off & copy PPT",   "goto": "bad_ending2"}
        ]
    },
    "cs_early": {
        "text": "Finish early! Learn core syntax.",
        "effect": {"int": 10, "happy": 10, "health": 0},
        "goto": "cs_midterm"
    },
    "cs_learn": {
        "text": "Learn core syntax together.",
        "effect": {"int": 8, "happy": 5, "health": 0},
        "goto": "cs_midterm"
    },

    "cs_midterm": {
        "text": "CS Midterm preparation?",
        "options": [
            {"text": "Group study + tutor",         "goto": "cs_high"},
            {"text": "Review lectures + exercises", "goto": "cs_high"},
            {"text": "Last-minute cramming",        "goto": "cs_average"},
            {"text": "No review, take exam",        "goto": "bad_ending3"}
        ]
    },
    "cs_high": {
        "text": "Get high points!",
        "effect": {"int": 15, "happy": 10, "health": 5},
        "goto": "cs_extracurricular"
    },
    "cs_average": {
        "text": "Score average.",
        "effect": {"int": 5, "happy": 0, "health": -5},
        "goto": "cs_extracurricular"
    },

    "cs_extracurricular": {
        "text": "CS extracurricular. Pick one:",
        "options": [
            {"text": "ACM Competition & meet senior", "goto": "cs_acm"},
            {"text": "IT Support part-time job",      "goto": "cs_it"},
            {"text": "Stay in dorm",                  "goto": "cs_dorm"}
        ]
    },
    "cs_acm": {
        "text": "Senior invites you to solve problems?",
        "options": [
            {"text": "Cooperate",     "goto": "cs_good"},
            {"text": "Compete alone", "goto": "cs_normal"}
        ]
    },
    "cs_it": {
        "text": "Gain hardware skills. How to use salary?",
        "options": [
            {"text": "Java advanced course",  "goto": "cs_good"},
            {"text": "Buy gifts for parents", "goto": "cs_parents"}
        ]
    },
    "cs_dorm": {
        "text": "Stay in dorm. Evening plan?",
        "options": [
            {"text": "Read tech blogs",      "goto": "cs_good"},
            {"text": "Play games all night", "goto": "bad_ending5"}
        ]
    },
    "cs_parents": {
        "text": "Parents support you. Next step?",
        "options": [
            {"text": "Treat roommates to hotpot", "goto": "hotpot_ending"},
            {"text": "Buy gaming gear",           "goto": "gaming_ending"}
        ]
    },
    "cs_good":   {"ending": "🎓 CS Good Ending: Successful Tech Career"},
    "cs_normal": {"ending": "😐 CS Normal Ending: Average Graduate"},

    # ── Art & Humanity 线 ──
    "art_track": {
        "text": "First Art & Humanity lecture. What do you do?",
        "options": [
            {"text": "Actively discuss with professor", "goto": "art_gift"},
            {"text": "Doodle in notebook",              "goto": "art_doodle"},
            {"text": "Scroll social media",             "goto": "art_warn"}
        ]
    },
    "art_gift": {
        "text": "Received 'Philosophy, Art & Culture for Beginners' as a gift!",
        "effect": {"int": 5, "happy": 15, "health": 0},
        "goto": "art_group"
    },
    "art_doodle": {
        "text": "You missed the key discussion.",
        "effect": {"int": 0, "happy": -5, "health": 0},
        "goto": "art_group"
    },
    "art_warn": {
        "text": "Be warned by the professor.",
        "options": [
            {"text": "Change",      "goto": "art_group"},
            {"text": "Unrepentant", "goto": "bad_ending1"}
        ]
    },

    "art_group": {
        "text": "Art group project. How do you contribute?",
        "options": [
            {"text": "Actively split tasks & brainstorm", "goto": "art_early"},
            {"text": "Ask teammates for help & feedback", "goto": "art_learn"},
            {"text": "Slack off & only copy PPT",         "goto": "bad_ending2"}
        ]
    },
    "art_early": {
        "text": "Finish early! Enhance creativity.",
        "effect": {"int": 5, "happy": 15, "health": 5},
        "goto": "art_midterm"
    },
    "art_learn": {
        "text": "Learn artistic techniques together.",
        "effect": {"int": 3, "happy": 10, "health": 0},
        "goto": "art_midterm"
    },

    "art_midterm": {
        "text": "Art Midterm preparation?",
        "options": [
            {"text": "Visit gallery with classmates", "goto": "art_high"},
            {"text": "Practice sketches daily",       "goto": "art_high"},
            {"text": "Last-minute cramming",          "goto": "art_average"},
            {"text": "Skip prep, wing it",            "goto": "bad_ending3"}
        ]
    },
    "art_high": {
        "text": "Create stunning portfolio piece!",
        "effect": {"int": 8, "happy": 20, "health": 5},
        "goto": "art_extracurricular"
    },
    "art_average": {
        "text": "Average critique, room for growth.",
        "effect": {"int": 3, "happy": 5, "health": -5},
        "goto": "art_extracurricular"
    },

    "art_extracurricular": {
        "text": "Art extracurricular. Pick one:",
        "options": [
            {"text": "Gallery internship & curator talk", "goto": "art_gallery"},
            {"text": "Freelance design gigs",             "goto": "art_freelance"},
            {"text": "Stay in studio",                    "goto": "art_studio"}
        ]
    },
    "art_gallery": {
        "text": "Curator invites you to co-host. Your choice?",
        "options": [
            {"text": "Collaborate fully", "goto": "art_good"},
            {"text": "Work alone",        "goto": "art_normal"}
        ]
    },
    "art_freelance": {
        "text": "Earn first commission. How to use money?",
        "options": [
            {"text": "Art supplies masterclass", "goto": "art_good"},
            {"text": "Buy gifts for friends",    "goto": "art_friends"}
        ]
    },
    "art_studio": {
        "text": "Late night in studio. Plan?",
        "options": [
            {"text": "Read art theory blogs", "goto": "art_good"},
            {"text": "Binge Netflix",         "goto": "bad_ending5"}
        ]
    },
    "art_friends": {
        "text": "Friends thank you. Next step?",
        "options": [
            {"text": "Host art salon",   "goto": "art_good"},
            {"text": "Buy fancy coffee", "goto": "hotpot_ending"}
        ]
    },
    "art_good":   {"ending": "🎨 Art Good Ending: Renowned Artist"},
    "art_normal": {"ending": "😐 Art Normal Ending: Freelancer"},

    # 通用 Bad Endings
    "bad_ending1": {"ending": "💀 Bad Ending 1: GPA < 1.5"},
    "bad_ending2": {"ending": "💀 Bad Ending 2: Contribution 0"},
    "bad_ending3": {"ending": "💀 Bad Ending 3: Exam Fail"},
    "bad_ending5": {"ending": "💀 Bad Ending 5: All-nighter Downfall"},
    "hotpot_ending": {"ending": "🍲 Bad Ending: Broke & Hungry"},
    "gaming_ending": {"ending": "🎮 Bad Ending: Addicted"}
}

# ---------- 路由 ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/game", methods=["POST"])
def game():
    data = request.json
    step   = data.get("step", "intro")
    choice = data.get("choice", 0)
    state  = data.get("state", new_game())

    node = EVENTS[step]

    if "ending" in node:
        return jsonify({"game_over": True, "ending": node["ending"]})

    if "options" in node:
        opt = node["options"][choice]
        next_step = opt["goto"]
        next_node = EVENTS[next_step]

        if "effect" in next_node:
            for k in ["int", "health", "happy"]:
                state[k] = max(0, min(100, state[k] + next_node["effect"].get(k, 0)))
            state["events"].insert(0, {"icon": "📌", "text": next_node["text"]})
            next_step = next_node["goto"]

        return jsonify({
            "game_over": False,
            "state": state,
            "step": next_step,
            "node": EVENTS[next_step]
        })

if __name__ == "__main__":
    app.run(debug=True)
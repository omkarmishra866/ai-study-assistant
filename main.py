import google.generativeai as genai
import sqlite3
import os
from datetime import datetime

# ─────────────────────────────────────────
#  PUT YOUR GEMINI API KEY HERE
API_KEY = "AIzaSyBAFanTIE4aV59-SBFfVPLiglf7oI7u-jM"
# Get free key from: https://aistudio.google.com/app/apikey
# ─────────────────────────────────────────

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

DB_FILE = "study_assistant.db"

# ── DATABASE SETUP ──
def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            type      TEXT,
            question  TEXT,
            answer    TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(type_, question, answer):
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        "INSERT INTO history (type, question, answer, timestamp) VALUES (?, ?, ?, ?)",
        (type_, question, answer, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()
    conn.close()

def view_history():
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("SELECT type, question, timestamp FROM history ORDER BY id DESC LIMIT 10").fetchall()
    conn.close()
    if not rows:
        print("\n  No history yet.\n")
        return
    print("\n  ── LAST 10 SESSIONS ──")
    for i, (t, q, ts) in enumerate(rows, 1):
        print(f"  {i}. [{t}] {q[:60]}...  ({ts})")
    print()

# ── AI FUNCTIONS ──
def ask_question():
    q = input("\n  Your question: ").strip()
    if not q:
        return
    print("  🤖 Thinking...\n")
    prompt = f"You are a helpful academic tutor. Answer this clearly and concisely for a college student:\n\n{q}"
    resp = model.generate_content(prompt)
    print(f"  {resp.text}\n")
    save_to_db("Q&A", q, resp.text)

def summarize_notes():
    print("\n  Paste your notes below. Type 'DONE' on a new line when finished:")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "DONE":
            break
        lines.append(line)
    notes = "\n".join(lines)
    if not notes.strip():
        return
    print("  🤖 Summarizing...\n")
    prompt = f"Summarize these study notes in clear bullet points for a college student:\n\n{notes}"
    resp = model.generate_content(prompt)
    print(f"  📝 SUMMARY:\n{resp.text}\n")
    save_to_db("Summary", notes[:100], resp.text)

def generate_quiz():
    topic = input("\n  Enter topic (e.g. Binary Search Trees, SQL Joins, OOP): ").strip()
    if not topic:
        return
    print(f"  🤖 Generating 5-question MCQ quiz on '{topic}'...\n")
    prompt = f"""Generate exactly 5 MCQ questions on the topic: {topic}
For each question use this format:
Q1. [Question]
   a) [Option]  b) [Option]  c) [Option]  d) [Option]
Answer: [correct option with explanation]

Make it suitable for a B.Tech Computer Science student."""
    resp = model.generate_content(prompt)
    print(f"  🧠 QUIZ:\n{resp.text}\n")
    save_to_db("Quiz", topic, resp.text)

# ── MAIN MENU ──
def main():
    init_db()
    print("\n" + "="*40)
    print("     🤖 AI STUDY ASSISTANT")
    print("     by Omkar Kumar")
    print("="*40)

    while True:
        print("\n  1. Ask a question")
        print("  2. Summarize my notes")
        print("  3. Generate MCQ Quiz")
        print("  4. View chat history")
        print("  5. Exit")
        choice = input("\n  Choose (1-5): ").strip()

        if choice == "1":
            ask_question()
        elif choice == "2":
            summarize_notes()
        elif choice == "3":
            generate_quiz()
        elif choice == "4":
            view_history()
        elif choice == "5":
            print("\n  Goodbye! Keep studying! 📚\n")
            break
        else:
            print("  Invalid choice. Try again.")

if __name__ == "__main__":
    main()

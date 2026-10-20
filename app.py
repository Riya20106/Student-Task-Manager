from flask import Flask, redirect, render_template, request, session, url_for
from uuid import uuid4
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "local-demo-only-change-this")


def get_tasks():
    """Return tasks for this browser session; no external database is needed."""
    if "tasks" not in session:
        session["tasks"] = [
            {"id": "sample-1", "title": "Revise CI/CD concepts", "done": False},
            {"id": "sample-2", "title": "Prepare project demonstration", "done": True},
        ]
    return session["tasks"]


@app.get("/")
def index():
    tasks = get_tasks()
    return render_template(
        "index.html",
        tasks=tasks,
        total=len(tasks),
        completed=sum(1 for task in tasks if task["done"]),
    )


@app.post("/add")
def add_task():
    title = request.form.get("title", "").strip()
    if title:
        tasks = get_tasks()
        tasks.append({"id": str(uuid4()), "title": title[:120], "done": False})
        session["tasks"] = tasks
    return redirect(url_for("index"))


@app.post("/toggle/<task_id>")
def toggle_task(task_id):
    tasks = get_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = not task["done"]
            break
    session["tasks"] = tasks
    return redirect(url_for("index"))


@app.post("/delete/<task_id>")
def delete_task(task_id):
    session["tasks"] = [task for task in get_tasks() if task["id"] != task_id]
    return redirect(url_for("index"))


@app.get("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)

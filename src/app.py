from flask import Flask, render_template, request, redirect, url_for, flash

from src.db import init_db, get_config, set_config, get_last_log, get_logs, count_seen
from src.scheduler import init_scheduler

app = Flask(__name__)
_app_initialized = False


def create_app() -> Flask:
    global _app_initialized
    if _app_initialized:
        return app
    init_db()
    app.secret_key = get_config("secret_key") or "change-me-in-production"
    init_scheduler()
    _app_initialized = True
    return app


@app.route("/")
def dashboard():
    last_log = get_last_log()
    total_packages = count_seen()
    logs = get_logs(limit=10)
    return render_template(
        "dashboard.html",
        last_log=last_log,
        total_packages=total_packages,
        logs=logs,
    )


@app.route("/logs")
def logs_page():
    logs = get_logs(limit=200)
    return render_template("logs.html", logs=logs)


@app.route("/config", methods=["GET", "POST"])
def config_page():
    if request.method == "POST":
        for key in [
            "smtp_host",
            "smtp_port",
            "smtp_user",
            "smtp_password",
            "email_from",
            "email_to",
        ]:
            value = request.form.get(key, "").strip()
            if value:
                set_config(key, value)
        flash("Configuration enregistrée", "success")
        return redirect(url_for("config_page"))
    config = {
        key: get_config(key) or ""
        for key in [
            "smtp_host",
            "smtp_port",
            "smtp_user",
            "smtp_password",
            "email_from",
            "email_to",
        ]
    }
    return render_template("config.html", config=config)


@app.route("/trigger", methods=["POST"])
def trigger():
    try:
        from src.scheduler import run_veille_now

        run_veille_now()
        flash("Vérification lancée avec succès", "success")
    except Exception as e:
        flash(f"Erreur : {e}", "error")
    return redirect(url_for("dashboard"))


@app.route("/health")
def health():
    return {"status": "ok"}

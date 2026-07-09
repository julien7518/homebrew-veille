import logging
import threading

from apscheduler.schedulers.background import BackgroundScheduler

from src.fetcher import fetch_all
from src.db import is_seen, mark_seen, log_email_run
from src.emailer import build_html, send_email

logger = logging.getLogger(__name__)

TZ = "Europe/Paris"
scheduler = BackgroundScheduler(timezone=TZ)
_lock = threading.Lock()
_running = False


def run_veille():
    global _running
    if _running:
        logger.info("Déjà en cours d'exécution, skip")
        return
    _running = True
    try:
        logger.info("Début de la vérification Homebrew")
        packages = fetch_all()
        new_packages = [p for p in packages if not is_seen(p.name)]
        logger.info("%s paquets trouvés, %s nouveaux", len(packages), len(new_packages))

        if not new_packages:
            log_email_run(
                "skip", packages_count=0, error_message="Aucun nouveau paquet"
            )
            logger.info("Aucun nouveau paquet, email non envoyé")
            return

        for p in new_packages:
            mark_seen(p.name, p.kind)

        html = build_html(new_packages)
        send_email(
            subject=f"Veille Homebrew — {len(new_packages)} nouveau(x) paquet(s)",
            html_body=html,
        )
        log_email_run("sent", packages_count=len(new_packages))
        logger.info("Email envoyé avec %s paquet(s)", len(new_packages))
    except Exception as e:
        log_email_run("error", error_message=str(e))
        logger.exception("Erreur lors de la vérification")
    finally:
        _running = False


def run_veille_now():
    run_veille()


def init_scheduler():
    if not scheduler.get_job("daily_veille"):
        scheduler.add_job(run_veille, "cron", hour=8, minute=0, id="daily_veille")
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler démarré — vérification quotidienne à 08:00 (Europe/Paris)")

# Homebrew Veille

Automatic monitoring of new Homebrew packages (formulae + casks) with a web dashboard.

Every day at 8 AM, it fetches the Homebrew API, detects new packages, and sends a summary email (name, version, description, homepage link).

## Deployment

```bash
docker compose up -d --build
```

Configure SMTP at `http://localhost:8080/config`

## Usage

| Route           | Description                            |
| --------------- | -------------------------------------- |
| `GET /`         | Dashboard — last check, stats, history |
| `GET /logs`     | Full execution history                 |
| `GET /config`   | SMTP configuration                     |
| `POST /trigger` | Run a manual check                     |
| `GET /health`   | Healthcheck                            |

## Environment

| Variable  | Default           |
| --------- | ----------------- |
| `PORT`    | `8080`            |
| `DB_PATH` | `/data/veille.db` |
| `TZ`      | `Europe/Paris`    |

## License

MIT License. See [LICENSE](LICENSE.md)

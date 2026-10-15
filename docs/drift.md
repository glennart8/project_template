# Drift

## Så når en användare systemet

```
Webbläsare
   │  https
Entra Application Proxy     ← loggar in användaren, skickar identiteten som headers
   │
Server: Caddy (port 80)     ← enda öppna porten
   ├── /api/*  →  backend (FastAPI)  →  Postgres
   └── övrigt  →  frontend (färdigbyggda filer)
```

| Begrepp | Betyder |
|---|---|
| Container | Ett paketerat program med allt det behöver. Körs likadant överallt. |
| Image | Ritningen en container startas från, byggd från en `Dockerfile`. |
| Docker Compose | En fil som beskriver alla containrar och hur de hänger ihop. |
| Reverse proxy | Den enda dörren in. Tar emot alla anrop och skickar dem vidare. Här: Caddy. |
| Healthcheck | `/api/health` — svarar `ok` om appen lever. |

## Första driftsättningen

På en Linuxserver med Docker:

```bash
git clone <repo> && cd <repo>
echo "POSTGRES_PASSWORD=<långt lösenord, bara bokstäver och siffror>" > .env
chmod 600 .env
docker compose -f docker-compose.prod.yml up -d --build
```

Spara lösenordet i kommunens lösenordsvalv. `.env` finns bara på servern.

## Uppdatera

```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

Backend kör nya migrationer själv vid start.

## Checklista innan systemet tas i drift

- [ ] **Brandväggen släpper bara in App Proxy-connectorn** till port 80. Annars kan
      vem som helst skriva inloggningsheadern själv och bli vem som helst.
- [ ] Enterprise-appen i Entra skickar headerna `x-control-header`,
      `x-control-displayname-header` och `x-control-group-header`.
- [ ] Användare och grupper är tilldelade appen i Entra («Assignment required»).
- [ ] Backup av databasen (`pg_dump`) och av uppladdade filer, till en annan maskin.
- [ ] **En återläsning har provats.** En backup som aldrig lästs tillbaka är ingen backup.
- [ ] Någon har ansvar för att uppdatera servern och bygga om images.

## Det mallen redan sköter

- `restart: always`: systemet startar efter en omstart av servern.
- Loggrotation: loggarna fyller inte disken.
- Backend och databas har ingen öppen port.
- Containrarna körs inte som root.
- API-dokumentationen är avstängd, och testinloggning stoppas vid start.

Övervakning, CI och https ända fram till servern: se [extra.md](extra.md).

## Felsökning

```bash
docker compose -f docker-compose.prod.yml ps            # mår allt bra?
docker compose -f docker-compose.prod.yml logs -f backend
curl http://localhost/api/health
```

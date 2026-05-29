.PHONY: dev-up dev-down dev-logs dev-logs-deployer dev-logs-anvil dev-db prod-up prod-down

# --- Entorno de Desarrollo ---

dev-up:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d

dev-down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down

dev-down-v:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v

dev-logs:
	docker compose logs -f backend

dev-db:
	docker exec -it db psql -U postgres -d depfund


# --- Candidato a Producción ---

prod-up:
	docker compose up --build -d

prod-down:
	docker compose down

prod-down-v:
	docker compose down -v

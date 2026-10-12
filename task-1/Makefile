.PHONY: up down logs

COMPOSE := docker compose --project-name task-5-1

up:
	$(COMPOSE) up -d
	@echo "Airflow UI: http://localhost:8080"
	@echo "Mailpit UI: http://localhost:8025"

down:
	$(COMPOSE) down --timeout 0 --remove-orphans --volumes

logs:
	$(COMPOSE) logs -f

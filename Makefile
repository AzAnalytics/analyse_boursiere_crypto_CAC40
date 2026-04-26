.PHONY: help install test lint format clean run docs

help:
	@echo "Analyse Boursière & Crypto - Commandes disponibles"
	@echo "=================================================="
	@echo "  make install       - Installer les dépendances"
	@echo "  make test          - Lancer les tests"
	@echo "  make test-cov      - Tests + coverage report"
	@echo "  make lint          - Linter le code (flake8)"
	@echo "  make format        - Formater le code (black, isort)"
	@echo "  make clean         - Supprimer les fichiers temporaires"
	@echo "  make run           - Lancer le pipeline d'orchestration"
	@echo "  make streamlit     - Lancer l'app Streamlit"

install:
	pip install -r requirements.txt
	pip install -e ".[dev]"

test:
	pytest -v

test-cov:
	pytest -v --cov=core --cov=data_layer --cov=utils --cov-report=html

lint:
	flake8 core data_layer utils config tests

format:
	black core data_layer utils config tests
	isort core data_layer utils config tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov *.egg-info dist build

run:
	python orchestrate.py

streamlit:
	streamlit run app/main.py

docs:
	@echo "📖 Documentation disponible dans CLAUDE.md et REFACTORING_SUMMARY.md"
	@cat CLAUDE.md | head -50

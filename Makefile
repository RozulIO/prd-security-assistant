# Author = Adrian Puente Z. <ch0ks>
# Date = Sunday, December 14, 2025
# Version = 0.9

# Makefile for the AI-Guided Risk Assessment Assistant

# Define variables
PYTHON ?= python3
PEM_DIR := .venv
PIP := $(PEM_DIR)/bin/pip
STREAMLIT := $(PEM_DIR)/bin/streamlit

.PHONY: all install run clean lint

all: run

## install: Install Python dependencies using pip from requirements.txt
install:
	@echo "Installing Python dependencies..."
	$(PYTHON) -m venv $(PEM_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Dependencies installed."

## run: Start the Streamlit application
run:
	@echo "Starting Streamlit application..."
	$(STREAMLIT) run app.py --server.port $(PORT) --server.address 0.0.0.0

## clean: Remove temporary files, logs, and Python environment
clean:
	@echo "Cleaning up temporary files, logs, and Python environment..."
	rm -rf temp/
	rm -f app.log
	rm -rf $(PEM_DIR)
	@echo "Cleanup complete."

## lint: Run linting and formatting checks (placeholder for future tools like ruff, black, etc.)
lint:
	@echo "Running linting and formatting checks... (Not yet implemented)"
	# $(PEM_DIR)/bin/ruff check .
	# $(PEM_DIR)/bin/black .

# Helper to display all commands
help:
	@grep -E '^##' $(MAKEFILE_LIST) | sed -E 's/## (.*): /\1:\t/' | column -t -s ':'
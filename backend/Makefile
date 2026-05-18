# Food Store Backend Commands

.PHONY: test test-cov test-cov-html install

# Run all tests
test:
	python -m pytest tests/ -v

# Run tests with terminal coverage report
test-cov:
	python -m pytest tests/ --cov=app --cov-report=term-missing

# Run tests with HTML coverage report
test-cov-html:
	python -m pytest tests/ --cov=app --cov-report=html
	@echo "HTML report generated in htmlcov/index.html"

# Install dependencies
install:
	pip install -r requirements.txt

# Run dev server
dev:
	uvicorn app.main:app --reload

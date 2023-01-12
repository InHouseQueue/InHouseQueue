test:
	pytest -rf \ 
		--cov-context=test --cov-report=xml \
		-n auto

.PHONY: help
help:
	@echo " == execute python test on some python .venv == "
	@echo "type 'make test-python' to execute python test with pytest"
	@echo ""


.PHONY: test-python
test-python:
	pytest ./test -vv --cov=./src/{target_test_module} --cov-report=html

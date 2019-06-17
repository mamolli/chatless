.PHONY: test deploy
.DEFAULT_GOAL := deploy

test:
	pytest -sv --cov=chatless
deploy:
	serverless deploy -f chatbot
	serverless logs -f chatbot -t

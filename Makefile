help:
	@printf "Available Makefile commands:\n\n"
	@printf "run -> [ Builds docker image and runs application ]\n"
.PHONY: help

run:
	@echo "Building docker image and running [url-scraper]"
	@docker build -t url-scraper .
	@docker run -it --rm --name url-scraper url-scraper
.PHONY: run

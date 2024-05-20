# Stage 1: Builder/Compiler
FROM python:3.8.13 as builder
RUN apt update && \
	apt install --no-install-recommends -y build-essential gcc

RUN pip3 install --upgrade pip

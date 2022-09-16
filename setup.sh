#!/usr/bin/bash
docker volume create \
	--opt type=none \
	--opt device='$(pwd)'/../../volumes/temperatura \
	--opt o=bind \
	pg_temperatura


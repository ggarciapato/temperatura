#!/usr/bin/bash
mkdir "$(pwd)"/../../volumes/temperatura

docker volume create \
	--opt type=none \
	--opt device="$(pwd)"/../../volumes/temperatura \
	--opt o=bind \
	pg_temperatura


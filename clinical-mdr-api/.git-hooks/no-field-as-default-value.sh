#!/usr/bin/env bash

RED=$'\e[0;31m'
NC=$'\e[0m'

grep -Przl ".*:.* = (Field\(|\([\n\s]*Field\()|.*: \([\n\s]*.*[\n\s]*\) = Field\(" clinical_mdr_api consumer_api
if [ $? -eq 0 ]; then
    printf "\n${RED}In these files 'pydantic.Field' is assigned as a default value. Use 'typing.Annotated' instead.${NC}\n"
    exit 1
fi
#!/bin/bash

export $(jq -r 'to_entries|map("\(.key)=\(.value)")|.[]' /shared/db_info.json)
#!/bin/bash
set -e

export SPARQL_ENDPOINT=http://localhost:9090/query
export SPARQL_USER=admin
export SPARQL_PASS=admin

cli="blueprint-ui-config-initializer/cli.js"

node --no-deprecation $cli fetch-classes
python blueprint-config-tui/main.py --item-type classes
less classes.ttl

node --no-deprecation $cli fetch-links
python blueprint-config-tui/main.py --item-type links
clear
less links.ttl

node --no-deprecation $cli fetch-details
python blueprint-config-tui/main.py --item-type details
clear
less details.ttl

node --no-deprecation $cli generate-config


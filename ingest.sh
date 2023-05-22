# Bash script to ingest data
# This involves scraping the data from the web and then cleaning up and putting in Weaviate.
# Error if any command fails
set -e
# wget -r -A.html --wait 1 https://help.dexem.com/call-tracking/ -P sources/
# wget -r -A.html --wait 1 https://www.dexem.com/ -P sources/
wget -r -A.html --wait 1 https://aide.dexem.com/call-tracking/ -P sources/
wget -r -A.html --wait 1 https://aide.dexem.com/call-manager/ -P sources/
wget -r -A.html --wait 1 https://aide.dexem.com/serveur-vocal-interactif/ -P sources/
wget -r -A.html --wait 1 https://blog.dexem.com/ -P sources/

python3 ingest.py

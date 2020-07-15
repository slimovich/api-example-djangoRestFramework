> ### 🛠 Status: WIP
>
> *Under developement, WIP. Be patient.*

# Overview

Implement an API using django and djangorestframwork

# Features

- /towns - ​Returns a list of towns.
- /aggs ​- Returns aggregation results on towns’ populations
- /query ​- Returns the generated SQLite query for the JSON query given as input
  
# Quick start

- install the dependencies locally
```bash
./setup/scripts/install
```

- migrate the database
```bash
./setup/scripts/migrate
```

- populate the database
```bash
./setup/scripts/populate_db
```

- run unit test
```bash
./setup/scripts/test
```

- run the server
```bash
./setup/scripts/run
```

# Test

Use the script populate_db to populate data base with src/data/French_Towns_Data.csv

 

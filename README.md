# light_the_lamp
A custom fantasy hockey platform

*Version Roadmap*

# 0.1.0
- ~~start todo list~~
- ~~implement version control module~~
    - ~~version dataclass~~
- ~~version.py~~
- ~~git push script~~

# 0.2.0
- ~~build database handler class~~
- ~~initialize database modules~~
    - ~~each table has a module with a version labeled python script~~
        - ~~table api~~
        - ~~associated dataclass~~
        - ~~associated testing functions~~
    - ~~each table's __init__.py handles version control~~
        - ~~default to latest code version~~
        - ~~allow for importing older apis~~

# 0.3.0
- ~~build team table class~~
    - ~~api~~
    - ~~dataclass~~
    - ~~test function~~

# 0.4.0
- build player table class
    - api
    - dataclass
    - test function

# 0.5.0
- build game table class
    - api
    - dataclass
    - test function

# 0.6.0
- build player stat table class
    - api
    - dataclass
    - test function

# 0.7.0
- build user table class
    - api
    - dataclass
    - test function

# 0.8.0
- build user picks table class
    - api
    - dataclass
    - test function

# 0.9.0
- build user stats table class
    - api
    - dataclass
    - test function

# 0.10.0
- build user matchups table class
    - api
    - dataclass
    - test function

# 0.11.0
- update database class
    - plug all the table objects in
    - build wrapper for test functions with option flags

# 0.12.0
- build logger
    - handler for database test results

# 1.0.0
- document existing code
    - move version roadmap
    - readme to walk through code organization and architecture


*Architecture*


    build backend
    - player tracking
        - theodds gives csv
        - nhl api may give json, and I'll have to use it to track performance
          anyways

    - data update system
        - cron job updates local data
            - every 30 minutes before the start of a the game until 4 hours 
              after the game ends
                - roster information
                - player stats (if available)
            - daily
                - confirm the validity of unverified games from at least two
                  two days ago

    
    build api
    - flask

    
    sql schema
    - team object
        - team rowid
        - conference
        - division
        - team location
        - team name
        - team abbrev

    - player object
        - player rowid (maybe make this nhlid)
        - player nhlid
        - team rowid
        - roster status (injured, scratch, active)
        - player name

    - game object
        - game rowid
        - game start time
        - game status (before, first, second, third, intermission, end)
        - game clock
        - home team rowid
        - home team points
        - away team rowid
        - away team points

    - player stat object
        - stat rowid
        - player rowid
        - game rowid
        - shots on goal
        - goals
        - assists

    - user object
        - user rowid
        - user username
        - user password
        - user email

    - user picks object
        - picks rowid
        - player #1 rowid
        - player #1 LTL points
        - player #2 rowid
        - player #2 LTL points
        - player #3 rowid
        - player #3 LTL points
        - player #4 rowid
        - player #4 LTL points
        - player #5 rowid
        - player #5 LTL points

    - user stats object
        - u_stats rowid
        - user rowid
        - user total matches
        - user total wins
        - user total ties
        - user total LTL points
        - user streak

    - user matchup object
        - matchup rowid
        - home user rowid
        - away user rowid
        - pick/pass
        - home user LTL points
        - away user LTL points
        - result (home, tie, away)


    build frontend
    - build in godot
        - HTTP nodes to receive data from the api



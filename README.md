# WARNING 
#### Incomplete, may or may not work, errors aren't handled properly \n I don't know if I'll complete it due to legal reasons but for now if you can add data and use mongodb you can use it on your own server or local host


# stream-save

- create an account at https://www.mongodb.com/
- build a database
- choose free tier plan
- choose cluster name or use default
- create cluster
- create adn add a database user by adding username and password (make be different from your account)
- scroll down in add ip entries, ip address field enter "0.0.0.0" without inverted commas, click add entry
- click finish and close
- go to database
- click connect
- click connect your application
- copy your db url in 2nd box, make sure "Include full driver code example" checkbox is unchecked
- go to config.py
- replace 'YOUR_DB_URL' with db url you just copied, make sure it's inside inverted commas
- now you can either host it in server or host it locally
- copy git repo and run 'easy_add_remove.py' to add/remove data
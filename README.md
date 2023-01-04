# Disclaimer 
###### Not me nor mongodb are responsible for whatever data user host in your own database this app is just a tool to add and remove data in mongodb in stremio format. Only user will be responsible for whatever they add

# WARNING 
###### errors aren't handled properly as I don't have much time right now if you encounter any error or problem feel free to open a GitHub issue


---
##### Please don't make addon public nor install any stream-save public addon reason being the hoster will be able to see your cluster username, password which will give them access to your database, its not the same as having access to your mongo account but its bad enough

# Prerequisites

- create an account at https://www.mongodb.com/
- build a database
- choose free tier plan
- choose cluster name or use default
- create cluster
- create and add a database user by adding username and password (make be different from your account)
- scroll down in add ip entries, ip address field enter "0.0.0.0" without inverted commas, click add entry
- click finish and close
- go to database
- click connect
- click connect your application
- copy your db url in 2nd box, make sure "Include full driver code example" checkbox is unchecked
- go to addon configure page and install addon


# setup

- go to [render.com](https://render.com)
- create an account
- go to dashboard click "+new" and choose "web service"
- scroll down in public git repository field and enter repo address
- choose a name it can be anything, i highly recommend you not to choose name "stream-save"  instead choose more unique name or append some value to stream save example: "stream-save-fskskjsdf", reason being if you choose a normal name anyone can access to your addon while it doesn't give them access to your database it still pose some problems so its better if you choose a unique name and share it with your friends and family only
- scroll down to start command field it should be "gunicorn app:app" change it to "gunicorn wsgi:app"
- create web service, it'll take few minutes once is done you'll hv ur addon url which will be something like "name[.onrender.com](https://stream-save-74rhf6.onrender.com/)"
- go to url configure and install addon

# usage


- go to https://www.imdb.com/
- search your movie/show
- in the end of url there is id starting with tt example:- "tt0944947" copy that
- go to addonurl/manage page of addon
- follow instructions there if page redirects to success it'll be added into your database

NOTE:- when adding single episode, suppose you're adding s1 ep8 of some series add in this format
 imdbid:1:8

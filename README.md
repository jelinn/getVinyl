# getGizz.py 

## Use Python to get the limited edition 7" singles from the hit band KGATLW

## Collect them all!

This script :
- scrapes pdoom on a recurring basis using python requests
- parses the page and pulls all the products listed using python BeautifulSoup. Stores results in sqlite db.
- alerts via discord on new and removed products. 

To use: 
- Set discord webhook URL to env variable -
```
export DISCORD_WEBHOOK="yourURLhere"
```

Install python dependencies: 
```
pip install -r requirements.txt
```

- Set the sleep time (in seconds) using the waitTime var - default is 5 mins (300 seconds)

```
waitTime = 300
```


- Run the script in the background

```
python getGizz.py &
```
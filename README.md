# Mochi

**Special thanks to [@Mayank](https://github.com/MAYANK-T0MAR), the most talented full stack dev i know, for making this project possible. He created [mochi-client](https://github.com/MAYANK-T0MAR/mochi-client), the Frontend UI that lets users interact with Mochi's Backend APIs.**

### Table of contents
- Mochi and its features
- endpoints of Mochi's backend APIs and other related details
- stack and requirements

## What is Mochi?
- Mochi is a url shortener built with FastAPI and SQLModel. It supports custom alias, expiry choice, analytics and most notably a shortcut shortener, which can be used directly from the address bar of the browser.

### notable features
- **custom alias**: user can select the code/alias that is appended to the shortened url.
- **expiry choice**: user can choose whether the url ill expire after 1 hour, 1 day, 1 week, 1 month or never. 
- **analytics**: user can check total clicks, unique visits and click time history through the analytics feature.
- **direct shortener**: user can shorten an url blazingly fast directly through the browser address/URL bar without visiting the frontend.
- **url delete**: user can delete the shortened url from the server, giving the user neccessary control.
- **fast redirection**: the url is immdiately redirected to the main address when the shortened url is clicked.
- **No registration/login required**: user can directly start using the app without any auth demands.

## Endpoints and request body schema

### Endpoint: '/shorten'
Method: POST
Request body schema:
```
{
  "url": "string",
  "custom_code": "string",
  "expiry": "string"
}
```
Note: 'url' is a mendatory field while 'custom_code' and 'expiry' are optional. url only takes a full url that starts with https:// or http://
Eg with all fields:
```
{
  "url": "https://averylongurlwithunneccessarystuff.com",
  "custom_code": "mine",
  "expiry": "1w"
}
```
or as simply
```
{
  "url": "https://averylongurlwithunneccessarystuff.com"
}
```
Response schema example:
```
{
  "short_url": "https://mochi-production.up.railway.app/8q_GS0"
}
```

### Endpoint: '/direct'
Method: GET
Query parameter schema:
```
https://mochi-production.up.railway.app/direct?url=the_long_url&custom_code=string&expiry=string
```
Note: 'url' is a mendatory parameter while 'custom_code' and 'expiry' are optional. url only takes a full url that starts with https:// or http://
Eg with all parameters:
```
https://mochi-production.up.railway.app/direct?url=https://musings-production.up.railway.app&custom_code=rants&expiry=1w
```
or as simply
```
https://mochi-production.up.railway.app/direct?url=https://musings-production.up.railway.app
```
Response schema example:
```
{
  "short_url": "https://mochi-production.up.railway.app/8q_GS0"
}
```

## Endpoint: '/analytics'
Method: GET
Query parameter schema:
```
https://mochi-production.up.railway.app/direct?url=the_short_url
```
Note: 'url' is a mendatory parameter. url only takes a full url that starts with https:// or http://
Eg with all parameters:
```
https://mochi-production.up.railway.app/direct?url=https://musings-production.up.railway.app
```
Response schema example:
```
{
  "shortened_url": "https://mochi-production.up.railway.app/2Kl7-T",
  "redirects_to": "https://musings-production.up.railway.app",
  "total_clicks": 2,
  "unique_visits": 1,
  "clicks_time_history": [
    "2025-08-12T08:13:09.147266",
    "2025-08-12T08:13:48.704528"
  ]
}
```

## Endpoint '/{code}'
Method: GET

Note: this route recieves the request when the user types the short url in the browser address bar and click enter. It redirects the user to the targetted address.

Eg:
```
https://mochi-production.up.railway.app/2Kl7-T
```

## Endpoint '/'
Method: GET
Response: "welcome to mochi"

### curl command examples
```
curl -X 'GET' \
  'https://mochi-production.up.railway.app/' \
  -H 'accept: application/json'

curl -X 'POST' \
  'https://mochi-production.up.railway.app/shorten' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "https://github.com/synbhwl",
  "custom_code": "syn",
  "expiry": "1d"
}'

curl -X 'GET' \
  'https://mochi-production.up.railway.app/direct?url=https://github.com/synbhwl&custom_code=synbhwl&expiry=1w' \
  -H 'accept: application/json'

curl -X 'GET' \
  'https://mochi-production.up.railway.app/analytics?url=https://mochi-production.up.railway.app/synbhwl' \
  -H 'accept: application/json'

Note: use the redirect route in the browser by simply entering the short url and pressing enter.
```

## stack and requirements
Mainly:
- fastapi==0.103.2
- pydantic==2.5.3
- python-dotenv==0.21.1
- sqlmodel==0.0.24
- uvicorn==0.22.0
To see all dependencies, refer to [requirements.txt](https://github.com/synbhwl/mochi/blob/main/requirements.txt)

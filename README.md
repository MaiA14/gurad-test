# Streamer
A Fast API app that integrate with a stream.

## Features
- HTTPS (Bonus)
- Handle data according rules config (flexible)
- Support both partial & complete objects of supplied proto
- Validate specified headers
- Normalizing data
- Route data to downstream services based on a configuration file.
- Stats of stream (Bonus)
- Get current rules
- Update rules

## Running this server 

```bash
POST https://satisfied-berty-mai2-b6a31fff.koyeb.app/stream_start

```
> :memo: **Note:** No need to pass body in order to get data. The required parameters are stored in the config file.
<br>
Reasons: 
<br>

- Accessibility - this POST request won't work with a private email, because the hiring url supports the email you supplied. 

- Security - configuration files or environment variables can be protected with access controls and encryption, ensuring that only authorized processes or personnel can access the key.


## Running this server locally

install requirements:
```bash
pip install -r requirements.txt

```
Run the server:
```bash
python3.8 -m uvicorn main:app --reload

```


## Data:

- Original data from stream: 
<img src="https://i.ibb.co/p1PmhP8/3.png" alt="image" width="600" height="auto">

- Normalizing data:
<img src="https://i.ibb.co/sJLPmxc/Screenshot-2024-08-09-at-21-44-25.png" alt="image" width="600" height="auto">

- Matched rules:
<img src="https://i.ibb.co/xhBjjwg/Screenshot-2024-08-11-at-3-36-12.png" alt="image" width="600" height="auto">

- Stats (Bonus) - Retrieve the current metrics
```bash
GET https://satisfied-berty-mai2-b6a31fff.koyeb.app/stats

```

<img src="https://i.postimg.cc/hGYwPwvW/Screenshot-2024-08-10-at-23-04-33.png" alt="image" width="600" height="auto">


- Rules get - Retrieve the current rules from the configuration
```bash
GET https://satisfied-berty-mai2-b6a31fff.koyeb.app/get_rules

```

<img src="https://i.ibb.co/qRnXR1R/Screenshot-2024-08-11-at-3-22-29.png" alt="image" width="600" height="auto">


- Update rules - Update the rules from the configuration.
```bash
POST https://satisfied-berty-mai2-b6a31fff.koyeb.app/update_rules

```

<img src="https://i.ibb.co/dcCs9g2/Screenshot-2024-08-11-at-3-25-04.png" alt="image" width="600" height="auto">


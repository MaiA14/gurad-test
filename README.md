# Streamer
A Fast API app that integrate with a stream.

## Features
- HTTPS 
- Handle data according rules config (flexible)
- Support both partial & complete objects of supplied proto
- Validate specified headers
- Normalizing data
- Route data to downstream services based on a configuration file.

## Running this server 

```bash
POST https://satisfied-berty-mai2-b6a31fff.koyeb.app/stream_start

```
> :memo: **Note:** No need to pass body in order to get data. The required parameters are stored in config file.
<br>
Reasons: 
<br>

- Accessibility - this POST request won't work with a private email, because the hiring url supports the email you supplied. Private email gets status code 401 - Unauthorized.

- Security - configuration files or environment variables can be protected with access controls and encryption, ensuring that only authorized processes or personnel can access the key.

## Data:

- Original data from stream: 
<img src="https://i.ibb.co/p1PmhP8/3.png" alt="image" width="600" height="auto">

- Normalizing data:
<img src="https://i.ibb.co/sJLPmxc/Screenshot-2024-08-09-at-21-44-25.png" alt="image" width="600" height="auto">

- Matched rules:
<img src="https://i.ibb.co/F3jhf6F/Screenshot-2024-08-09-at-21-47-45.png" alt="image" width="600" height="auto">
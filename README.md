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
<br>
No need to pass body in order to get data. The required parameters are stores in config file.
<br>
Reasons: 
<br>

- Accessibility - this POST request won't work with a private email, because the hiring url supports the email you supplied. Private email gets status code 401 - Unauthorized.

- Security - configuration files or environment variables can be protected with access controls and encryption, ensuring that only authorized processes or personnel can access the key.
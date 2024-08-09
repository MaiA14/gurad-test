# Streamer

## Running this server 

```bash
POST https://satisfied-berty-mai2-b6a31fff.koyeb.app/stream_start

```
<br>
No need to pass body in order to get data. The required parameters are stores in config file.
<br>
Reasons:
- Accessibility - this POST request won't work with a private email, because the hiring url supports the email you supplied. Private email gets status code 401 - Unauthorized.

- Security: configuration files or environment variables can be protected with access controls and encryption, ensuring that only authorized processes or personnel can access the key.
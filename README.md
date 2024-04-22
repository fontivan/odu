# ODU - One-time Download URL

This script provides a simple way to provide a single file to web clients.

The script has some basic obfuscation security to prevent random sniffers from stealing your file:

- On startup a random port between 10000 and 65525 will be generated and used by the HTTP server. The server will only be listening to this single port.

- On startup, a random UUID will be generated and used in the URL. If the correct UUID is not provided the script will return 404.

- The user must provide a password that is also required in the URL. If the correct password is not provided the script will return 404.

- The script is configured to automatically exit after a specified period. The default is 1 hour, but it can be disabled by setting the value to 0 or any negative number.


## usage

Run the script using `make run` and providing an `ARGS` list
```bash
$> make run ARGS="--file-path /tmp/my-test-file.txt --password secretpassword"
(cd src && /home/sskeard/git/github/odu/venv/bin/python odu.py --file-path /tmp/my-test-file.txt --password secretpassword)
File '/tmp/my-test-file.txt' is now available at 'http://123.123.123.123:34245/7ca972cc-e874-47dd-af0f-b1dfe925fa26/secretpassword'
File '/tmp/my-test-file.txt' is now available at 'http://192.168.0.100:34245/7ca972cc-e874-47dd-af0f-b1dfe925fa26/secretpassword'
File '/tmp/my-test-file.txt' is now available at 'http://127.0.0.1:34245/7ca972cc-e874-47dd-af0f-b1dfe925fa26/secretpassword'
Remember to configure firewall or network router ports!
Waiting up to 1 hours before exiting automatically
127.0.0.1 - - [21/Apr/2024 23:44:39] "GET /7ca972cc-e874-47dd-af0f-b1dfe925fa26/secretpassword HTTP/1.1" 200 -
192.168.0.100 - - [21/Apr/2024 23:44:40] "GET /7ca972cc-e874-47dd-af0f-b1dfe925fa26/secretpassword HTTP/1.1" 200 -
```

## why?

I needed to send a large zip file and didn't want to upload it to a cloud provider.

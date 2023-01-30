## Requirements
System requirements:
- python3
- firefox
- geckodriver
- pip3

To install them run the following commands:
```
sudo apt install python3
sudo apt install firefox
sudo apt install pip3
wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
tar -xvzf geckodriver*
chmod +x geckodriver
sudo mv geckodriver /usr/local/bin
```

Python  requirements: 
- scapy==2.6.3
- selenium==3.141.0

To install them, run the following after running the system requirements:
```
pip3 install scapy==2.6.3 selenium==3.141.0
```
## Usage
The file named `bot.py` is the entry point to the application, it can be simply run using: `python3 bot.py` but the better approach is to create  a `cronjob` to daily run the launch command to clean up the log files preventing using all available disk space, refresh the proxies that update every 24 hours and keep the application running in background even after ending a SSH session.

## Structure
The whole code is a `scapy` project created by the `scrapy startproject hermes`, for more information about `scrapy` projects are found at: https://docs.scrapy.org/en/latest/intro/tutorial.html
The `bot.py`file contains the main code utilizing `webdriver`to navigate to the target URL.
The `proxies.json`is a file generated automatically using the following command:  `scrapy crawl arachne -O proxies.json`.
There are a few needed environment variables to run the application:
- `SMTP_SERVER`: The SMTP server used to send emails via.
- `COMPANY_EMAIL`: The email at the SMTP server that we use to send emails from.
- `APP_PASSWORD`: The password used to login to the SMTP server.
- `COMPANY_NAME`: The name to send emails as.
- `CLIENT_EMAIL`: The email to send the notifications to.

## Notes
Using the default run settings, the average time for a subsequent successful acquisition of products' data from the site is around 10-30 minutes, to reduce this time try experimenting with different `TIMEOUT`values or use paid proxy services.

Currently, the application only sends email notifications regarding new unique products, it doesn't detect new colors/variations of already existing products.

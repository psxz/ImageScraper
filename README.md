# Image URL Scraper

A simple image url scraper application built with Beautiful Soup, Selenium, Chromedriver and Flask. Can be run in Docker after building an image using the provided Dockerfile. Not built for production.

Currently the application scrapes the parent and child image urls upto level 1 (will be generalized to multiple levels). Multiple scraping jobs can be submitted which run in parallel processes within the Flask app (very bad idea). Each job can have multiple threads (default = 1) and can be given multiple parent urls.
The application is hosted on local_host and default port is 8080.

Beautiful Soup is used to collect set of all valid webpage urls from parent and child webpages.
Selenium then scrapes all valid image urls (PNG, GIF, JPEG, JPG) from the collected set.

Can be improved with message passing via RQ, Redis or Celery which will allow for safe multiprocesing for multiple jobs. A database can be attached in case of scrapig the actual images as well.

Docker run command can be used to increase the RAM available to the container via the following commands:

docker run -v /dev/shm:/dev/shm --shm-size=2gb -d -p 8080:8080 IMAGE_NAME

and commenting out the '--disable-dev-shm-usage' option in ScraperCore.py

The saved results can also be stored by adding a 'job_info' directory with Docker run command.

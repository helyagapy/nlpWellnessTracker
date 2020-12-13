# Wellness Tracker
Wellness Tracker is a Flask application that allows users to record text, exercise, and sleep logs. The application additionally incorporates natural language processing and conducts sentiment analyses on the user's journal entries.  Users will be able to see their old entries and sentiment analyses results.

The sentiment analyses is conducted with VADER (Valence Aware Dictionary and Sentiment Reasoner) tool. Documentation for the tool is available from: https://github.com/%C3%A7/vaderSentiment

## Citation
Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text. Eighth International Conference on Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.

## Required Installations

Prior to running the Wellness Tracker, please use the package manager [pip] to install the VADER sentiment tool.

```
pip install vaderSentiment
```

## Project Folder Structure
```
project
├── README.md
├── DESIGN.md
├── WALKTHROUGH.mp4
├── application.py --- contains the Flask implementation and routes
├── helpers.py --- helper functions are located here: apology, login_required, and vader
├── journal.db --- SQL database with tables: users, entries, exercise, and sleep
|
├── static
│   ├── bootstrap.min.css --- CSS stylesheet retrieved from https://bootswatch.com/
│   ├── styles.css --- stylesheet to further customize application
│   ├── notebook.ico
│   ├── relaxcat.png
│   └── sleepcat.png
|
└── templates
    ├── apology.html
    ├── exercise.html
    ├── history.html
    ├── index.html
    ├── journal.html
    ├── layout.html --- Loads Chart.js and bootstrap for html template and styles
    ├── login.html
    ├── past.html
    ├── pastentries.html
    ├── plot.html
    ├── register.html
    ├── sentiment.html
    └── sleep.html

```
## How to run
The application uses the Flask framework. In order to implement the application as designed, please retrieve the full project folder structure outlined above. Once the folder structure is in place, running the application should be as simple as going to the "project" folder location and entering "flask run" in the terminal window.

## Flask, HTML, CSS, JavaScript
All the flask routes and back-end error handling are located in the file application.py. It imports helper functions from the helper.py file. The application.py will render the HTML pages from the templates folders depending on the method they arrive at.

The templates folder also includes a layout.html file that provide the underlying theme of the app.  The layout.html file also loads Chart.js for the plot implementation.

The styling of the application draws from bootswatch and also a local css file, both of which are located in the static folder. Within the static folder are also image files. Images are used in the browser tab icon, the homepage, and also in the footer.

## SQLite Database
A SQLite database is configured to store user accounts, journal entries and sentiment analyses, exercise logs, and sleep logs. After the user registers an account, their password will be hashed and stored in the database as well.

## Walkthrough of User Experience
A new user would first need to register an account. After registration, they would remain logged into the account and can then access the different functions of the app. They can visit separate pages to log journals, log exercise minutes, and log sleep hours. After submitting a journal entry, the user would immediately receive results from sentiment analysis conducted on the entry. They can also see the results in a chart by visitng the "History" page or in a line graph by visiting the "Sentiment Plot" page. If users want to see their old entries, they can visit the "See Old Entries" page, select a timestamp from a drop down menu of their past entries and then be redirected to another page with the text. After users provide exercise and sleep data, they will also be able to see those entries on the "History" page.

## Video Walkthrough
https://youtu.be/Gx7Uag6kmAI
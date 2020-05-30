# SearchEngineCS121
Program name: Boogle
Authors: Andy Park, Kyler Frazier

Welcome to Boogle! We are definitely not a rip off of a multi-billion dollar
coorperation!

Getting started:

If you haven't already, you will need to run PREPROCESS.py to index a collection of websites. The default name of the folder with the collection is "DEV".

After which, you will be able to run queries on the collection through either QUERY.py by providing your query as a command line argument, or run it as a web app using FLASK.

# Some prerequisites and instructions
To preprocess:
    You will need to have NLTK and BS4 installed in python.
    To do this:

    $ python3 -m pip install bs4
    $ python3 -m pip install nltk
    $ python3
    >>> import nltk
    >>> nltk.download('punkt')
    >>> quit()
    $ python3 PREPROCESS.py

To run queries:
    If you only want to use the terminal version of the query, no more
    installations are needed.
    To run queries:

    $ python3 QUERY.py <your query>

    However, if you would like to run the web-app version (which is recommeneded) then a few more steps are needed.
    Installations will be as follows:

    $ python3 -m pip install python-dotenv
    $ python3 -m venv env
    $ env/Scripts/activate
    $ python3 -m pip install flask
    $ flask run
    
    Now flask is up and running, you will need some way to open it. We recommend going into your preferred web-browser, and going to
    http://localhost:5000/

    From here, you'll be able to use Boogle just like any other search engine!

# And beyond!
We have a list of queries and some explanations of how we improved them in
report.pdf
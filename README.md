# EMOTIONAL CRYSIS LOGGER
#### Video Demo: <https://www.youtube.com/watch?v=lNGc4J_O2sE>
#### Description : An emotional crysis Logger that's going to help you log your emotions and understand the the insights of how your emotions evolve.

## The In-s and Out-s of the Project:
>In modern web "Analytics" usually comes off at the cost of privacy
This project, is built especially to take into account your privacy.
The architecture of my app combines Data Science and Cryptography to achieve an intersection of features and data sovereignity.
This project was built so that the user can have a deep-insight of their moods and how they evolve without surrendering their data to a centralized "Big Tech" server.

## app.py
**This is the brain of the app**.

It starts the flask app and loads in all the necessary libraries.

It starts with setting cookies to not be stored, when the user refreshes the page or goes back and forth, so that they don't submit something they don't want to by a mistake.

The code here handles the GET and POST requests on every HTML page, including the main feature that powers this app, the logs_dict library, that is really just a weighted chain.

The `get_logs_dict()` function passes that dict into other functions, which can use it to display the necessary stat.
>The reason to choose dicts was simple, O(1) lookup.

To app uses hybrid approach between SQL and Python data-structures to optimize the lookups, and prioritize UX.

This file also handles Auth, which is a simple register, and a Log in.


## crypt.py
>The security engine.
This file initialises the Fernet library.

It initialises the SECRET_KEY and the crypter.

It has the needed functions, required to encrypt and
decrypt the user notes.

**The reason why this file is isolated is for security reasons, and for easier debugging.**

## helpers.py
>Utility functions
It has functions like @login_required that uses a wrapper function to ensure that user can access parts of my app only if they have logged in.

It also has a time conversion function for the most dominant time chart.

The time adjustment for the times page is done through JavaScript.

## constants.py
>Static data definitions
This contains the **EMOTIONS** and **TRIGGERS** dictionaries.

The reason for them to be in separate files is to avoid circuiar imports, and it's arguably better architect to keep your constants in a different file.

In order to add new emotions for e.g, it's easy to navigate to this file and do it from there.

## crysis.db
>The memory of the project
This SQL database has 2 tables; **logs** and **users**.

The database enforces a **One-to-Many** relationship between **users and logs**

Logs uses `user_id` as a foreign key to link to `users` with the `id`.

To ensure UX and scalability, I created B-Tree
Indexes on `user_id` and `emotions` which improves the speed from O(N) to O(log N).

The database makes sure that the app remains fast even when the history grows into thousands of entries!

### Visuals :
![Data View](data_view.png)
Figure 1: It illustrates the Privacy and Utility Trade off. While the notes colum remains encrypted (Purple) to protect user's diaries, `metadata` (blue/yellow) remains visible to the system to power the analytics engine!
The error messages use cute words to make the user feel at ease and and at home.

## The static.css :
I have used a glassmorphism design, with a nice black and purple design which should be soothing to the eye, give modern feeling and let the user feel at ease.

The charts use warm colors which enhance visibility.


## Future Vision:
I plan to add scalability, optimize my loops and use SQL where it's better over Python.

To add a password reset system.

## The Challenges:
**The Optimization** was the hardest part, because I had to manage a hybrid system between Python loops and data-structures and SQL lookups, eventually I ended up using SQL for finding most common emotions and chains, and python for individual data clusters.



## Installation & Usage

To run **Crysis** locally on your machine, follow these steps:

1.  **Clone the Repository:**
    Download the source code to your local machine.
2.  **Install Dependencies:**
    Navigate to the project directory and install the required Python libraries:
    `pip install -r requirements.txt`
3.  **Environment Setup:**
    Create a `.env` file in the root directory to store your `SECRET_KEY`. This ensures your encryption keys are never hardcoded.
4.  **Initialize the Database:**
    The system uses SQLite. Ensure `crysis.db` is present (or initialize it using schema.sql if applicable).
5.  **Launch:**
    Run the Flask application:
    `flask run`

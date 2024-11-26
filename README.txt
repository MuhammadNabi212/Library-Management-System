# Library-Management-System

Library Management System
Identifying Information

Name: 
P-Number:
Course Code: 

Declaration of Own Work
I confirm that this assignment is my own work.
Where I have referred to online sources, I have provided comments detailing the reference and included a link to the source.
Program Description
The Library Management System is a comprehensive Python application designed to manage a library's book collection. It provides a robust set of features for librarians and users, including:

Adding new books to the library
Searching for books by title, author, or genre
Borrowing and returning books
Rating books
Generating personalized book recommendations based on user borrowing history
Persistent data storage using JSON

The system maintains a detailed record of each book, tracking its borrowing history, ratings, and availability. Users can interact with the library through a text-based menu interface, allowing for easy book management and discovery.
Packages/Libraries Used

Python standard libraries:

os
json
datetime
typing
collections



Installation Instructions

Ensure Python 3.7+ is installed on your system
Clone the repository or download the source files
Install required dependencies:
Copypip install -r requirements.txt


Running the Program
Navigate to the directory containing the source files
Run the program using Python:
 app.py

Follow the on-screen menu to interact with the library system

Usage Notes
The system saves book data to library_data.json
Each book requires a unique book ID when added
Users can log in with any user ID
Ratings are on a scale of 1-5

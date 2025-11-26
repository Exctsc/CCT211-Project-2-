MyMediaHub - Media Library Tracker
Project Description
Course: CCT211 : Fundamentals of User Interface Programming
Institution: Institute of Communication, Culture, Information and Technology
Term: Fall 2025 Nov.25
Contributors: Ye Lian, Tony Ren, Jiachen Huang. (Each member contributed equally.)

Project: Final Project: MyMediaHub (Media Library Management Application)
MyMediaHub is a personal media library tracker that helps users organize and manage their collection of media. Such as books, films, games, audiobooks, podcasts, TV shows, and more. The application features a clean, modern interface with multi-user support, search/filter capabilities, statistics tracking, and cover image uploads.

Features:
Multi-User System: Create and manage multiple user profiles
Media Management: Add, edit, view, and delete media items
11 Media Types: Books, Films, Games, Audiobooks, Podcasts, TV Shows, Documentaries, Comics, Anime, Manga, Cartoons
Search & Filter: Find media by title, type, or completion status
Statistics Dashboard: View your library stats and reading/watching progress
Cover Images: Upload and display cover art for your media
Details View: See comprehensive information about each item
Database Persistence: All data saved using SQLite

System Requirements：
Recommended: Windows System as the buttons will have colours
Also Works On: macOS (with full Mac compatibility) 

Required Libraries:
Tkinter (usually comes with Python)
Pillow (PIL) for image handling
Sqlite3 (comes with Python)

How to Run
IMPORTANT: First-Time Setup
Before running the main application, you MUST run the setup database first!

Step 1: Initialize the Database
bashpython setup_database.py
This creates the necessary database files (media_library.db and users.db)

Step 2: Run the Application
bashpython main.py

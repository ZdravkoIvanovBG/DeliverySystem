# 📦 Delivery System
### A Python-based application that allows customers to browse and borrow books. Being able to add, remove and sort books.

# Project Setup Instructions

## Prerequisites

To run this project, you will need:

- Python 3.10+

## Setup Guide

### Step 1: Clone the Repository

First, clone the repository to your machine:

```sh
git clone <repository-url>
```

### Step 2: Navigate to the project directory 

```sh
cd <repository-directory>
```

### Step 3: Go into the main.py file

Go into the main.py file and run the program.

```sh
python main.py
```

After starting the program, you can use the commands listed. Pre-filled data is added with the library.json

---

### Main Classes
- **LibraryItem** – abstract class that represents a library resource such as Book and EBook. It consists of title, author, release_year.
- **Book** – represents a physical book, adding ISBN and page count.
- **EBook** - represents a digital book, adding file_format and file_size.
- **Reader** - represents a user who registers to the library. He can borrow books and return them.
- **Library** – manages the whole library system. You can add books, remove them, search for books or readers,
sort books by title or year and print all books or readers.

### OOP Principles

**Classes and Objects**: Books, Ebooks, Readers and Library are all classes with their own constructors and methods.

**Inheritance**: Book and EBook inherit from LibraryItem with super() adding abstraction.

**Encapsulation**: Availability is protected and only modified by the borrow and return_item methods, and if searched, 
it is done by a method in LibraryItem rather than using it directly with _availability.

**Polymorphism**: the borrow() and return_item() methods are overridden in Book and Ebook writing their own rules.
Book can be borrowed just once and EBook can be borrowed infinite times.

## Commands

- add book
- add reader
- borrow book
- return book
- remove book
- show books
- show readers
- sort books
- finish
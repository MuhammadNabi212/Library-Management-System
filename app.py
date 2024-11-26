import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict
import matplotlib.pyplot as plt

class Book:
    def __init__(self, title: str, author: str, genre: str, book_id: str):
        self.title = title
        self.author = author
        self.genre = genre
        self.book_id = book_id
        self.is_borrowed = False
        self.borrow_history: List[Dict] = []
        self.rating: float = 0.0
        self.num_ratings: int = 0

    def __str__(self) -> str:
        status = 'Borrowed' if self.is_borrowed else 'Available'
        rating_info = f", Rating: {self.rating:.1f}/5.0" if self.num_ratings > 0 else ", No ratings yet"
        return f"{self.title} by {self.author} ({status}){rating_info}"

    def add_rating(self, rating: float) -> None:
        """Add a rating (1-5) to the book and update average."""
        if 1 <= rating <= 5:
            self.rating = ((self.rating * self.num_ratings) + rating) / (self.num_ratings + 1)
            self.num_ratings += 1

    def borrow(self, user_id: str) -> bool:
        """Borrow the book and record the transaction."""
        if not self.is_borrowed:
            self.is_borrowed = True
            self.borrow_history.append({
                'user_id': user_id,
                'borrow_date': datetime.now().isoformat(),
                'return_date': None
            })
            return True
        return False

    def return_book(self) -> bool:
        """Return the book and update the transaction record."""
        if self.is_borrowed:
            self.is_borrowed = False
            if self.borrow_history:
                self.borrow_history[-1]['return_date'] = datetime.now().isoformat()
            return True
        return False

    def to_dict(self) -> Dict:
        """Convert book object to dictionary for JSON serialization."""
        return {
            'title': self.title,
            'author': self.author,
            'genre': self.genre,
            'book_id': self.book_id,
            'is_borrowed': self.is_borrowed,
            'borrow_history': self.borrow_history,
            'rating': self.rating,
            'num_ratings': self.num_ratings
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Book':
        """Create a Book object from a dictionary."""
        book = cls(data['title'], data['author'], data['genre'], data['book_id'])
        book.is_borrowed = data['is_borrowed']
        book.borrow_history = data['borrow_history']
        book.rating = data.get('rating', 0.0)
        book.num_ratings = data.get('num_ratings', 0)
        return book

class Library:
    def __init__(self):
        self.books: List[Book] = []
        self.load_books()

    def add_book(self, title: str, author: str, genre: str, book_id: str) -> None:
        """Add a new book to the library with error checking."""
        try:
            if not all([title, author, genre, book_id]):
                raise ValueError("All fields must be filled")
            if any(b.book_id == book_id for b in self.books):
                raise ValueError("Book ID already exists")
            new_book = Book(title, author, genre, book_id)
            self.books.append(new_book)
            self.save_books()
            print(f"Book '{title}' added successfully.")
        except ValueError as e:
            print(f"Error adding book: {e}")

    def search_books(self, search_term: str, search_type: str = 'all') -> List[Book]:
        """Enhanced search with multiple criteria and sorting."""
        search_term = search_term.lower()
        if search_type == 'title':
            results = [b for b in self.books if search_term in b.title.lower()]
        elif search_type == 'author':
            results = [b for b in self.books if search_term in b.author.lower()]
        elif search_type == 'genre':
            results = [b for b in self.books if search_term in b.genre.lower()]
        else:
            results = [b for b in self.books if 
                      search_term in b.title.lower() or 
                      search_term in b.author.lower() or 
                      search_term in b.genre.lower()]
        return sorted(results, key=lambda x: (-x.rating, x.title))

    def generate_recommendations(self, user_id: str) -> List[Book]:
        """Generate book recommendations based on user's borrowing history and ratings."""
        user_genres = defaultdict(int)
        user_authors = defaultdict(int)
        
        # Analyze user's borrowing history
        for book in self.books:
            for record in book.borrow_history:
                if record['user_id'] == user_id:
                    user_genres[book.genre] += 1
                    user_authors[book.author] += 1
        
        # Find books that match user's preferences
        recommendations = []
        for book in self.books:
            if not book.is_borrowed and book not in recommendations:
                score = (user_genres[book.genre] * 2 + 
                        user_authors[book.author] * 3 + 
                        book.rating)
                if score > 0:
                    recommendations.append((score, book))
        
        # Return top 5 recommendations sorted by score
        return [book for _, book in sorted(recommendations, reverse=True)[:5]]

    def generate_statistics(self) -> Dict:
        """Generate library statistics for visualization."""
        stats = {
            'genres': defaultdict(int),
            'authors': defaultdict(int),
            'ratings': defaultdict(list),
            'borrow_frequency': defaultdict(int)
        }
        
        for book in self.books:
            stats['genres'][book.genre] += 1
            stats['authors'][book.author] += 1
            if book.num_ratings > 0:
                stats['ratings'][book.genre].append(book.rating)
            stats['borrow_frequency'][book.title] = len(book.borrow_history)
        
        return stats

    def visualize_statistics(self) -> None:
        """Create visualizations of library statistics."""
        stats = self.generate_statistics()
        
        # Create a figure with subplots
        plt.figure(figsize=(15, 10))
        
        # Genre distribution
        plt.subplot(2, 2, 1)
        genres = list(stats['genres'].keys())
        counts = list(stats['genres'].values())
        plt.bar(genres, counts)
        plt.title('Books by Genre')
        plt.xticks(rotation=45)
        
        # Average ratings by genre
        plt.subplot(2, 2, 2)
        avg_ratings = {genre: sum(ratings)/len(ratings) 
                      for genre, ratings in stats['ratings'].items() 
                      if ratings}
        if avg_ratings:
            plt.bar(avg_ratings.keys(), avg_ratings.values())
            plt.title('Average Ratings by Genre')
            plt.xticks(rotation=45)
        
        # Most borrowed books
        plt.subplot(2, 2, 3)
        sorted_books = sorted(stats['borrow_frequency'].items(), 
                            key=lambda x: x[1], reverse=True)[:5]
        plt.bar([b[0] for b in sorted_books], [b[1] for b in sorted_books])
        plt.title('Most Borrowed Books')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()

    def save_books(self) -> None:
        """Save library data to JSON file with error handling."""
        try:
            with open("library_data.json", "w") as file:
                json_data = [book.to_dict() for book in self.books]
                json.dump(json_data, file, indent=4)
        except Exception as e:
            print(f"Error saving library data: {e}")

    def load_books(self) -> None:
        """Load library data from JSON file with error handling."""
        try:
            if os.path.exists("library_data.json"):
                with open("library_data.json", "r") as file:
                    data = json.load(file)
                    self.books = [Book.from_dict(book_data) for book_data in data]
        except Exception as e:
            print(f"Error loading library data: {e}")
            self.books = []

def main():
    library = Library()
    current_user = None

    def login() -> None:
        nonlocal current_user
        user_id = input("Enter your user ID: ")
        current_user = user_id
        print(f"Logged in as user: {user_id}")

    def print_menu() -> None:
        print("\n=== Library Management System ===")
        print("1. Add Book")
        print("2. Search Books")
        print("3. Borrow Book")
        print("4. Return Book")
        print("5. View All Books")
        print("6. Rate a Book")
        print("7. Get Book Recommendations")
        print("8. View Library Statistics")
        print("9. Change User")
        print("0. Exit")
        print("==============================")

    if not current_user:
        login()

    while True:
        try:
            print_menu()
            choice = input("Enter choice (0-9): ")

            if choice == '1':
                title = input("Enter book title: ")
                author = input("Enter book author: ")
                genre = input("Enter book genre: ")
                book_id = input("Enter book ID: ")
                library.add_book(title, author, genre, book_id)

            elif choice == '2':
                print("\nSearch by:")
                print("1. Title")
                print("2. Author")
                print("3. Genre")
                print("4. All fields")
                search_choice = input("Enter choice (1-4): ")
                search_term = input("Enter search term: ")
                
                search_type = {
                    '1': 'title',
                    '2': 'author',
                    '3': 'genre',
                    '4': 'all'
                }.get(search_choice, 'all')
                
                found_books = library.search_books(search_term, search_type)
                if found_books:
                    print("\nSearch results:")
                    for idx, book in enumerate(found_books, 1):
                        print(f"{idx}. {book}")
                else:
                    print("No books found.")

            elif choice == '3':
                if not current_user:
                    print("Please log in first.")
                    login()
                    continue
                    
                book_id = input("Enter book ID to borrow: ")
                book = next((b for b in library.books if b.book_id == book_id), None)
                if book:
                    if book.borrow(current_user):
                        library.save_books()
                        print("Book borrowed successfully.")
                    else:
                        print("Book is already borrowed.")
                else:
                    print("Book not found.")

            elif choice == '4':
                book_id = input("Enter book ID to return: ")
                book = next((b for b in library.books if b.book_id == book_id), None)
                if book:
                    if book.return_book():
                        library.save_books()
                        print("Book returned successfully.")
                    else:
                        print("Book is not borrowed.")
                else:
                    print("Book not found.")

            elif choice == '5':
                books = sorted(library.books, key=lambda x: x.title)
                print("\nAll Books:")
                for idx, book in enumerate(books, 1):
                    print(f"{idx}. {book}")

            elif choice == '6':
                book_id = input("Enter book ID to rate: ")
                book = next((b for b in library.books if b.book_id == book_id), None)
                if book:
                    try:
                        rating = float(input("Enter rating (1-5): "))
                        if 1 <= rating <= 5:
                            book.add_rating(rating)
                            library.save_books()
                            print("Rating added successfully.")
                        else:
                            print("Rating must be between 1 and 5.")
                    except ValueError:
                        print("Please enter a valid number.")
                else:
                    print("Book not found.")

            elif choice == '7':
                if not current_user:
                    print("Please log in first.")
                    login()
                    continue
                
                recommendations = library.generate_recommendations(current_user)
                if recommendations:
                    print("\nRecommended Books:")
                    for idx, book in enumerate(recommendations, 1):
                        print(f"{idx}. {book}")
                else:
                    print("No recommendations available yet. Try borrowing and rating some books first!")

            elif choice == '8':
                library.visualize_statistics()

            elif choice == '9':
                login()

            elif choice == '0':
                print("Thank you for using the Library Management System!")
                break

            else:
                print("Invalid choice. Please try again.")

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()

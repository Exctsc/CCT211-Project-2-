import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog, font
from database import DatabaseModel, Media, UserManager
from PIL import Image, ImageTk
import os
import calendar
from datetime import datetime

APP_NAME = "MyMediaHub"

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

MEDIA_TYPES = ["Book", "Film", "Game", "Audiobook", "Podcast", "TV Show", "Documentary", "Comic", "Anime", "Manga",
               "Cartoon"]
STATUSES = ["To Read", "In Progress", "Completed", "On Hold", "Dropped"]
GENRES = ["Action", "Comedy", "Drama", "Fantasy", "Horror", "Romance", "Sci-Fi", "Thriller", "Mystery", "Adventure",
          "Biography", "Historical"]

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
          "December"]
DAYS = list(range(1, 32))
YEARS = list(range(1900, 2026))

# Color scheme
COLORS = {
    'bg_dark': '#2c3e50',
    'bg_medium': '#34495e',
    'bg_light': '#ecf0f1',
    'accent_blue': '#3498db',
    'accent_blue_hover': '#2980b9',
    'accent_green': '#2ecc71',
    'accent_red': '#e74c3c',
    'accent_orange': '#e67e22',
    'accent_purple': '#9b59b6',
    'text_dark': '#2c3e50',
    'text_light': '#ecf0f1',
    'border': '#bdc3c7'
}

# Global image cache to prevent garbage collection
IMAGE_CACHE = {}


def load_image(filename, size=None):
    """Load an image from assets folder with caching"""
    try:
        filepath = os.path.join(ASSETS_DIR, filename)
        if not os.path.exists(filepath):
            return None

        # Check cache first
        cache_key = f"{filename}_{size}"
        if cache_key in IMAGE_CACHE:
            return IMAGE_CACHE[cache_key]

        img = Image.open(filepath)
        if size:
            img.thumbnail(size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)

        # Cache the image
        IMAGE_CACHE[cache_key] = photo
        return photo
    except Exception as e:
        print(f"Error loading image {filename}: {e}")
        return None


def get_media_icon(media_type):
    """Get the icon for a specific media type"""
    icon_map = {
        "Book": "icon_book.png",
        "Film": "icon_film.png",
        "Game": "icon_game.png",
        "Audiobook": "icon_audiobook.png",
        "Podcast": "icon_podcast.png",
        "TV Show": "icon_tv.png",
        "Documentary": "icon_documentary.png",
        "Comic": "icon_comic.png",
        "Anime": "icon_anime.png",
        "Manga": "icon_manga.png",
        "Cartoon": "icon_cartoon.png"
    }

    icon_filename = icon_map.get(media_type)
    if icon_filename:
        return load_image(icon_filename, size=(24, 24))
    return None


def get_rating_symbol(rating):
    """Convert rating to colored symbol"""
    if rating is None:
        return "-"
    if rating <= 5.0:
        return "👎"
    elif rating <= 8.0:
        return "👍"
    else:
        return "❤️"


def create_header_canvas(parent, width=800, height=100):
    """Create a decorative header with app name and logo"""
    canvas = tk.Canvas(parent, width=width, height=height, bg=COLORS['bg_dark'], highlightthickness=0)

    # Try to load and display logo 100 pixels x 100 pixels
    logo_img = load_image("logo.png", size=(100, 100))
    if logo_img:
        # Place logo on left side
        canvas.create_image(60, height // 2, image=logo_img, anchor="center")
        # Keep reference to prevent garbage collection
        canvas.logo_image = logo_img
    else:
        # Fallback: Draw a circle if logo not found
        canvas.create_oval(20, 25, 60, 65, fill=COLORS['accent_blue'], outline="")

    # app title
    canvas.create_text(width // 2, height // 2, text=APP_NAME,
                       font=("Helvetica", 32, "bold"), fill=COLORS['text_light'])

    # decorative line
    canvas.create_line(120, height - 10, width - 40, height - 10, fill=COLORS['accent_blue'], width=3)

    return canvas


def create_decorative_separator(parent, width=600):
    """Create a decorative separator line"""
    canvas = tk.Canvas(parent, width=width, height=20, bg=COLORS['bg_light'], highlightthickness=0)

    # Create gradient-like effect with multiple lines
    colors = [COLORS['accent_blue'], COLORS['accent_green'], COLORS['accent_purple']]
    for i, color in enumerate(colors):
        y = 10
        x_offset = i * 3
        canvas.create_line(x_offset, y, width // 3 + x_offset, y, fill=color, width=2)
        canvas.create_line(width // 3 + 20 + x_offset, y, 2 * width // 3 + x_offset, y, fill=color, width=2)
        canvas.create_line(2 * width // 3 + 20 + x_offset, y, width + x_offset, y, fill=color, width=2)

    return canvas


class UserSelectionScreen:
    """Start screen for user selection"""

    def __init__(self, root, callback):
        """Initialize user selection screen"""
        self.root = root
        self.callback = callback
        self.user_manager = UserManager()

        self.frame = tk.Frame(root, bg=COLORS['bg_dark'])
        self.frame.pack(fill="both", expand=True)

        self._create_widgets()

    def _create_widgets(self):
        """Create start screen widgets"""
        # Big logo at top
        logo_img = load_image("logo.png", size=(150, 150))
        if logo_img:
            logo_label = tk.Label(self.frame, image=logo_img, bg=COLORS['bg_dark'])
            logo_label.image = logo_img  # Keep reference
            logo_label.pack(pady=20)

        # App title
        tk.Label(
            self.frame,
            text=APP_NAME,
            font=("Helvetica", 36, "bold"),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_light']
        ).pack(pady=10)

        # Subtitle
        subtitle = tk.Label(
            self.frame,
            text="Select Your Profile",
            font=("Helvetica", 18),
            bg=COLORS['bg_dark'],
            fg=COLORS['accent_green']
        )
        subtitle.pack(pady=10)

        user_frame = tk.Frame(self.frame, bg=COLORS['bg_dark'])
        user_frame.pack(pady=30)

        try:
            users = self.user_manager.get_all_users()

            if not users:
                self._show_new_user_prompt()
            else:
                for user in users:
                    self._create_user_button(user_frame, user)

                # Add user button with black text (this is for Mac LOL)
                add_button = tk.Button(
                    user_frame,
                    text="+ Add User",
                    font=("Helvetica", 14, "bold"),
                    bg=COLORS['accent_green'],
                    fg="black",  # Black text for Mac
                    activebackground=COLORS['accent_blue'],
                    activeforeground="black",
                    command=self._add_new_user,
                    padx=30,
                    pady=15,
                    relief="flat",
                    cursor="hand2",
                    bd=2
                )
                add_button.pack(side="left", padx=15)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users: {e}")

    def _create_user_button(self, parent, username):
        """Create a button for a user"""
        user_btn = tk.Button(
            parent,
            text=username,
            font=("Helvetica", 16, "bold"),
            bg=COLORS['accent_blue'],
            fg="black",  # Black text for Mac
            activebackground=COLORS['accent_blue_hover'],
            activeforeground="black",
            command=lambda: self._select_user(username),
            padx=40,
            pady=20,
            relief="flat",
            cursor="hand2",
            bd=2
        )
        user_btn.pack(side="left", padx=15)

    def _select_user(self, username):
        """Handle user selection"""
        self.user_manager.close()
        self.frame.destroy()
        self.callback(username)

    def _show_new_user_prompt(self):
        """Show prompt for first-time user"""
        label = tk.Label(
            self.frame,
            text="Welcome! Create your first user profile:",
            font=("Helvetica", 16),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_light']
        )
        label.pack(pady=20)

        self._add_new_user()

    def _add_new_user(self):
        """Add a new user"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New User")
        dialog.geometry("400x200")
        dialog.configure(bg=COLORS['bg_light'])
        dialog.grab_set()

        # small header
        header_frame = tk.Frame(dialog, bg=COLORS['bg_medium'], height=50)
        header_frame.pack(fill="x")
        tk.Label(
            header_frame,
            text="Create New Profile",
            font=("Helvetica", 16, "bold"),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_light']
        ).pack(pady=12)

        tk.Label(
            dialog,
            text="Enter username:",
            font=("Helvetica", 12),
            bg=COLORS['bg_light'],
            fg=COLORS['text_dark']
        ).pack(pady=20)

        username_var = tk.StringVar()
        entry = tk.Entry(dialog, textvariable=username_var, font=("Helvetica", 12), width=25)
        entry.pack(pady=10)
        entry.focus()

        def save_user():
            username = username_var.get().strip()
            if not username:
                messagebox.showerror("Error", "Username cannot be empty!")
                return

            try:
                if self.user_manager.create_user(username):
                    messagebox.showinfo("Success", f"User '{username}' created successfully!")
                    dialog.destroy()
                    self.frame.destroy()
                    self.__init__(self.root, self.callback)
                else:
                    messagebox.showerror("Error", "Username already exists!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create user: {e}")

        tk.Button(
            dialog,
            text="Create Profile",
            command=save_user,
            bg=COLORS['accent_green'],
            fg="black",  # Black text for Mac
            font=("Helvetica", 11, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2"
        ).pack(pady=15)


class DetailsWindow:
    """Window for displaying full media details"""

    def __init__(self, parent, media):
        """Initialize details window"""
        self.window = tk.Toplevel(parent)
        self.window.title(f"Details - {media.title}")
        self.window.geometry("600x700")
        self.window.configure(bg=COLORS['bg_light'])
        self.window.grab_set()

        self._create_widgets(media)

    def _create_widgets(self, media):
        """Create detail widgets"""
        # Header
        header_frame = tk.Frame(self.window, bg=COLORS['bg_dark'], height=60)
        header_frame.pack(fill="x")
        tk.Label(
            header_frame,
            text="Media Details",
            font=("Helvetica", 18, "bold"),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_light']
        ).pack(pady=15)

        # Create scrollable frame
        canvas = tk.Canvas(self.window, bg=COLORS['bg_light'])
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        main_frame = tk.Frame(canvas, bg=COLORS['bg_light'], padx=20, pady=20)

        main_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=main_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load user-uploaded cover image or show placeholder
        if media.image_path and os.path.exists(media.image_path):
            try:
                img = Image.open(media.image_path)
                # Larger thumbnail size: 250x400 as this maintains portrait images better
                img.thumbnail((250, 400))
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(main_frame, image=photo, bg=COLORS['bg_light'])
                img_label.image = photo
                img_label.pack(pady=10)
            except:
                # Show placeholder if image fails to load
                placeholder = load_image("placeholder.png", size=(250, 400))
                if placeholder:
                    img_label = tk.Label(main_frame, image=placeholder, bg=COLORS['bg_light'])
                    img_label.image = placeholder
                    img_label.pack(pady=10)
        else:
            # Show placeholder when no image path
            placeholder = load_image("placeholder.png", size=(250, 400))
            if placeholder:
                img_label = tk.Label(main_frame, image=placeholder, bg=COLORS['bg_light'])
                img_label.image = placeholder
                img_label.pack(pady=10)

        # Title
        tk.Label(
            main_frame,
            text=media.title,
            font=("Helvetica", 20, "bold"),
            bg=COLORS['bg_light'],
            fg=COLORS['text_dark'],
            wraplength=550
        ).pack(pady=10)

        # Details frame
        details_frame = tk.Frame(main_frame, bg="white", relief="solid", bd=1)
        details_frame.pack(fill="x", expand=False, pady=10)

        details = [
            ("Type:", media.media_type),
            ("Genre:", media.genre),
            ("Release Date:", media.release_date),
            ("Director/Author:", media.director),
            ("Rating:", f"{media.rating}/10 {get_rating_symbol(media.rating)}" if media.rating else "-"),
            ("Status:", media.status),
            ("Date Added:", media.date_added.split()[0] if media.date_added else "-")
        ]

        for i, (label, value) in enumerate(details):
            row_frame = tk.Frame(details_frame, bg="white")
            row_frame.pack(fill="x", padx=15, pady=5)

            tk.Label(
                row_frame,
                text=label,
                font=("Helvetica", 11, "bold"),
                bg="white",
                fg=COLORS['text_dark'],
                anchor="w",
                width=15
            ).pack(side="left")

            # Add icon for Type field
            if i == 0 and label == "Type:":  # First item is Type
                icon_img = get_media_icon(media.media_type)
                if icon_img:
                    icon_label = tk.Label(row_frame, image=icon_img, bg="white")
                    icon_label.image = icon_img  # Keep reference
                    icon_label.pack(side="left", padx=(0, 5))

            tk.Label(
                row_frame,
                text=value,
                font=("Helvetica", 11),
                bg="white",
                fg=COLORS['text_dark'],
                anchor="w"
            ).pack(side="left", fill="x", expand=True)

        # Description section
        if media.description:
            tk.Label(
                main_frame,
                text="Description:",
                font=("Helvetica", 12, "bold"),
                bg=COLORS['bg_light'],
                fg=COLORS['text_dark'],
                anchor="w"
            ).pack(fill="x", pady=(15, 5))

            desc_frame = tk.Frame(main_frame, bg="white", relief="solid", bd=1)
            desc_frame.pack(fill="both", expand=True)

            desc_text = tk.Text(desc_frame, wrap="word", font=("Helvetica", 10),
                                height=8, bg="white", fg="black")  # Black text for Mac
            desc_text.insert("1.0", media.description)
            desc_text.config(state="disabled")
            desc_text.pack(padx=10, pady=10, fill="both", expand=True)

        # Close button
        tk.Button(
            main_frame,
            text="Close",
            command=self.window.destroy,
            bg=COLORS['accent_blue'],
            fg="black",  # Black text for Mac
            font=("Helvetica", 11, "bold"),
            padx=30,
            pady=8,
            relief="flat",
            cursor="hand2"
        ).pack(pady=15)


class AddEditWindow:
    """Window for adding or editing media items"""

    def __init__(self, parent, media, callback):
        """Initialize add/edit window"""
        self.media = media
        self.callback = callback

        self.window = tk.Toplevel(parent)
        self.window.title("Edit Media" if media else "Add New Media")
        self.window.geometry("700x750")
        self.window.configure(bg=COLORS['bg_light'])
        self.window.grab_set()

        self.image_path = media.image_path if media else ""

        self._create_widgets()

        if media:
            self._populate_fields()

    def _create_widgets(self):
        """Create form widgets"""
        # Header
        header_frame = tk.Frame(self.window, bg=COLORS['bg_dark'], height=60)
        header_frame.pack(fill="x")
        title_text = "Edit Media Item" if self.media else "Add New Media Item"
        tk.Label(
            header_frame,
            text=title_text,
            font=("Helvetica", 18, "bold"),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_light']
        ).pack(pady=15)

        # Scrollable form
        canvas = tk.Canvas(self.window, bg=COLORS['bg_light'])
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        self.form_frame = tk.Frame(canvas, bg=COLORS['bg_light'])

        self.form_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")

        # Form fields
        self.entries = {}

        # Title
        self._create_field("Title *", "title", tk.Entry)

        # Media Type
        self._create_field("Media Type *", "media_type", ttk.Combobox, values=MEDIA_TYPES)

        # Genre
        self._create_field("Genre", "genre", ttk.Combobox, values=GENRES)

        # Release Date
        date_frame = tk.Frame(self.form_frame, bg=COLORS['bg_light'])
        date_frame.pack(fill="x", pady=5)

        tk.Label(
            date_frame,
            text="Release Date:",
            font=("Helvetica", 11),
            bg=COLORS['bg_light'],
            fg=COLORS['text_dark'],
            anchor="w"
        ).pack(side="left", padx=(0, 10))

        self.month_var = tk.StringVar()
        self.day_var = tk.StringVar()
        self.year_var = tk.StringVar()

        ttk.Combobox(date_frame, textvariable=self.month_var, values=MONTHS,
                     state="readonly", width=12).pack(side="left", padx=2)
        ttk.Combobox(date_frame, textvariable=self.day_var, values=DAYS,
                     state="readonly", width=5).pack(side="left", padx=2)
        ttk.Combobox(date_frame, textvariable=self.year_var, values=YEARS,
                     state="readonly", width=8).pack(side="left", padx=2)

        # Director/Author
        self._create_field("Director/Author", "director", tk.Entry)

        # Rating
        rating_frame = tk.Frame(self.form_frame, bg=COLORS['bg_light'])
        rating_frame.pack(fill="x", pady=5)

        tk.Label(
            rating_frame,
            text="Rating (0-10):",
            font=("Helvetica", 11),
            bg=COLORS['bg_light'],
            fg=COLORS['text_dark'],
            anchor="w"
        ).pack(side="left", padx=(0, 10))

        self.rating_var = tk.StringVar()
        rating_spinbox = tk.Spinbox(
            rating_frame,
            from_=0,
            to=10,
            increment=0.5,
            textvariable=self.rating_var,
            font=("Helvetica", 10),
            width=10
        )
        rating_spinbox.pack(side="left")

        # Status
        self._create_field("Status *", "status", ttk.Combobox, values=STATUSES)

        # Description
        desc_label_frame = tk.Frame(self.form_frame, bg=COLORS['bg_light'])
        desc_label_frame.pack(fill="x", pady=(10, 5))

        tk.Label(
            desc_label_frame,
            text="Description:",
            font=("Helvetica", 11),
            bg=COLORS['bg_light'],
            fg=COLORS['text_dark'],
            anchor="w"
        ).pack(side="left")

        self.description_text = tk.Text(
            self.form_frame,
            height=5,
            font=("Helvetica", 10),
            wrap="word",
            bg="white",
            fg="black",  # Black text for Mac
            relief="solid",
            bd=1,
            insertbackground="black"
        )
        self.description_text.pack(fill="x", pady=5)

        # Image selection
        image_frame = tk.Frame(self.form_frame, bg=COLORS['bg_light'])
        image_frame.pack(fill="x", pady=10)

        tk.Button(
            image_frame,
            text="Choose Cover Image",
            command=self._choose_image,
            bg=COLORS['accent_orange'],
            fg="black",  # Black text for Mac
            font=("Helvetica", 10, "bold"),
            padx=15,
            pady=5,
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)

        self.image_label = tk.Label(
            image_frame,
            text="No image selected",
            font=("Helvetica", 9),
            bg=COLORS['bg_light'],
            fg=COLORS['text_dark']
        )
        self.image_label.pack(side="left", padx=10)

        # Buttons
        button_frame = tk.Frame(self.form_frame, bg=COLORS['bg_light'])
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="Save",
            command=self._save,
            bg=COLORS['accent_green'],
            fg="black",  # Black text for Mac
            font=("Helvetica", 12, "bold"),
            padx=40,
            pady=10,
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=10)

        tk.Button(
            button_frame,
            text="Cancel",
            command=self.window.destroy,
            bg=COLORS['accent_red'],
            fg="black",  # Black text for Mac
            font=("Helvetica", 12, "bold"),
            padx=40,
            pady=10,
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=10)

    def _create_field(self, label_text, field_name, widget_class, **kwargs):
        """Create a form field"""
        frame = tk.Frame(self.form_frame, bg=COLORS['bg_light'])
        frame.pack(fill="x", pady=5)

        tk.Label(
            frame,
            text=label_text,
            font=("Helvetica", 11),
            bg=COLORS['bg_light'],
            fg=COLORS['text_dark'],
            anchor="w",
            width=15
        ).pack(side="left", padx=(0, 10))

        if widget_class == ttk.Combobox:
            widget = ttk.Combobox(frame, state="readonly", **kwargs)
        else:
            widget = widget_class(frame, font=("Helvetica", 10), **kwargs)

        widget.pack(side="left", fill="x", expand=True)
        self.entries[field_name] = widget

    def _choose_image(self):
        """Choose cover image"""
        filename = filedialog.askopenfilename(
            title="Select Cover Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if filename:
            self.image_path = filename
            self.image_label.config(text=os.path.basename(filename))

    def _populate_fields(self):
        """Populate fields with existing media data"""
        if not self.media:
            return

        self.entries['title'].insert(0, self.media.title)
        self.entries['media_type'].set(self.media.media_type)
        self.entries['genre'].set(self.media.genre)

        if self.media.release_date:
            parts = self.media.release_date.split()
            if len(parts) >= 3:
                self.month_var.set(parts[0])
                self.day_var.set(parts[1].rstrip(','))
                self.year_var.set(parts[2])

        self.entries['director'].insert(0, self.media.director)

        if self.media.rating:
            self.rating_var.set(str(self.media.rating))

        self.entries['status'].set(self.media.status)

        if self.media.description:
            self.description_text.insert("1.0", self.media.description)

        if self.media.image_path:
            self.image_label.config(text=os.path.basename(self.media.image_path))

    def _save(self):
        """Save media item"""
        # Validate required fields
        title = self.entries['title'].get().strip()
        media_type = self.entries['media_type'].get()
        status = self.entries['status'].get()

        if not all([title, media_type, status]):
            messagebox.showerror("Error", "Please fill in all required fields (*)")
            return

        # Create release date string
        release_date = ""
        if self.month_var.get() and self.day_var.get() and self.year_var.get():
            release_date = f"{self.month_var.get()} {self.day_var.get()}, {self.year_var.get()}"

        # Get rating
        rating = None
        try:
            rating_text = self.rating_var.get()
            if rating_text:
                rating = float(rating_text)
                if not (0 <= rating <= 10):
                    messagebox.showerror("Error", "Rating must be between 0 and 10")
                    return
        except ValueError:
            messagebox.showerror("Error", "Invalid rating value")
            return

        # Create media object
        media = Media(
            id=self.media.id if self.media else None,
            title=title,
            media_type=media_type,
            genre=self.entries['genre'].get(),
            release_date=release_date,
            director=self.entries['director'].get().strip(),
            description=self.description_text.get("1.0", "end-1c").strip(),
            rating=rating,
            status=status,
            image_path=self.image_path
        )

        self.callback(media)
        self.window.destroy()


class StatisticsWindow:
    """Window for displaying library statistics"""

    def __init__(self, parent, db_model):
        """Initialize statistics window"""
        self.window = tk.Toplevel(parent)
        self.window.title(f"{APP_NAME} - Statistics")
        self.window.geometry("700x600")
        self.window.configure(bg=COLORS['bg_light'])
        self.window.grab_set()

        self.db_model = db_model
        self._create_widgets()

    def _create_widgets(self):
        """Create statistics widgets"""
        # Header
        header_frame = tk.Frame(self.window, bg=COLORS['bg_dark'], height=60)
        header_frame.pack(fill="x")
        tk.Label(
            header_frame,
            text="Library Statistics",
            font=("Helvetica", 18, "bold"),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_light']
        ).pack(pady=15)

        main_frame = tk.Frame(self.window, bg=COLORS['bg_light'], padx=30, pady=20)
        main_frame.pack(fill="both", expand=True)

        try:
            stats = self.db_model.get_statistics()

            # Total items with large display
            total_frame = tk.Frame(main_frame, bg=COLORS['accent_blue'], relief="solid", bd=2)
            total_frame.pack(fill="x", pady=15)

            tk.Label(
                total_frame,
                text=str(stats['total_items']),
                font=("Helvetica", 48, "bold"),
                bg=COLORS['accent_blue'],
                fg="black"
            ).pack(pady=10)

            tk.Label(
                total_frame,
                text="Total Items in Library",
                font=("Helvetica", 14),
                bg=COLORS['accent_blue'],
                fg="black"
            ).pack(pady=(0, 10))

            # Decorative separator
            create_decorative_separator(main_frame, width=640).pack(pady=15)

            # Type breakdown
            if stats['type_breakdown']:
                tk.Label(
                    main_frame,
                    text="📚 By Media Type",
                    font=("Helvetica", 16, "bold"),
                    bg=COLORS['bg_light'],
                    fg=COLORS['text_dark'],
                    anchor="w"
                ).pack(fill="x", pady=(10, 5))

                type_frame = tk.Frame(main_frame, bg="white", relief="solid", bd=1)
                type_frame.pack(fill="x", pady=5)

                for media_type, count in sorted(stats['type_breakdown'].items()):
                    row = tk.Frame(type_frame, bg="white")
                    row.pack(fill="x", padx=15, pady=5)

                    tk.Label(
                        row,
                        text=media_type,
                        font=("Helvetica", 11),
                        bg="white",
                        fg=COLORS['text_dark'],
                        anchor="w",
                        width=20
                    ).pack(side="left")

                    tk.Label(
                        row,
                        text=str(count),
                        font=("Helvetica", 11, "bold"),
                        bg="white",
                        fg=COLORS['accent_blue'],
                        anchor="e"
                    ).pack(side="right")

            # Status breakdown
            if stats['status_breakdown']:
                tk.Label(
                    main_frame,
                    text="📊 By Status",
                    font=("Helvetica", 16, "bold"),
                    bg=COLORS['bg_light'],
                    fg=COLORS['text_dark'],
                    anchor="w"
                ).pack(fill="x", pady=(15, 5))

                status_frame = tk.Frame(main_frame, bg="white", relief="solid", bd=1)
                status_frame.pack(fill="x", pady=5)

                for status, count in sorted(stats['status_breakdown'].items()):
                    row = tk.Frame(status_frame, bg="white")
                    row.pack(fill="x", padx=15, pady=5)

                    tk.Label(
                        row,
                        text=status,
                        font=("Helvetica", 11),
                        bg="white",
                        fg=COLORS['text_dark'],
                        anchor="w",
                        width=20
                    ).pack(side="left")

                    tk.Label(
                        row,
                        text=str(count),
                        font=("Helvetica", 11, "bold"),
                        bg="white",
                        fg=COLORS['accent_green'],
                        anchor="e"
                    ).pack(side="right")

            # Average rating
            tk.Label(
                main_frame,
                text="⭐ Average Rating",
                font=("Helvetica", 16, "bold"),
                bg=COLORS['bg_light'],
                fg=COLORS['text_dark'],
                anchor="w"
            ).pack(fill="x", pady=(15, 5))

            rating_frame = tk.Frame(main_frame, bg=COLORS['accent_purple'], relief="solid", bd=2)
            rating_frame.pack(fill="x", pady=5)

            avg_rating = stats.get('average_rating', 0)
            tk.Label(
                rating_frame,
                text=f"{avg_rating}/10",
                font=("Helvetica", 24, "bold"),
                bg=COLORS['accent_purple'],
                fg="black"
            ).pack(pady=15)

        except Exception as e:
            tk.Label(
                main_frame,
                text=f"Error loading statistics: {e}",
                font=("Helvetica", 12),
                bg=COLORS['bg_light'],
                fg=COLORS['accent_red']
            ).pack(pady=20)

        # Close button
        tk.Button(
            main_frame,
            text="Close",
            command=self.window.destroy,
            bg=COLORS['accent_blue'],
            fg="black",  # Black text for Mac
            font=("Helvetica", 11, "bold"),
            padx=30,
            pady=8,
            relief="flat",
            cursor="hand2"
        ).pack(pady=20)


class MainApplication:
    """Main application window"""

    def __init__(self, root, username):
        """Initialize main application"""
        self.root = root
        self.username = username
        self.root.title(f"{APP_NAME} - {username}")
        self.root.geometry("1000x700")
        self.root.configure(bg=COLORS['bg_light'])

        db_name = f"media_library_{username}.db"
        self.db_model = DatabaseModel(db_name)

        self.current_media_list = []
        self.sort_reverse = {}

        self._setup_styles()
        self._create_menu()
        self._create_widgets()
        self._load_media()

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_styles(self):
        """Setup ttk styles"""
        style = ttk.Style()

        # Configure Treeview style
        style.configure("Treeview",
                        background="white",
                        foreground="black",  # Black text for visibility
                        fieldbackground="white",
                        font=("Helvetica", 10))
        style.configure("Treeview.Heading",
                        font=("Helvetica", 10, "bold"),
                        foreground="black")  # Black heading text

        style.map('Treeview',
                  background=[('selected', 'focus', COLORS['accent_blue']),
                              ('selected', '!focus', '#d3d3d3')],  # Light gray when unfocused
                  foreground=[('selected', 'focus', 'white'),  # White text on blue when focused
                              ('selected', '!focus', 'black'),  # Black text on gray when unfocused
                              ('!selected', 'black')])  # Black text when not selected

    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add New Item", command=self._add_media)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Statistics", command=self._show_statistics)
        view_menu.add_command(label="Clear Filters", command=self._clear_filters)

    def _create_widgets(self):
        """Create main GUI widgets"""
        # Header with app name
        header_canvas = create_header_canvas(self.root, width=1000, height=100)
        header_canvas.pack(pady=(0, 10))

        # User welcome
        welcome_frame = tk.Frame(self.root, bg=COLORS['bg_light'])
        welcome_frame.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(
            welcome_frame,
            text=f"Welcome back, {self.username}!",
            font=("Helvetica", 14),
            bg=COLORS['bg_light'],
            fg=COLORS['text_dark']
        ).pack(side="left")

        # Control panel
        control_frame = tk.Frame(self.root, bg=COLORS['bg_light'], padx=10, pady=10)
        control_frame.pack(fill="x")

        # Search
        tk.Label(
            control_frame,
            text="🔍 Search:",
            font=("Helvetica", 10),
            bg=COLORS['bg_light'],
            fg=COLORS['text_dark']
        ).pack(side="left", padx=5)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._apply_filters())
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side="left", padx=5)

        # Filter by Type
        tk.Label(
            control_frame,
            text="📁 Type:",
            font=("Helvetica", 10),
            bg=COLORS['bg_light'],
            fg=COLORS['text_dark']
        ).pack(side="left", padx=(15, 5))

        self.filter_type_var = tk.StringVar(value="All")
        type_combo = ttk.Combobox(control_frame, textvariable=self.filter_type_var,
                                  values=["All"] + MEDIA_TYPES, state="readonly", width=15)
        type_combo.pack(side="left", padx=5)
        type_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())

        # Filter by Status
        tk.Label(
            control_frame,
            text="⏳ Status:",
            font=("Helvetica", 10),
            bg=COLORS['bg_light'],
            fg=COLORS['text_dark']
        ).pack(side="left", padx=(15, 5))

        self.filter_status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(control_frame, textvariable=self.filter_status_var,
                                    values=["All"] + STATUSES, state="readonly", width=15)
        status_combo.pack(side="left", padx=5)
        status_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())

        # Treeview
        tree_frame = tk.Frame(self.root, bg=COLORS['bg_light'])
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("ID", "Title", "Type", "Genre", "Year", "Director", "Rating", "Status")
        self.treeview = ttk.Treeview(tree_frame, columns=columns, show="tree headings", height=15)
        self.treeview.column("#0", width=0, stretch="no")

        for col in columns:
            self.treeview.heading(col, text=col, command=lambda c=col: self._sort_column(c))
            if col == "Title":
                self.treeview.column(col, anchor="w", width=200)
            elif col == "Rating":
                self.treeview.column(col, anchor="center", width=80)
            elif col == "ID":
                self.treeview.column(col, anchor="center", width=50)
            else:
                self.treeview.column(col, anchor="w", width=100)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)

        self.treeview.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.treeview.bind("<<TreeviewSelect>>", self._on_select)
        self.treeview.bind("<Double-1>", lambda e: self._show_details())

        # Button panel
        button_frame = tk.Frame(self.root, bg=COLORS['bg_light'], pady=10)
        button_frame.pack(fill="x", padx=10)

        tk.Button(
            button_frame,
            text="➕ Add New",
            command=self._add_media,
            bg=COLORS['accent_green'],
            fg="black",  # Black text for Mac
            font=("Helvetica", 11, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="✏️ Edit",
            command=self._edit_media,
            bg=COLORS['accent_blue'],
            fg="black",  # Black text for Mac
            font=("Helvetica", 11, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="🗑️ Delete",
            command=self._delete_media,
            bg=COLORS['accent_red'],
            fg="black",  # Black text for Mac
            font=("Helvetica", 11, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="📊 Statistics",
            command=self._show_statistics,
            bg=COLORS['accent_purple'],
            fg="black",  # Black text for Mac
            font=("Helvetica", 11, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="👁️ View Details",
            command=self._show_details,
            bg=COLORS['accent_orange'],
            fg="black",  # Black text for Mac
            font=("Helvetica", 11, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief="sunken",
            bg=COLORS['bg_medium'],
            fg=COLORS['text_light'],
            font=("Helvetica", 9),
            anchor="w"
        )
        status_bar.pack(fill="x")

    def _load_media(self):
        """Load all media items from database"""
        try:
            self.current_media_list = self.db_model.get_all_records()
            self._refresh_treeview(self.current_media_list)
            self.status_var.set(f"Loaded {len(self.current_media_list)} items")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load media: {e}")

    def _refresh_treeview(self, media_list):
        """Refresh treeview with media items"""
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        for media in media_list:
            # Parse year from release_date
            year = "-"
            if media.release_date:
                parts = media.release_date.split()
                if parts and len(parts) >= 3:
                    year = parts[-1]

            values = (
                media.id,
                media.title,
                media.media_type,
                media.genre,
                year,
                media.director,
                f"{media.rating}/10 {get_rating_symbol(media.rating)}" if media.rating else "-",
                media.status
            )
            self.treeview.insert("", "end", values=values)

    def _on_select(self, event):
        """Handle treeview selection"""
        selection = self.treeview.selection()
        if selection:
            item = self.treeview.item(selection[0])
            values = item['values']
            self.status_var.set(f"Selected: {values[1]}")

    def _show_details(self):
        """Show detailed view of selected item"""
        selection = self.treeview.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a media item to view!")
            return

        item = self.treeview.item(selection[0])
        media_id = item['values'][0]
        media = self.db_model.get_record(media_id)

        if media:
            DetailsWindow(self.root, media)

    def _add_media(self):
        """Open add media window"""

        def on_save(media):
            try:
                self.db_model.create_record(media)
                self._load_media()
                messagebox.showinfo("Success", "Media item added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add media: {e}")

        AddEditWindow(self.root, media=None, callback=on_save)

    def _edit_media(self):
        """Open edit media window"""
        selection = self.treeview.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a media item to edit!")
            return

        item = self.treeview.item(selection[0])
        media_id = item['values'][0]
        media = self.db_model.get_record(media_id)

        def on_save(updated_media):
            try:
                self.db_model.update_record(updated_media)
                self._load_media()
                messagebox.showinfo("Success", "Media item updated successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update media: {e}")

        AddEditWindow(self.root, media=media, callback=on_save)

    def _delete_media(self):
        """Delete selected media item"""
        selection = self.treeview.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a media item to delete!")
            return

        item = self.treeview.item(selection[0])
        title = item['values'][1]
        media_id = item['values'][0]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{title}'?"):
            try:
                self.db_model.delete_record(media_id)
                self._load_media()
                messagebox.showinfo("Success", "Media item deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete media: {e}")

    def _apply_filters(self):
        """Apply search and filter criteria"""
        search_term = self.search_var.get().strip().lower()
        filter_type = self.filter_type_var.get()
        filter_status = self.filter_status_var.get()

        filtered_list = self.current_media_list

        if search_term:
            filtered_list = [m for m in filtered_list if search_term in m.title.lower()]

        if filter_type != "All":
            filtered_list = [m for m in filtered_list if m.media_type == filter_type]

        if filter_status != "All":
            filtered_list = [m for m in filtered_list if m.status == filter_status]

        self._refresh_treeview(filtered_list)
        self.status_var.set(f"Showing {len(filtered_list)} of {len(self.current_media_list)} items")

    def _clear_filters(self):
        """Clear all filters"""
        self.search_var.set("")
        self.filter_type_var.set("All")
        self.filter_status_var.set("All")
        self._load_media()

    def _sort_column(self, col):
        """Sort treeview by column"""
        pass

    def _show_statistics(self):
        """Show statistics window"""
        StatisticsWindow(self.root, self.db_model)

    def _on_closing(self):
        """Handle window closing"""
        self.db_model.close()
        self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    root.title(APP_NAME)

    def start_app(username):
        """Start main application with selected user"""
        MainApplication(root, username)

    UserSelectionScreen(root, start_app)
    root.mainloop()


if __name__ == "__main__":
    main()
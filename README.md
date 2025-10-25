# Movie Project 3 aka _My Movies Database_

![Python](https://img.shields.io/badge/-Python-blue?logo=python&logoColor=white)

## 📝 Description

A Python CLI app to track and analyze your movie ratings. Add, edit, and delete reviews with notes, fetch movie details via OMDB API, and generate a shareable HTML page with posters and country flags—all with secure multi-user login.

## ✨ Features
- Add, update, and delete movie ratings with personal notes
- Automatically fetch movie details (title, year, country, etc.) from the OMDB API
- Multi-user support with secure login via bcrypt-hashed passwords
- Filter, sort, and view stats (best/worst ratings, random pick)
- Export ratings to a static HTML page with movie posters and country flags
- Navigate via an intuitive CLI menu

## 🛠️ Tech Stack
- 🐍 **Language**: Python 3
- 💾 **Database**: SQLite for persistent data storage
- 🖥️ **Frontend**: CLI with colored output powered by a custom Python module
- 🌐 **Web Export**: Static HTML generation with custom templates and CSS
- 🔌 **API**: OMDB API for movie metadata
- 🔒 **Security**: bcrypt for password hashing, `.env` for API key isolation

## 📦 Key Dependencies

- `bcrypt==5.0.0` – Secure password hashing
- `emoji==2.15.0` – Display emojis in CLI
- `maskpass==0.3.7` – Hidden password input
- `pycountry==24.6.1` – Country flag lookup
- `python-dotenv==1.1.1` – Environment variable management
- `requests==2.32.5` – HTTP calls to OMDB API
- `SQLAlchemy==2.0.43` – Database ORM
- `setuptools==80.9.0` – Package management

## 📁 Project Structure

```
.
├── data/               # SQLite database file
├── docs/               # ERD diagram and documentation
│   └── erd.png
├── src/                # Main application code
│   └── myapp/
├── templates/          # HTML template for website export
├── static/             # Generated CSS and HTML files
├── .env                # Environment file (not versioned)
├── .gitignore          # Ignore sensitive and generated files
├── requirements.txt    # Python dependencies
├── setup.py            # Package setup
└── start.sh            # Launch script
```

## 🛠️ Development Setup

1. **Clone the repository**:
	```bash
	git clone https://github.com/paul-wosch/Movie-Project-3.git
	cd Movie-Project-3
	```

2. **Get an OMDB API key** from [OMDB API](https://www.omdbapi.com/apikey.aspx) and add it to a `.env` file:
	```env
	OMDB_API_KEY=your_api_key_here
	```

3. **Create virtual environment** (optional):
    ```bash
    python -m venv .venv
    ```

4. **Activate virtual environment** (optional):
    ```bash
    source .venv/bin/activate  # Mac/Linux
    # .venv\Scripts\activate   # Windows
    ```

5. **Install external packages**:
    ```bash
    pip install -r requirements.txt
    ```

6. **Install local package in editable mode**:
    ```bash
    pip install -e .
    ```
   
    This makes the `myapp` module importable, ensuring correct imports in `main.py`.

7. **Run the application**:
    ```bash
    python src/myapp/main.py
    ```

8. **Deactivate virtual environment** (optional):
    ```bash
    deactivate
    ```

> 💡 **Make `start.sh` executable**  
> On macOS or Linux, run:  
> ```bash
> chmod 755 start.sh
> ```  
> Afterward, you can launch the app with:  
> ```bash
> ./start.sh
> ```

## 👥 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/paul-wosch/Movie-Project-3.git`
3. **Create** a new branch: `git switch -c feature/your-feature`
4. **Commit** your changes: `git commit -am 'Add some feature'`
5. **Push** to your branch: `git push origin feature/your-feature`
6. **Open** a pull request

Ensure your code follows PEP 8 and includes appropriate docstrings.

## 🚧 Known Issues and Planned Improvements

- **OMDB API data validation**: Movie data retrieved from the OMDB API should be validated before being stored in the database to ensure consistency and prevent malformed entries.
- **Country flag display**: Flag emojis may not render correctly in all terminals. As an alternative, display ISO alpha-2 country codes (e.g., US, DE) when emoji support is unreliable.
- **Architecture**: Currently procedural; future versions will migrate to OOP for better structure and maintainability, leveraging SQLAlchemy ORM fully.
- **Global state**: The logged-in user ID is currently tracked via a global variable. Refactor to use dependency injection or a session context class to avoid global state.
- **Code complexity**: The `cli.py` module contains too many lines and local variables. Consider refactoring into smaller functions or splitting into submodules.
- **Package naming**: The main package `myapp` is generic. Rename to a more descriptive name (e.g., `movierater`) to better reflect the project’s purpose.
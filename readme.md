Here's a `README.md` file for your repository, formatted for clarity and ease of use:

---

# Python Code Executor

A comprehensive Python code execution environment with a PySide2 GUI that enables real-time code editing, syntax highlighting, script management, and output display. This project is designed to execute code directly from an interactive editor, with support for syntax highlighting, autocomplete, and tabbed document management.

## Project Structure

```
code_executer/
├── bbrun.sh                  # Script to start the application in either detached or foreground mode
├── temp_script.py            # Utility to generate project folder and file structure
└── src/
    ├── main.py               # Application entry point
    ├── views/                # GUI components
    │   ├── dialogs.py
    │   ├── editor/           # Code editor and auxiliary widgets
    │   ├── main_window/      # Main application window components
    ├── services/             # Service layer for script management, session handling, and script execution
    └── __init__.py
```

## File Descriptions

### `bbrun.sh`
Shell script to start the Python application. The script includes options to run the app in the background (`-d` flag) or foreground, with virtual environment activation.

### `temp_script.py`
Generates a hierarchical project structure with file contents copied to the clipboard for easy sharing.

### `src/main.py`
Application entry point for initializing and displaying the main window interface.

## Key Modules and Features

### Views
- **dialogs.py**: Dialogs for user interactions, such as saving and loading scripts.
- **editor/**:
  - `code_editor.py`: Main code editor widget with line numbering and syntax highlighting.
  - `output_window.py`: Displays execution results.
  - `custom_tabbar.py`: Tab bar for renaming and managing editor tabs.
- **main_window/**:
  - `window.py`: Sets up the main application window.
  - `menu.py`: Manages menu actions, including opening and saving scripts.
  - `session.py`: Session management for saving and restoring open files.
  
### Services
- **script_manager.py**: Manages scripts, including saving, loading, and version control.
- **session_manager.py**: Handles saving the application state across sessions.
- **executor.py**: Executes the code in the current editor tab, with optional sudo support.

## How to Use

1. Clone the repository and navigate to the `code_executer` directory.
2. Ensure that the required Python dependencies (such as `PySide2`) are installed in a virtual environment.
3. Start the application:
   ```bash
   ./bbrun.sh      # For foreground mode
   ./bbrun.sh -d   # For detached mode
   ```

## Features

- **Tabbed Editor**: Manage multiple files with tabs, save unsaved changes, and handle multiple code execution contexts.
- **Syntax Highlighting and Autocomplete**: Enhanced code editor with real-time syntax highlighting and text auto-completion.
- **Script Versioning**: Save versions of scripts, load previous versions, and manage metadata.
- **Session Persistence**: Automatically saves the state, restoring open files and session settings on startup.

## Contributing

Feel free to submit issues, pull requests, or suggestions. Please make sure to adhere to the existing code style and test changes thoroughly before submitting.

## License

MIT License. See `LICENSE` file for more details.

---

This `README.md` provides an overview of your code structure, key components, and usage instructions, making it easier for others (and yourself!) to understand and work with the project.

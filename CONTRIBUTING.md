# Contributing Guide

Thank you for your interest in contributing to **InfoOverlay**! This repository hosts a lightweight, low-overhead system information display tailored for production nodes and low-spec infrastructure. 

Follow the steps below to contribute efficiently, preserving our strict performance standards and architectural integrity.

## Core Architectural Pillars

When writing code for InfoOverlay, keep these design rules in mind:
1. **Low Overhead & Memory Safety:** Avoid massive object allocations or intense loops in the main execution paths. The application must run smoothly on low-spec hardware.
2. **Strict UI Separation:** The UI layer (`PySide6`) must remain clean. Heavy tasks, system parsing, or file I/O must run asynchronously to prevent freezing the graphical interface.
3. **No Garbage Collection Bloat:** Clean up your objects, disconnect signals when components are destroyed, and prevent memory leaks.

## Requirements

Before working on a contribution, ensure your development environment is ready:

* **Python:** Version 3.11
* **Core Libraries:** PySide6, shiboken6, pyinstaller, xhtml2pdf, markdown
* **Build System:** Git, PowerShell (for deployment scripts), and Doxygen (for documentation references)

## How to Contribute

### 1. Set Up Your Workspace
1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/Math77077/InfoOverlay.git
   cd InfoOverlay


### 2. Create a Feature Branch

Always use standard branch prefixes to keep our repository history clean and predictable:

```bash
git checkout -b feature/your-awesome-feature
# or
git checkout -b bugfix/resolve-memory-leak
# or
git checkout -b docs/add-developer-notes
# or
git checkout -b chore/update-dependencies

```

### 3. Implement Changes & Test

* Ensure code adheres to Python PEP 8 style standards.
* Document all complex backend services or UI abstractions using **Doxygen-style docstrings**, so they render correctly in the automated pipeline.
* Test that your code doesn't crash the asset rendering mechanism if custom resources (images/videos) are missing from the `resources/` dropzones.

### 4. Commit and Push

Write descriptive, clear commit messages that describe the *what* and the *why*:

```bash
git add .
git commit -m "Optimize system metric polling interval to reduce background CPU cycles"
git push origin feature/your-awesome-feature

```

### 5. Open a Pull Request

* Use our PR Template to fill in details about what you modified.
* Clearly explain how you tested your changes (e.g., resource usage metrics, stability on long idle states).
* If your contribution changes UI layout, colors, or overlay visuals, **you must include a screenshot** in your PR description.

## Repository Hygiene

To keep the release builds light, do not track or commit temporary workspace files. Ensure your local `.gitignore` prevents pushing:

* PyInstaller output directories (`build/`, generated `.spec` files).
* Local virtual environments (`.venv/`, `env/`).
* Python cache files (`__pycache__/`, `.pyc`).
* Generated local release bundles (`InfoOverlay.zip`, `dist/`).

## Project Support & Questions

If you encounter bugs, have questions about the backend layout, or want to discuss a major architectural shift, please open a GitHub Issue directly:
https://github.com/Math77077/InfoOverlay/issues

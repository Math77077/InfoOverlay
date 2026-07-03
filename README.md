# InfoOverlay

[![Build Portable Windows App](https://github.com/Math77077/InfoOverlay/actions/workflows/build.yml/badge.svg)](https://github.com/Math77077/InfoOverlay/actions)
[![Documentation](https://img.shields.io/badge/docs-doxygen-blue.svg)](https://Math77077.github.io/InfoOverlay/)

> A lightweight, frameless, and transparent multi-window overlay system for digital signage, supporting scrolling text, images, and video with smart orientation detection. Specifically engineered to run seamlessly within the administrative constraints of Brazilian Public Health Clinics (**Unidades Básicas de Saúde - UBS**).

---

## Project Architecture & Design Philosophy

This software suite is engineered to solve a distinct public infrastructure challenge: delivering a reliable, dynamic, hardware-accelerated digital signage platform to low-spec machines where local users **possess zero administrative privileges**. 

### Production & Deployment Constraints
* **Zero-Installer Portability:** Clinic staff cannot run standard `.msi` or `.exe` installation packages due to strict network registry restrictions. The application compiles into a zero-installation, user-space portable bundle.
* **No-Code Content Management (Data Decoupling):** Core system vectors and UI styles are embedded securely into the application container. Operational media campaigns (`images` and `videos`), however, are completely decoupled—allowing administrative staff to update live playlists by dragging and dropping local files without code manipulation or compilation.

---

## 📂 Repository Structure

```text
├── .github/workflows/
│   └── build.yml             # Automated CI/CD (Windows Bundle + PDF + Doxygen Compiler)
├── app_assets/               # Embedded UI vector graphical assets (frozen into binary)
├── overlays/                 # Polymorphic Presentation Media Subsystem
│   ├── __init__.py
│   ├── image_overlay.py      # Anti-aliased image aspect rendering
│   ├── preview_overlay.py    # Default administrative setup guide overlay
│   ├── text_overlay.py       # High-frequency ticker text engine with custom HUD editor
│   └── video_overlay.py      # Hardware-accelerated QGraphicsView video pipeline
├── resources/                # External User-Facing Media Management Path
│   ├── images/               # [User Dropzone] Landscape (_h) and Portrait (_v) images
│   └── videos/               # [User Dropzone] Landscape (_h) and Portrait (_v) videos
├── .gitignore                # Restricts build artifacts and docs from polluting git tree
├── asset_service.py          # Unified filesystem tracking layer and RAM caching service
├── base_window.py            # Frameless, clamped multi-monitor OS window controller
├── Doxyfile                  # Structural parsing configuration for Doxygen pipelines
├── main.py                   # System entry point and controller orchestrator
├── requirements.txt          # Explicitly pinned build-time package manifests
└── USER_MANUAL.md            # Raw markdown user documentation source

```

---

## Clean Code & SOLID Engineering Breakdown

### 1. Single Responsibility Principle (SRP) & Dependency Injection

Instead of forcing presentation layers (`QWidgets`) to interact directly with disk I/O, file systems, and environment variable sniffing, directory tracking is entirely delegated to a standalone utility layer:

* **`AssetService`:** Acts as the single source of truth for file topology tracking. It auto-detects execution environments (sniffing `sys._MEIPASS` vs `sys.executable`), loads target directories, tracks lists, and produces randomized playlist vectors.
* **Constructor Injection:** Presentation views depend abstractly on data streams. The `AssetService` instance is injected directly into components (`__init__(self, asset_service)`), keeping layers loosely coupled and structurally testable.

### 2. High-Frequency Thread Performance & Memory Safety

To ensure smooth performance during layout transformation transitions on low-spec hardware:

* **Disk I/O Isolation:** Media scanning happens exclusively at startup or upon requested reloads. Playlists are processed using shallow copies directly out of structured RAM cache arrays (`_cached_images_h`, etc.), protecting the main GUI display thread from heavy disk bottlenecks.
* **Polymorphic Layout Swapping:** The controller uses a Strategy pattern via `switch_mode()`. When changing displays, existing widgets undergo explicit reference clearing, thread decoding pauses, and deferred heap deletion (`deleteLater()`), ensuring **zero memory allocation leaks** over prolonged operational shifts.

### 3. Advanced Window Clamping & Environment Defenses

* **Algebraic Movement Clamping:** Because `FramelessWindowHint` bypasses native OS display borders, a custom boundary evaluation algorithm intercepts mouse moves. It dynamically locks coordinates to the active monitor geometry, rendering it mathematically impossible for a user to drag a window to an unreachable screen location.
* **Graphics Backend Shielding:** Under Linux testing platforms, the engine forces the `xcb` X11 backend interface initialization explicitly (`os.environ["QT_QPA_PLATFORM"] = "xcb"`), while dropping back gracefully to native Direct X/Windows display management drivers in production environments.

---

## CI/CD Pipeline Infrastructure

The included GitHub Actions pipeline (`.github/workflows/build.yml`) automates your entire production deployment ecosystem across two concurrent jobs:

```text
⚙️ GitHub Actions Workflow Pipeline
 ├── 🪟 Job 1: Windows Compilation Pipeline
 │    ├── Environment Cache Handshake (requirements.txt hashing)
 │    ├── PyInstaller Module Engine Compilation (Onedir Configuration)
 │    ├── Inline Python Markdown-to-PDF User Guide Generation
 │    └── SmartScreen Workaround (Root Launcher 'Iniciar.bat' Structuring)
 └── 🐧 Job 2: Documentation Deployment Pipeline
      └── Compiles Doxygen Python Docstrings ──> Deploys to Live GitHub Pages Site

```

### Windows SmartScreen Blocker

Uncertified binaries often trigger aggressive Windows SmartScreen security alerts in public institutions. To prevent this, our pipeline automatically nests the compiled folder structure and structures a root-level script **`Iniciar.bat`**:

```batch
@echo off
start "" "%~dp0UBS_Signage\UBS_Signage.exe"

```

Instructing users to run this local bat launcher safely bypasses direct binary checks, resulting in a smooth user experience.

---

## 🛠️ Local Development & Manual Compilation

### 1. Requirements Setup

Ensure you are running Python 3.11+. Install all core components and pipeline utilities locally:

```bash
pip install -r requirements.txt

```

### 2. Run the Application

```bash
python main.py

```

### 3. Generate Local Documentation Pages

To audit the Doxygen documentation map locally before pushing upstream, execute:

```bash
doxygen Doxyfile

```

Open `docs/html/index.html` in any browser to review structural interaction diagrams and class definitions.

---

## 📄 Documentation Links

* **User Manual:** For complete details on file naming guidelines (`_h` vs `_v`), hotkey bindings, multi-monitor dragging, and the interactive scrolling text edit HUD, refer to the included [USER_MANUAL.md](USER_MANUAL.md) (or open the compiled `Manual_do_Usuario.pdf` included inside your production ZIP file).

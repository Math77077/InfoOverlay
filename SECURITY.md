# Security Policy

Security is a core design principle for **InfoOverlay**, especially considering its deployment environment on shared, low-spec infrastructure in public clinics. Please report any suspected vulnerabilities responsibly using the secure channels outlined below.

## Supported Versions

Security fixes and dependency patches are actively provided only for the latest stable releases tracking our default production branch.

| Version/Branch | Supported |
| --- | --- |
| `main` | Yes |
| Legacy / Archive Tags | No |

## Reporting a Vulnerability

If you discover a security vulnerability, **please do not open a public issue.** Public disclosure allows exploits to be tracked and weaponized before a patch can be deployed.

Instead, please use **GitHub Private Vulnerability Reporting**:
1. Navigate to the main page of the repository on GitHub.
2. Click on the **Security** tab under the repository name.
3. On the left sidebar, click **Advisories**.
4. Click **Report a vulnerability** to open a private advisory form directly with the maintainers.

### What to Include
To speed up the patching process, please include:
* Clear, step-by-step reproduction instructions.
* The operating system environment where the issue was validated (e.g., Windows 10/11 vs Linux X11).
* A brief assessment of the impact (e.g., unauthorized window generation, execution blocking, or local configuration tampering).

You can expect an initial acknowledgment and validation response from the maintainers within **48–72 hours**.

## Scope of Evaluation

### In-Scope (Examples)
* **Local Memory Exhaustion:** Bugs within the polymorphic layout swapper (`switch_mode()`) or deferred heap deletion (`deleteLater()`) that can intentionally trigger host crashes or memory overflows.
* **Input Injection Vulnerabilities:** Unsanitized string injection vectors inside the interactive Ticker Text HUD editor that could exploit backend string parsing or rendering components.
* **Algebraic Clamping Escapes:** Flaws in the coordinate constraint algorithm that allow unexpected system overlays to completely block administrative access to core OS elements.

### Out-of-Scope (Examples)
* **Local Media Directory Manipulation:** Malicious actors manually deleting files inside the local `resources/` dropzones. This is a local administrative infrastructure failure, not an application security exploit.
* **Lack of Code Signing Alerts:** Operating system warnings triggered by running uncertified binaries directly. This is a standard operating system defense mechanism mitigated explicitly by our documented `Iniciar.bat` deployment architecture.
* **Physical Device Compromise:** Any exploit requiring root/administrator access to the host machine's hardware layer.

## Secure Development Guidelines
* Never hardcode environment paths or local credentials within repository modules.
* Always isolate GUI application loops from unpredictable file system changes using thread-safe caching layers (`AssetService`).
## Description
Summarize the changes introduced by this Pull Request. Explain the purpose of this modification and how it enhances the system.

## Related Issue
If this PR addresses or fixes an open issue, link it here. 
Example: Closes #12

## Type of Change
Check the options that are relevant:

- [ ] Bug fix (non-breaking change which fixes an incorrect behavior)
- [ ] New feature (non-breaking change which adds functional capabilities)
- [ ] UI Refinement / Overlay Customization (changes to layouts, text tickers, or HUD elements)
- [ ] Refactoring / Performance Optimization (reducing memory footprints, stabilizing thread pools)
- [ ] Documentation update (manuals, README, Doxygen comments)

---

## Validation & Testing Done
Describe how you verified these modifications. For desktop signage platforms running on low-spec infrastructure, runtime stability is highly critical.

- [ ] Memory Leak Review: Checked that the controller pauses threads and executes proper object cleanup via deleteLater() when switching modes.
- [ ] Fallback Safety: Verified that asset indexing service handles missing resource directories gracefully without causing execution crashes.
- [ ] Boundary Clamping: Tested that window dragging handles coordinate lock restrictions across single or extended monitor configurations.
- [ ] Package Verification: Verified that the standalone execution structures (such as paths processed within Iniciar.bat) remain uncompromised.

**Testing Details:**
Provide a brief note on your validation context (e.g., "Tested on Windows 11 under a dual-monitor extended desktop configuration; window limits clamped correctly, and resource RAM caching dropped CPU spikes by 5%").

---

## Visual Impact (Mandatory for UI Changes)
If your modifications change how text tickers scroll, how aspect ratios render images, or affect the interactive HUD layout, please paste screenshot captures or links to demo recordings here.

---

## Final Checklist
- [ ] The execution pipeline compiles without syntax blocks or package manifest discrepancies.
- [ ] Local build structures, local virtual environments, and PyInstaller transient artifacts are excluded from the staging area.
- [ ] Complex backend modules or UI event layers are documented using Doxygen-compliant docstrings.
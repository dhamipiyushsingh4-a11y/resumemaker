# AI ATS Resume Builder Pro

A private Windows desktop resume builder with:
- 100 selectable layout presets (the current export uses a clean, single-column ATS-safe layout)
- Job description keyword extraction and profile keyword comparison
- Heuristic ATS-readiness checklist (not a guarantee of ATS ranking or hiring)
- Editable resume content
- PDF and DOCX export
- Hindi + English text entry support (resume content is user-provided; UI is currently English)

## Free / no paid API
The current version uses a local, rule-based keyword analyzer. It does not call a paid AI API and works offline. It is not a generative LLM. It will not invent qualifications or experience. Review all generated content and add only truthful information.

## Build Windows EXE on GitHub (no local Python or Node.js needed)
1. Create a new **private** repository on GitHub.
2. Upload all files and folders from this project ZIP. Keep `.github/workflows/build-windows.yml` in the repository.
3. Open the repository's **Actions** tab.
4. Select **Build Windows EXE** and click **Run workflow** (or push files to `main` to trigger it).
5. Wait for the green successful run.
6. Open the completed workflow run, scroll to **Artifacts**, and download `AI-ATS-Resume-Builder-Pro-Windows`.
7. Extract the ZIP and double-click `AI_ATS_Resume_Builder_Pro.exe`.

Windows may show SmartScreen because this is a personally built unsigned app. Only run the EXE built from your own repository.

## Run from source (optional)
Python 3.11+, then:
```bash
pip install -r requirements.txt
python main.py
```

## Important ATS notes
- Prefer the included single-column export layout for ATS compatibility.
- A numerical score is a heuristic checklist, not a real score from Workday, Greenhouse, Taleo, or another ATS.
- Keyword suggestions are prompts for review, not instructions to claim skills you do not have.
- Always check spelling, dates, contact details, and the final PDF/DOCX before applying.

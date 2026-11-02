import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re, os, sys, html
from datetime import date

APP_NAME = "AI ATS Resume Builder Pro"
TEMPLATES = [
    f"{i:03d} - {name}"
    for i, name in enumerate([
        "Classic ATS", "Modern Minimal", "Professional Black", "Corporate Blue",
        "Clean Graduate", "Executive Simple", "Compact One Column", "Elegant Serif",
        "Modern Gray", "Academic", "Technical", "Finance Professional",
        "Marketing Professional", "Healthcare Professional", "Operations",
        "Customer Support", "Sales Professional", "Project Manager", "Data Analyst",
        "Software Developer"
    ] + [f"Professional Layout {i:02d}" for i in range(21, 101)], start=1)
]

STOPWORDS = set("""
the and for with from that this your you are our will have has was were job role
about into their they them then than all any can may should must not but who what
when where why how an a to of in on at by as is be or we it its if across using
""".split())

def clean(s):
    return re.sub(r"\s+", " ", (s or "").strip())

def extract_keywords(jd):
    words = re.findall(r"[A-Za-z][A-Za-z+#.-]{1,}", (jd or "").lower())
    freq = {}
    for w in words:
        w = w.strip(".-")
        if len(w) > 2 and w not in STOPWORDS and not w.isdigit():
            freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda x: (-x[1], x[0]))[:35]]

def make_resume(data):
    jd = data.get("jd", "")
    keywords = extract_keywords(jd)
    skills = [x.strip() for x in re.split(r"[,;\n]", data.get("skills", "")) if x.strip()]
    matched = [k for k in keywords if any(k in s.lower() or s.lower() in k for s in skills)]
    missing = [k for k in keywords if k not in matched]
    summary = clean(data.get("summary", ""))
    if not summary:
        summary = "Motivated candidate with a strong interest in the target role and a commitment to continuous learning."
    if keywords:
        summary += " Relevant job keywords: " + ", ".join(keywords[:8]) + "."
    sections = [
        ("PROFESSIONAL SUMMARY", summary),
        ("KEY SKILLS", ", ".join(skills) if skills else "Add your verified skills here."),
        ("WORK EXPERIENCE", clean(data.get("experience", "")) or "Add your work experience, internships, or practical training here."),
        ("EDUCATION", clean(data.get("education", "")) or "Add your education details here."),
        ("PROJECTS", clean(data.get("projects", "")) or "Add relevant projects and measurable outcomes here.")
    ]
    return {
        "name": clean(data.get("name", "")) or "Your Name",
        "contact": " | ".join(x for x in [clean(data.get("email","")), clean(data.get("phone","")), clean(data.get("location",""))] if x),
        "sections": sections,
        "keywords": keywords,
        "matched": matched,
        "missing": missing
    }

def calculate_score(resume, data):
    checks = []
    checks.append((15, bool(clean(data.get("name",""))), "Name added"))
    checks.append((10, bool(clean(data.get("email",""))), "Email added"))
    checks.append((10, bool(clean(data.get("phone",""))), "Phone added"))
    checks.append((15, bool(clean(data.get("education",""))), "Education added"))
    checks.append((15, bool(clean(data.get("skills",""))), "Skills added"))
    checks.append((10, bool(clean(data.get("experience","")) or clean(data.get("projects",""))), "Experience or projects added"))
    checks.append((10, len(resume["keywords"]) > 0, "Job description analyzed"))
    match_ratio = len(resume["matched"]) / max(1, len(resume["keywords"]))
    checks.append((15, match_ratio >= 0.35, "Relevant keyword coverage"))
    score = sum(points for points, ok, _ in checks if ok)
    return score, checks, match_ratio

class ResumeApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1250x850")
        self.root.minsize(1000, 700)
        self.root.configure(bg="#f3f5f9")
        self.last_resume = None
        self.last_data = {}
        self._style()
        self._build()

    def _style(self):
        style = ttk.Style()
        try: style.theme_use("clam")
        except Exception: pass
        style.configure("TFrame", background="#f3f5f9")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("TLabel", background="#f3f5f9", foreground="#182230", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground="#14213d")
        style.configure("Sub.TLabel", font=("Segoe UI", 9), foreground="#667085")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Accent.TButton", background="#315efb", foreground="white")
        style.map("Accent.TButton", background=[("active", "#244bd1")])
        style.configure("TNotebook", background="#f3f5f9", borderwidth=0)
        style.configure("TNotebook.Tab", padding=(14, 8), font=("Segoe UI", 10, "bold"))

    def _build(self):
        header = ttk.Frame(self.root, padding=(22, 18))
        header.pack(fill="x")
        ttk.Label(header, text="AI ATS Resume Builder Pro", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Create a job-targeted resume • Check keyword coverage • Export PDF / DOCX", style="Sub.TLabel").pack(anchor="w", pady=(3,0))
        bar = ttk.Frame(self.root, padding=(20, 0, 20, 12))
        bar.pack(fill="x")
        ttk.Label(bar, text="Resume design:").pack(side="left")
        self.template_var = tk.StringVar(value=TEMPLATES[0])
        ttk.Combobox(bar, textvariable=self.template_var, values=TEMPLATES, state="readonly", width=32).pack(side="left", padx=8)
        ttk.Label(bar, text="100 layouts included • ATS-safe single-column output", style="Sub.TLabel").pack(side="left", padx=10)

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(0,12))
        self.profile_tab = ttk.Frame(self.tabs, padding=14)
        self.jd_tab = ttk.Frame(self.tabs, padding=14)
        self.preview_tab = ttk.Frame(self.tabs, padding=14)
        self.tabs.add(self.profile_tab, text="1  Profile & Details")
        self.tabs.add(self.jd_tab, text="2  Job Description")
        self.tabs.add(self.preview_tab, text="3  Resume Editor & ATS")

        self.vars = {}
        self._profile_form()
        self._jd_form()
        self._preview_form()

        footer = ttk.Frame(self.root, padding=(20, 0, 20, 16))
        footer.pack(fill="x")
        ttk.Button(footer, text="Generate ATS Resume", style="Accent.TButton", command=self.generate).pack(side="left")
        ttk.Button(footer, text="Export PDF", command=self.export_pdf).pack(side="left", padx=8)
        ttk.Button(footer, text="Export DOCX", command=self.export_docx).pack(side="left")
        ttk.Button(footer, text="Clear All", command=self.clear_all).pack(side="right")

    def add_field(self, parent, key, label, height=1, width=60):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=8)
        frame.pack(fill="x", pady=4)
        ttk.Label(frame, text=label, background="#ffffff", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        if height == 1:
            widget = ttk.Entry(frame, width=width)
            widget.pack(fill="x", pady=(4,0))
        else:
            widget = tk.Text(frame, height=height, wrap="word", font=("Segoe UI", 10), relief="solid", bd=1, padx=6, pady=5)
            widget.pack(fill="x", pady=(4,0))
        self.vars[key] = widget

    def _profile_form(self):
        canvas = tk.Canvas(self.profile_tab, bg="#f3f5f9", highlightthickness=0)
        scroll = ttk.Scrollbar(self.profile_tab, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=inner, anchor="nw", width=canvas.winfo_width() or 900)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True); scroll.pack(side="right", fill="y")
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(1, width=e.width))
        self.add_field(inner, "name", "Full name")
        self.add_field(inner, "email", "Email address")
        self.add_field(inner, "phone", "Phone number")
        self.add_field(inner, "location", "City / Location")
        self.add_field(inner, "summary", "Professional summary (optional – generated if blank)", 3)
        self.add_field(inner, "skills", "Skills (comma separated)", 3)
        self.add_field(inner, "education", "Education (qualification, institute, year, marks)", 3)
        self.add_field(inner, "experience", "Work experience / internship (role, company, dates, achievements)", 4)
        self.add_field(inner, "projects", "Projects / certifications / achievements", 3)

    def _jd_form(self):
        ttk.Label(self.jd_tab, text="Paste the complete job description below", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(self.jd_tab, text="The local analyzer extracts repeated role-related terms and compares them with the skills you provide.").pack(anchor="w", pady=(4,10))
        self.jd_text = tk.Text(self.jd_tab, wrap="word", font=("Segoe UI", 10), padx=10, pady=10, relief="solid", bd=1)
        self.jd_text.pack(fill="both", expand=True)
        self.jd_text.insert("1.0", "Paste job title, responsibilities, required skills and qualifications here...")
        ttk.Label(self.jd_tab, text="Tip: Use the full JD for better keyword analysis. Only include skills and experience you genuinely have.", style="Sub.TLabel").pack(anchor="w", pady=8)

    def _preview_form(self):
        top = ttk.Frame(self.preview_tab)
        top.pack(fill="x")
        self.score_label = ttk.Label(top, text="ATS score: Not checked", font=("Segoe UI", 15, "bold"))
        self.score_label.pack(side="left")
        self.match_label = ttk.Label(top, text="Keyword match: —", style="Sub.TLabel")
        self.match_label.pack(side="right")
        body = ttk.Panedwindow(self.preview_tab, orient="horizontal")
        body.pack(fill="both", expand=True, pady=10)
        left = ttk.Frame(body, padding=6); right = ttk.Frame(body, padding=6)
        body.add(left, weight=3); body.add(right, weight=2)
        ttk.Label(left, text="Editable resume content", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.editor = tk.Text(left, wrap="word", font=("Segoe UI", 10), padx=10, pady=10, undo=True)
        self.editor.pack(fill="both", expand=True, pady=6)
        ttk.Label(right, text="ATS analysis", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.analysis = tk.Text(right, wrap="word", font=("Segoe UI", 9), padx=9, pady=9, state="disabled")
        self.analysis.pack(fill="both", expand=True, pady=6)

    def get_data(self):
        data = {}
        for key, widget in self.vars.items():
            data[key] = widget.get() if isinstance(widget, ttk.Entry) else widget.get("1.0", "end-1c")
        data["jd"] = self.jd_text.get("1.0", "end-1c")
        return data

    def generate(self):
        data = self.get_data()
        resume = make_resume(data)
        score, checks, ratio = calculate_score(resume, data)
        lines = [resume["name"], resume["contact"], ""]
        for heading, content in resume["sections"]:
            lines += [heading, content, ""]
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", "\n".join(lines))
        self.score_label.configure(text=f"ATS readiness estimate: {score}/100")
        self.match_label.configure(text=f"Keyword match: {len(resume['matched'])}/{len(resume['keywords'])} ({ratio:.0%})")
        report = [f"ATS readiness estimate: {score}/100", "", "CHECKLIST"]
        report += [("✓ " if ok else "• ") + label for _, ok, label in checks]
        report += ["", "MATCHED KEYWORDS"] + (resume["matched"] or ["No matching keywords detected yet."])
        report += ["", "POTENTIALLY MISSING KEYWORDS"] + (resume["missing"][:20] or ["No obvious gaps from this basic scan."])
        report += ["", "Important: This is a heuristic checklist, not a real ATS vendor score. Add only truthful skills; do not claim skills you do not have."]
        self.analysis.configure(state="normal"); self.analysis.delete("1.0","end"); self.analysis.insert("1.0","\n".join(report)); self.analysis.configure(state="disabled")
        self.last_resume = resume; self.last_data = data
        self.tabs.select(self.preview_tab)

    def _editor_text(self):
        txt = self.editor.get("1.0", "end-1c").strip()
        if not txt: raise ValueError("Please generate or enter resume content first.")
        return txt

    def export_pdf(self):
        try:
            from reportlab.lib.pagesizes import LETTER
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            content = self._editor_text()
            path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF file","*.pdf")], initialfile="ATS_Resume.pdf")
            if not path: return
            styles = getSampleStyleSheet()
            title = ParagraphStyle("ResumeTitle", parent=styles["Title"], textColor=colors.HexColor("#1d3557"), alignment=0, fontSize=18, spaceAfter=5)
            heading = ParagraphStyle("ResumeHeading", parent=styles["Heading2"], textColor=colors.HexColor("#1d3557"), fontSize=10, leading=13, spaceBefore=9, spaceAfter=3)
            normal = ParagraphStyle("ResumeBody", parent=styles["BodyText"], fontSize=9, leading=12, spaceAfter=4)
            story = []
            for idx, line in enumerate(content.splitlines()):
                safe = html.escape(line)
                if idx == 0: story.append(Paragraph(safe, title))
                elif line.isupper() and len(line) < 45: story.append(Paragraph(safe, heading))
                else: story.append(Paragraph(safe or "&nbsp;", normal))
            SimpleDocTemplate(path, pagesize=LETTER, rightMargin=.65*inch, leftMargin=.65*inch, topMargin=.55*inch, bottomMargin=.55*inch).build(story)
            messagebox.showinfo("Export complete", f"PDF saved:\n{path}")
        except ImportError:
            messagebox.showerror("Missing library", "PDF export library is missing. Rebuild using the included GitHub workflow.")
        except Exception as e: messagebox.showerror("PDF export failed", str(e))

    def export_docx(self):
        try:
            from docx import Document
            from docx.shared import Pt, Inches, RGBColor
            content = self._editor_text()
            path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word document","*.docx")], initialfile="ATS_Resume.docx")
            if not path: return
            doc = Document()
            sec = doc.sections[0]; sec.top_margin = Inches(.55); sec.bottom_margin = Inches(.55)
            for idx, line in enumerate(content.splitlines()):
                if idx == 0:
                    p = doc.add_paragraph(); r = p.add_run(line); r.bold = True; r.font.size = Pt(19); r.font.color.rgb = RGBColor(29,53,87)
                elif line.isupper() and len(line) < 45:
                    p = doc.add_paragraph(); r = p.add_run(line); r.bold = True; r.font.size = Pt(10); r.font.color.rgb = RGBColor(29,53,87)
                else:
                    p = doc.add_paragraph(line); p.paragraph_format.space_after = Pt(3)
                    for r in p.runs: r.font.size = Pt(9)
            doc.save(path)
            messagebox.showinfo("Export complete", f"DOCX saved:\n{path}")
        except ImportError:
            messagebox.showerror("Missing library", "DOCX export library is missing. Rebuild using the included GitHub workflow.")
        except Exception as e: messagebox.showerror("DOCX export failed", str(e))

    def clear_all(self):
        if not messagebox.askyesno("Clear all", "Clear all profile details and resume content?"): return
        for widget in self.vars.values():
            if isinstance(widget, ttk.Entry): widget.delete(0, "end")
            else: widget.delete("1.0", "end")
        self.jd_text.delete("1.0", "end")
        self.editor.delete("1.0", "end")
        self.analysis.configure(state="normal"); self.analysis.delete("1.0","end"); self.analysis.configure(state="disabled")
        self.score_label.configure(text="ATS score: Not checked"); self.match_label.configure(text="Keyword match: —")
        self.last_resume = None

def main():
    root = tk.Tk()
    ResumeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

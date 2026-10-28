#!/usr/bin/env python3
"""Generates the professional 4-6 page PDF engineering report for GymFlow-v2.
Session 9 Software Engineering Assignment.
"""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PROJECT_ROOT = Path(__file__).resolve().parent
PDF_PATH = PROJECT_ROOT / "GymFlow_Session9_Report.pdf"


class NumberedCanvas(canvas.Canvas):
    """Canvas that tracks page count and adds running headers and footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#6B7280"))

        # Header (Pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 755, "GymFlow-v2 — Software Engineering Project Report")
            self.drawRightString(558, 755, "Session 9 Assignment")
            self.setStrokeColor(colors.HexColor("#E5E7EB"))
            self.setLineWidth(0.5)
            self.line(54, 748, 558, 748)

        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#E5E7EB"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)

        self.setFont("Helvetica", 8)
        self.drawString(54, 32, "Author: Ibrahim Khalil | Python 3.12, CustomTkinter, MySQL")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=27,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=3,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#D97706"),
        spaceAfter=10,
    )

    meta_style = ParagraphStyle(
        "DocMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#4B5563"),
        spaceAfter=12,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16.5,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13.5,
        textColor=colors.HexColor("#B45309"),
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.8,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=5,
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1F2937"),
        leftIndent=10,
        spaceAfter=2.5,
    )

    table_text = ParagraphStyle(
        "TableText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.8,
        leading=10,
        textColor=colors.HexColor("#1F2937"),
    )

    table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=colors.white,
    )

    story = []

    # =========================================================================
    # PAGE 1: TITLE, MOTIVATION, PROBLEM STATEMENT, CORE REQUIREMENTS
    # =========================================================================
    story.append(Paragraph("GymFlow-v2: Architectural Improvement & System Completion", title_style))
    story.append(Paragraph("Session 9 Software Engineering Assignment Report", subtitle_style))
    story.append(Paragraph("<b>Author:</b> Ibrahim Khalil &nbsp;|&nbsp; <b>Repository:</b> Mtgazer/GymFLow-v2 &nbsp;|&nbsp; <b>Branch:</b> feature/session-9-completion &nbsp;|&nbsp; <b>Date:</b> October 2026", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#D97706"), spaceAfter=8))

    story.append(Paragraph("1. Project Motivation and Problem Statement", h1_style))
    story.append(Paragraph(
        "Modern fitness centers require dependable, responsive management software to handle daily desk operations, member registrations, subscription renewals, and financial tracking. Many existing management tools either rely on bloated web-based SaaS solutions with ongoing monthly fees or fragmented spreadsheets that introduce data corruption and concurrency errors.",
        body_style,
    ))
    story.append(Paragraph(
        "GymFlow-v2 was conceived as a high-performance, modular desktop GUI application built using Python and CustomTkinter. The existing starter codebase provided an aesthetic UI and basic SQLite routines, but lacked essential enterprise software engineering standards. Specifically, it suffered from hardcoded SQLite dependencies without MySQL integration, absence of formal design patterns, missing abstraction and encapsulation in models, zero automated test coverage, and no specialized data structures for undo or caching.",
        body_style,
    ))

    story.append(Paragraph("2. System Overview and Core Functional Requirements", h1_style))
    story.append(Paragraph(
        "GymFlow-v2 delivers an end-to-end gym administration suite. The system is engineered to provide full CRUD operations across multiple entities, support transactional permanence, and maintain complete decoupling between user interface widgets and persistence engines.",
        body_style,
    ))

    features_data = [
        [Paragraph("Feature Domain", table_header), Paragraph("Functional Capability", table_header), Paragraph("Engineering Implementation", table_header)],
        [
            Paragraph("<b>Member Management</b>", table_text),
            Paragraph("Create, Read, Update, and Delete gym members with validation.", table_text),
            Paragraph("MemberRepository, MemberService, custom dialogs with in-UI validation feedback.", table_text),
        ],
        [
            Paragraph("<b>Subscription Tracking</b>", table_text),
            Paragraph("Multi-tier membership plans (Basic, Premium, Gold, VIP) with automatic expiration calculation.", table_text),
            Paragraph("PlanRepository, Subscriptions table with foreign key cascading and status tracking.", table_text),
        ],
        [
            Paragraph("<b>Real-Time Analytics</b>", table_text),
            Paragraph("Dashboard displaying total active/expired members, gross revenue, and recent subscriptions.", table_text),
            Paragraph("DashboardRepository aggregation queries (SQL SUM, COUNT, CURDATE filtering).", table_text),
        ],
        [
            Paragraph("<b>Resilient Data Storage</b>", table_text),
            Paragraph("Enterprise MySQL database with transparent offline fallback to SQLite.", table_text),
            Paragraph("DatabaseConnectionManager Singleton, parameterized queries, .env loading.", table_text),
        ],
        [
            Paragraph("<b>LIFO Undo Operations</b>", table_text),
            Paragraph("Instant reversal of accidental member deletions, updates, and registrations.", table_text),
            Paragraph("In-memory UndoStack supporting dynamic inverse lambda execution.", table_text),
        ],
    ]
    t_feat = Table(features_data, colWidths=[115, 195, 194])
    t_feat.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_feat)
    story.append(Spacer(1, 8))

    story.append(Paragraph("3. Full CRUD Implementation Lifecycle", h1_style))
    story.append(Paragraph(
        "Every entity adheres to comprehensive Create, Read, Update, and Delete lifecycles across all layers: GUI dialogs validate inputs (names, phone formats, numeric prices) and report errors immediately on-screen; application services apply business constraints; repositories construct parameterized SQL statements; and database managers commit transactions safely.",
        body_style,
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: ARCHITECTURE, DESIGN PATTERNS, OOP PRINCIPLES
    # =========================================================================
    story.append(Paragraph("4. Software Architecture Pattern: Layered Architecture", h1_style))
    story.append(Paragraph(
        "GymFlow-v2 is organized according to a strict <b>Four-Layered Architecture</b>. This architectural pattern enforces separation of concerns, ensures unidirectional dependency flow, and prevents high-level business rules or low-level database operations from leaking into presentation widgets.",
        body_style,
    ))

    arch_data = [
        [Paragraph("Layer", table_header), Paragraph("Key Responsibilities & Components", table_header), Paragraph("Coupling Rules & Isolation", table_header)],
        [
            Paragraph("<b>1. Presentation Layer</b><br/>(<code>ui/</code>)", table_text),
            Paragraph("CustomTkinter windows, frames, cards, and modal dialogs (<code>Sidebar</code>, <code>Dashboard</code>, <code>Members</code>, <code>AddMemberDialog</code>). Handles user events and view rendering.", table_text),
            Paragraph("Strictly communicates with Service layer. Contains zero SQL queries or raw database connectors.", table_text),
        ],
        [
            Paragraph("<b>2. Business Logic Layer</b><br/>(<code>services/</code>)", table_text),
            Paragraph("Application services (<code>MemberService</code>, <code>DashboardService</code>). Enforces validation rules, plan calculations, undo recording, and data structure updates.", table_text),
            Paragraph("Independent of GUI widgets. Interacts solely with Repositories and in-memory data structures.", table_text),
        ],
        [
            Paragraph("<b>3. Data Access Layer</b><br/>(<code>repositories/</code>)", table_text),
            Paragraph("Concrete repositories (<code>MemberRepository</code>, <code>PlanRepository</code>, <code>DashboardRepository</code>) and connection manager (<code>DatabaseConnectionManager</code>).", table_text),
            Paragraph("Encapsulates all SQL syntax, joins, transactions, and parameterization. Decouples business logic from SQL dialects.", table_text),
        ],
        [
            Paragraph("<b>4. Domain / Model Layer</b><br/>(<code>models.py</code>)", table_text),
            Paragraph("Core business entities (<code>BaseEntity</code>, <code>Person</code>, <code>Member</code>, <code>Plan</code>, <code>Subscription</code>).", table_text),
            Paragraph("Defines domain contracts, encapsulation properties, serialization (<code>to_dict</code>, <code>from_db</code>), and status checks.", table_text),
        ],
    ]
    t_arch = Table(arch_data, colWidths=[105, 215, 184])
    t_arch.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 8))

    story.append(Paragraph("5. Software Design Patterns Implementation", h1_style))
    story.append(Paragraph("<b>A. Repository Pattern:</b> The system implements generic <code>BaseRepository[T]</code> defining abstract CRUD signatures (<code>add</code>, <code>get_by_id</code>, <code>get_all</code>, <code>update</code>, <code>delete</code>). Concrete implementations (<code>MemberRepository</code>, <code>PlanRepository</code>) encapsulate all SQL query formulation. The service layer interacts exclusively through repositories, enabling seamless switching between MySQL and SQLite without altering business logic.", body_style))
    story.append(Paragraph("<b>B. Singleton Pattern:</b> The <code>DatabaseConnectionManager</code> class implements a thread-safe Singleton pattern using a double-checked class locking mechanism (<code>threading.Lock</code>). This guarantees that only one coordinated database connection exists across all application threads, optimizing connection pooling and preventing connection starvation.", body_style))

    story.append(Paragraph("6. Object-Oriented Programming (OOP) Principles", h1_style))
    story.append(Paragraph(
        "All four core OOP principles are natively implemented across the domain and persistence classes:",
        body_style,
    ))
    story.append(Paragraph("• <b>Abstraction:</b> <code>BaseEntity(ABC)</code> and <code>BaseRepository(ABC)</code> establish clean contracts with <code>@abstractmethod</code> decorators, hiding complex internal SQL generation and database driver details.", bullet_style))
    story.append(Paragraph("• <b>Inheritance:</b> A logical hierarchy is established: <code>BaseEntity</code> &rarr; <code>Person</code> &rarr; <code>Member</code>. <code>Member</code> inherits demographic attributes from <code>Person</code> and identity tracking from <code>BaseEntity</code>, while adding gym-specific behaviors.", bullet_style))
    story.append(Paragraph("• <b>Encapsulation:</b> Protected attributes (<code>_full_name</code>, <code>_phone</code>, <code>_age</code>) are encapsulated with <code>@property</code> getters and setters that enforce validation invariants (e.g. non-empty names, valid phone digits, positive ages).", bullet_style))
    story.append(Paragraph("• <b>Polymorphism:</b> Overridden factory methods (<code>from_db</code>) and serialization methods (<code>to_dict</code>) allow polymorphic handling of diverse domain entities across data structures and repositories.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: DATA STRUCTURES & MYSQL DATABASE INTEGRATION
    # =========================================================================
    story.append(Paragraph("7. Domain-Specific Data Structures", h1_style))
    story.append(Paragraph(
        "Rather than relying solely on default containers, GymFlow-v2 incorporates three specialized data structures engineered to solve genuine performance and operational problems in the gym domain:",
        body_style,
    ))

    ds_data = [
        [Paragraph("Data Structure", table_header), Paragraph("GymFlow Implementation", table_header), Paragraph("Time Complexity", table_header), Paragraph("Operational Rationale", table_header)],
        [
            Paragraph("<b>Dictionary</b><br/>(Hash Map)", table_text),
            Paragraph("<code>MemberLookupIndex</code><br/>Dual-keyed by member ID and phone.", table_text),
            Paragraph("Lookups: <b>O(1)</b><br/>Insertion: <b>O(1)</b><br/>Removal: <b>O(1)</b>", table_text),
            Paragraph("Provides instantaneous O(1) lookups during member search and phone uniqueness validation without issuing repeated database queries.", table_text),
        ],
        [
            Paragraph("<b>Stack</b><br/>(LIFO)", table_text),
            Paragraph("<code>UndoStack[UndoAction]</code><br/>Bounded depth (max 50 actions).", table_text),
            Paragraph("Push: <b>O(1)</b><br/>Pop: <b>O(1)</b><br/>Peek: <b>O(1)</b>", table_text),
            Paragraph("Enables desk operators to undo accidental member deletions, profile edits, or registrations in Last-In, First-Out sequence.", table_text),
        ],
        [
            Paragraph("<b>Queue</b><br/>(FIFO)", table_text),
            Paragraph("<code>ActivityQueue</code><br/>Backed by <code>collections.deque</code>.", table_text),
            Paragraph("Enqueue: <b>O(1)</b><br/>Dequeue: <b>O(1)</b>", table_text),
            Paragraph("Tracks operational events (registrations, renewals, deletes) in chronological First-In, First-Out order for auditing and logging.", table_text),
        ],
    ]
    t_ds = Table(ds_data, colWidths=[85, 145, 95, 179])
    t_ds.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_ds)
    story.append(Spacer(1, 8))

    story.append(Paragraph("8. MySQL Database Integration and Schema Design", h1_style))
    story.append(Paragraph(
        "The project integrates enterprise MySQL storage via <code>mysql-connector-python</code> and <code>pymysql</code> with strict security and reliability measures:",
        body_style,
    ))
    story.append(Paragraph("• <b>Relational Schema:</b> Defined in <code>database/schema.sql</code> featuring four normalized tables: <code>members</code> (demographics and unique phone constraint), <code>plans</code> (duration and pricing tiers), <code>subscriptions</code> (member contracts with foreign key cascading and enum payment status), and <code>activity_logs</code> (audit trail).", bullet_style))
    story.append(Paragraph("• <b>Security & Credentials:</b> Zero hardcoded credentials. Database host, port, user, password, and database name are dynamically loaded from environment variables using <code>python-dotenv</code>. An annotated <code>.env.example</code> template is provided, and <code>.env</code> is excluded via <code>.gitignore</code>.", bullet_style))
    story.append(Paragraph("• <b>SQL Injection Prevention:</b> All database queries utilize parameterized placeholders (<code>%s</code> for MySQL, <code>?</code> for SQLite), completely mitigating SQL injection vulnerabilities.", bullet_style))
    story.append(Paragraph("• <b>Fault Tolerance & Fallback:</b> If MySQL is unavailable (e.g. during offline development or on machines without a running MySQL daemon), <code>DatabaseConnectionManager</code> logs a warning and transparently switches to local SQLite (<code>gym.db</code>), ensuring the application and test suites run continuously.", bullet_style))

    schema_summary = [
        [Paragraph("Table Name", table_header), Paragraph("Primary Key", table_header), Paragraph("Foreign Keys & Constraints", table_header), Paragraph("Key Attributes", table_header)],
        [Paragraph("<code>members</code>", table_text), Paragraph("<code>id</code> (AUTO_INCREMENT)", table_text), Paragraph("<code>phone UNIQUE</code>", table_text), Paragraph("full_name, phone, age, gender, created_at", table_text)],
        [Paragraph("<code>plans</code>", table_text), Paragraph("<code>id</code> (AUTO_INCREMENT)", table_text), Paragraph("<code>name UNIQUE</code>", table_text), Paragraph("name, duration_days, price, created_at", table_text)],
        [Paragraph("<code>subscriptions</code>", table_text), Paragraph("<code>id</code> (AUTO_INCREMENT)", table_text), Paragraph("FK member_id &rarr; members(id) [CASCADE]<br/>FK plan_id &rarr; plans(id)", table_text), Paragraph("start_date, end_date, payment_status, price_paid", table_text)],
        [Paragraph("<code>activity_logs</code>", table_text), Paragraph("<code>id</code> (AUTO_INCREMENT)", table_text), Paragraph("None", table_text), Paragraph("action_type, entity_name, description, timestamp", table_text)],
    ]
    t_sch = Table(schema_summary, colWidths=[85, 115, 150, 154])
    t_sch.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_sch)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: UML DIAGRAMS (USE CASE & SEQUENCE DIAGRAM)
    # =========================================================================
    story.append(Paragraph("9. System UML Diagrams: Use Case & Sequence", h1_style))
    story.append(Paragraph(
        "All UML diagrams are authored from the actual source code and stored in <code>docs/uml/</code> in both Mermaid specification (<code>.mmd</code>) and rendered high-resolution PNG format.",
        body_style,
    ))

    # Diagram A: Use Case Diagram
    story.append(Paragraph("A. System Use Case Diagram", h2_style))
    story.append(Paragraph("Illustrates the interactions between the primary actor (Gym Desk Operator) and GymFlow-v2 capabilities.", body_style))

    uc_img_path = PROJECT_ROOT / "docs" / "uml" / "use_case_diagram.png"
    if uc_img_path.exists():
        story.append(Image(str(uc_img_path), width=480, height=210))
    story.append(Spacer(1, 6))

    # Diagram C: Sequence Diagram
    story.append(Paragraph("B. Sequence Diagram: Member Registration Lifecycle", h2_style))
    story.append(Paragraph("Depicts the end-to-end communication across GUI, Service, Repository, Database Manager, and Data Structures during a registration operation.", body_style))

    seq_img_path = PROJECT_ROOT / "docs" / "uml" / "sequence_diagram.png"
    if seq_img_path.exists():
        story.append(Image(str(seq_img_path), width=480, height=255))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: CLASS DIAGRAM & GUI APPLICATION SCREENSHOTS
    # =========================================================================
    story.append(Paragraph("10. System Class Diagram and GUI Screenshots", h1_style))
    story.append(Paragraph("C. Detailed System Class Diagram", h2_style))
    story.append(Paragraph("Depicts domain models, repositories, Singleton connection manager, services, and UI components with exact relationships.", body_style))

    cls_img_path = PROJECT_ROOT / "docs" / "uml" / "class_diagram.png"
    if cls_img_path.exists():
        story.append(Image(str(cls_img_path), width=490, height=195))
    story.append(Spacer(1, 6))

    story.append(Paragraph("D. Actual GUI Screenshots", h2_style))
    story.append(Paragraph("Captured directly from the running CustomTkinter application using Linux Xwayland window buffer inspection:", body_style))

    dash_screen = PROJECT_ROOT / "docs" / "screenshots" / "dashboard_view.png"
    members_screen = PROJECT_ROOT / "docs" / "screenshots" / "members_view.png"
    add_screen = PROJECT_ROOT / "docs" / "screenshots" / "add_member_dialog.png"
    edit_screen = PROJECT_ROOT / "docs" / "screenshots" / "edit_member_dialog.png"

    img_table_data = [
        [Paragraph("<b>Figure 1: Dashboard View</b> (Live Analytics & Recent Activity)", body_style), Paragraph("<b>Figure 2: Members View</b> (Search, Cards, & Undo Action)", body_style)],
        [Image(str(dash_screen), width=240, height=135), Image(str(members_screen), width=240, height=135)],
        [Paragraph("<b>Figure 3: Add Member Modal</b> (Input Validation & Plans)", body_style), Paragraph("<b>Figure 4: Edit Member Modal</b> (Profile Updates)", body_style)],
        [Image(str(add_screen), width=180, height=125), Image(str(edit_screen), width=180, height=125)],
    ]
    t_imgs = Table(img_table_data, colWidths=[250, 250])
    t_imgs.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(t_imgs)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: TESTING, MANUAL VERIFICATION, DELIVERABLES, CONCLUSION
    # =========================================================================
    story.append(Paragraph("11. Quality Assurance & Automated Test Results", h1_style))
    story.append(Paragraph(
        "A comprehensive automated test suite was constructed using <code>pytest</code>, achieving 100% pass rate across 27 distinct test cases. Tests verify domain models, repositories against an isolated database, business logic, undo mechanisms, and design patterns:",
        body_style,
    ))

    test_summary = [
        [Paragraph("Test Module", table_header), Paragraph("Focus Area", table_header), Paragraph("Passed / Total", table_header), Paragraph("Status", table_header)],
        [Paragraph("<code>test_models.py</code>", table_text), Paragraph("Encapsulation, inheritance hierarchy, active calculations, serialization.", table_text), Paragraph("6 / 6", table_text), Paragraph("<font color='#16A34A'><b>PASSED</b></font>", table_text)],
        [Paragraph("<code>test_data_structures.py</code>", table_text), Paragraph("Dictionary O(1) index, UndoStack LIFO ordering, ActivityQueue FIFO drain.", table_text), Paragraph("5 / 5", table_text), Paragraph("<font color='#16A34A'><b>PASSED</b></font>", table_text)],
        [Paragraph("<code>test_patterns.py</code>", table_text), Paragraph("Singleton instance identity, thread safety, Repository conformance, MySQL fallback.", table_text), Paragraph("6 / 6", table_text), Paragraph("<font color='#16A34A'><b>PASSED</b></font>", table_text)],
        [Paragraph("<code>test_repositories.py</code>", table_text), Paragraph("Isolated database CRUD operations, plan management, analytical metrics.", table_text), Paragraph("3 / 3", table_text), Paragraph("<font color='#16A34A'><b>PASSED</b></font>", table_text)],
        [Paragraph("<code>test_services.py</code>", table_text), Paragraph("Input validation, duplicate phone check, edit/delete with undo restoration.", table_text), Paragraph("7 / 7", table_text), Paragraph("<font color='#16A34A'><b>PASSED</b></font>", table_text)],
    ]
    t_test = Table(test_summary, colWidths=[120, 220, 80, 84])
    t_test.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_test)
    story.append(Spacer(1, 8))

    story.append(Paragraph("12. Manual GUI Testing & Operational Verification Steps", h1_style))
    story.append(Paragraph(
        "To verify end-to-end functionality manually in any desktop environment, follow these steps:",
        body_style,
    ))
    story.append(Paragraph("1. <b>Application Launch:</b> Run <code>python app.py</code>. Verify window initializes at 1200x700 with dark aesthetic theme and sidebar.", bullet_style))
    story.append(Paragraph("2. <b>Navigation:</b> Click 'Members' in sidebar. Confirm active indicator updates and the members list view renders.", bullet_style))
    story.append(Paragraph("3. <b>Create Member:</b> Click '+ Add Member'. Fill full name, phone number, choose 'Gold' plan ($500), and click 'Save Member'. Confirm new card appears.", bullet_style))
    story.append(Paragraph("4. <b>Fast Search:</b> Type member name or phone in search box. Confirm cards filter dynamically using O(1) in-memory index.", bullet_style))
    story.append(Paragraph("5. <b>Edit Member:</b> Click 'Edit' on a card. Update phone number, click 'Save Changes'. Confirm card displays new info.", bullet_style))
    story.append(Paragraph("6. <b>LIFO Undo:</b> Click '↺ Undo' button in toolbar. Confirm edit is reversed and original info is restored.", bullet_style))
    story.append(Paragraph("7. <b>Delete Member:</b> Click 'Delete', confirm in modal dialog. Member is removed. Click '↺ Undo' to test full restoration.", bullet_style))
    story.append(Paragraph("8. <b>Dashboard Refresh:</b> Switch to 'Dashboard'. Confirm member count, active subscriptions, and revenue reflect changes.", bullet_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("13. Deliverables and Repository Artifacts Summary", h1_style))
    story.append(Paragraph(
        "The completed engineering deliverables include: (1) Complete Python source code adhering to 4-Layer Architecture; (2) MySQL schema (<code>database/schema.sql</code>) and automated initializer (<code>database/init_db.py</code>); (3) GoF Repository and Singleton Design Patterns; (4) Domain Data Structures (Dictionary index, Undo Stack, Event Queue); (5) 3 UML Diagrams (Mermaid sources and high-res PNGs in <code>docs/uml/</code>); (6) 4 GUI application screenshots in <code>docs/screenshots/</code>; (7) Automated test suite of 27 passing tests in <code>tests/</code>; (8) Comprehensive <code>README.md</code> and updated <code>PROJECT_AUDIT.md</code>; and (9) This comprehensive PDF engineering report.",
        body_style,
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("14. Conclusion", h1_style))
    story.append(Paragraph(
        "GymFlow-v2 has been successfully brought to full software engineering maturity, satisfying all requirements of the Session 9 Assignment. The existing aesthetic CustomTkinter interface was rigorously preserved, while the underlying architecture was elevated to a professional 4-Layer design utilizing the Repository Pattern and Singleton connection management. With enterprise MySQL support, domain data structures (Dictionary, LIFO Stack, FIFO Queue), 27 automated unit tests, and verified GUI execution, GymFlow-v2 stands as a robust, scalable gym management solution.",
        body_style,
    ))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] PDF generated at: {PDF_PATH}")


if __name__ == "__main__":
    build_pdf()

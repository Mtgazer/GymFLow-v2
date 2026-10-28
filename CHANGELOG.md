# Changelog

All notable changes to the GymFlow project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.0.0] - 2026-10-28

### Added
- **Enterprise MySQL Integration:**
  - Dynamic database connectivity supporting MySQL (`mysql-connector-python` and `pymysql`) configured securely via environment variables (`python-dotenv`).
  - Automated relational database schema script (`database/schema.sql`) with normalized tables (`members`, `plans`, `subscriptions`, `activity_logs`), cascading foreign key constraints, indexes, and initial plan seeds.
  - Automated database initialization and seeding utility (`database/init_db.py`).
  - Resilient offline fallback: automatic, transparent switch to local SQLite (`gym.db`) whenever a MySQL daemon is unreachable.
  - Environment variable template (`.env.example`) with zero committed credentials.
- **Software Design Patterns:**
  - **Repository Pattern:** Generic `BaseRepository[T]` interface with concrete implementations (`MemberRepository`, `PlanRepository`, `DashboardRepository`) completely decoupling application services from database SQL formulations.
  - **Singleton Pattern:** Thread-safe `DatabaseConnectionManager` with double-checked class locking (`threading.Lock`) for unified connection lifecycle management.
- **Domain-Specific Data Structures (`core/data_structures.py`):**
  - **Dictionary (`MemberLookupIndex`):** Dual-key hash index by member ID and unique phone number, enabling amortized $O(1)$ lookups and duplicate phone validation without redundant database roundtrips.
  - **Stack (`UndoStack`):** Bounded LIFO stack (capacity 50) that tracks inverse operations for member deletions, updates, and registrations.
  - **Queue (`ActivityQueue`):** Chronological FIFO event queue backed by `collections.deque` for administrative event logging and auditing.
- **GUI Enhancements & Interactive Undo:**
  - Interactive `↺ Undo` button in the Members toolbar displaying current stack depth and allowing one-click rollback of operations.
  - In-dialog error message banners in `AddMemberDialog`, `EditMemberDialog`, and `RenewMemberDialog` displaying clear validation feedback.
  - Automatic price auto-fill when switching membership plans in dialogs.
  - Empty state feedback when searches yield zero matching records.
- **Automated Test Suite:**
  - Comprehensive 27-test suite in `tests/` executed via `pytest -v` covering domain models, data structures, repositories, services, and design patterns against isolated test databases.
- **Documentation, UML, and Media Deliverables:**
  - 3 complete UML diagrams (Use Case, Sequence, Class) in Mermaid (`.mmd`) and high-resolution PNG format in `docs/uml/`.
  - Authentic, high-resolution GUI screenshots captured under Linux in `docs/screenshots/`.
  - Comprehensive 6-page PDF engineering report (`GymFlow_Session9_Report.pdf`).
  - Requirements audit document (`PROJECT_AUDIT.md`) tracking 100% completion of Session 9 specifications.

### Changed
- **Layered Architecture:** Refactored project into a strict 4-Layered Architecture (Presentation Layer, Business Logic Layer, Data Access Layer, Domain / Model Layer).
- **OOP Domain Hierarchy (`models.py`):**
  - Abstract base class `BaseEntity(ABC)` with abstract methods `to_dict()` and `from_db()`.
  - Class inheritance hierarchy: `BaseEntity` &rarr; `Person` &rarr; `Member`.
  - Encapsulated protected fields (`_full_name`, `_phone`, `_age`) with `@property` validation getters and setters.
- **Data Facade (`data/database.py`):** Refactored legacy database class into a backward-compatible facade delegating directly to repositories and connection manager.
- **Application Startup (`app.py`):** Wrapped execution in `if __name__ == "__main__":` to allow headless importing.
- **Version Metadata (`config.py`):** Upgraded `APP_VERSION` to `3.0.0` and `APP_NAME` to `GymFlow v3`.

### Fixed
- Fixed uncalled method reference bug in `MemberService.get_all_members`.
- Fixed unhandled `ValueError` when entering non-numeric pricing values in dialogs.
- Fixed sidebar active indicator synchronization when toggling between Dashboard and Members views.

---

## [2.0.0] - 2026-10-27
- Initial GymFlow v2 modular structure with CustomTkinter GUI, basic SQLite database handler, and initial dashboard/member views.

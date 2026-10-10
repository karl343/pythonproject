# Clinic Appointment Management System (ClinicMS)
## System Documentation & Project Report

---

## 1. System Overview and Architecture

### 1.1 Overview
The **Clinic Appointment Management System (ClinicMS)** is a desktop clinical application built with **Python 3**, **PyQt6**, **MySQL**, and **Matplotlib**. Designed for healthcare providers, clinic receptionists, and outpatient medical facilities, the software streamlines patient appointment scheduling, eliminates double-bookings, monitors real-time patient arrivals, tracks consultation outcomes, and presents visual caseload analytics.

### 1.2 Architecture Pattern: Model-View-Controller (MVC)
The project strictly implements the **Model-View-Controller (MVC)** architectural pattern to decouple data storage, business logic, and user interface rendering:

```
┌────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER (VIEW)                     │
│  MainWindow ── DashboardScreen, AddScreen, ViewAllScreen, SearchScreen,│
│                ModifyScreen, CancelScreen, DailyReportScreen,          │
│                AppointmentOutcomeDialog, DBSetupDialog, LoginDialog    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        BUSINESS LOGIC LAYER (CONTROLLER)               │
│  AppointmentController ── Validation, Conflict Detection,              │
│                           Arrival Alerts, Analytics Aggregation        │
│  AuthController        ── Authentication, Session & User Roles         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER (MODEL)                           │
│  DataManager ── CRUD Operations, Formatted ID Sequence (APT-0001)      │
│  Database    ── MySQL Connection Pool & Auto Schema Bootstrapping      │
└────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Key Modules & Responsibilities

| Module / File | Component | Description |
| :--- | :--- | :--- |
| `main.py` | Application Entry | Configures the application palette, executes the resilient MySQL connection retry loop, bootstraps the database schema, handles login, and launches the main window. |
| `models/database.py` | Connection Pooling | Manages a pooled connection manager (`MySQLConnectionPool`) based on `db_config.json`. |
| `models/data_manager.py` | Data Persistence | Handles parameterized SQL queries, auto-generates IDs (`APT-0001`), prevents SQL injection, checks slot conflicts, and loads user seed data. |
| `controllers/appointment_controller.py` | Business Controller | Enforces scheduling rules (double-booking detection, 11-digit phone validation), filters appointments, and aggregates analytics. |
| `controllers/auth_controller.py` | Auth Controller | Verifies credentials, manages admin authentication, and controls access permissions. |
| `views/main_window.py` | Primary Shell | Features a sidebar with 7 navigation screens, a real-time digital clock, and a 10-second background arrival monitor. |
| `views/outcome_dialog.py` | Outcome Dialog | Modal dialog triggered when an appointment's time arrives, allowing staff to log visit outcomes (Successful/Completed, Not Successful/No Show, Notes) or snooze. |
| `views/db_setup_dialog.py` | Setup Dialog | Dynamic connection dialog presented if MySQL is offline or requires updated credentials. |
| `views/screens/dashboard_screen.py` | Dashboard | Visual clinical metrics: 4 KPI cards, Matplotlib Donut Status Distribution chart, Doctor Caseload horizontal bar chart, and Today's Schedule table. |
| `views/screens/add_screen.py` | Add Screen | Booking form with 11-digit numeric contact validation and real-time double-booking collision checks. |
| `views/screens/view_all_screen.py` | View All Screen | Chronological roster of appointments with color-coded status badges and sortable columns. |
| `views/screens/search_screen.py` | Search Screen | Real-time search engine filtering records by Patient Name, Appointment ID, or Assigned Physician. |
| `views/screens/modify_screen.py` | Modify Screen | Appointment editor for updating patient info, contact numbers, or rescheduling time slots with conflict prevention. |
| `views/screens/cancel_screen.py` | Cancel Screen | Soft-cancel appointments (updating status to Cancelled) or permanently remove records with confirmation safety checks. |
| `views/screens/daily_report_screen.py` | Daily Report | Calendar-driven daily report detailing patient rosters and status distributions for any selected date. |

### 1.4 Core Business Rules
1. **Double-Booking Collision Prevention**: A physician cannot be booked for more than one consultation at the identical date and time slot.
2. **Strict Contact Number Validation**: Contact fields strictly restrict input to digits (`0-9`), cap character length at exactly 11 digits (Philippine mobile standard), and enforce validation at both the UI layer (`QRegularExpressionValidator`) and the controller layer.
3. **Sequential ID Formatting**: Appointments receive zero-padded, formatted identifiers automatically (`APT-0001`, `APT-0002`).

---

## 2. System Testing & Test Cases

### 2.1 Testing Methodology
The application was evaluated through a combination of **Unit Testing**, **Integration Testing**, and **End-to-End (E2E) Functional UI Testing**. Tests verified that user interfaces operate smoothly, user inputs are strictly sanitized, collision detection prevents duplicate schedules, background timers track patient arrivals, and the MySQL database maintains data integrity.

### 2.2 Comprehensive Test Cases Table

| Test Case | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- |
| **System Startup & Database Handshake** | Connect to MySQL database and initialize tables automatically | Database connected and tables created | **Passed** |
| **Database Connection Failure Recovery** | Launch database setup dialog if connection fails | `DBSetupDialog` displayed for credential re-entry | **Passed** |
| **User Login (Valid Credentials)** | Authenticate user and grant access to the main dashboard | User authenticated; main window opened | **Passed** |
| **User Login (Invalid Credentials)** | Deny access and display invalid credentials error | Access denied; error message displayed | **Passed** |
| **Add Appointment (Valid Data)** | Save new appointment with auto-generated ID (e.g., `APT-0001`) | Appointment saved to database; ID assigned | **Passed** |
| **Add Appointment (Empty Patient Name)** | Block submission and alert user that name is required | Form blocked; *"Patient Name is required."* shown | **Passed** |
| **Add Appointment (Empty Contact Info)** | Block submission and alert user that contact is required | Form blocked; *"Contact Information is required."* shown | **Passed** |
| **Contact Number Input Mask (Non-Digits)** | Reject alphabetical and special characters in contact field | Only numbers `0-9` accepted in the text box | **Passed** |
| **Contact Number Length (< 11 Digits)** | Reject contact numbers shorter than 11 digits | Submission blocked; *"Contact Information must be exactly 11 digits."* shown | **Passed** |
| **Contact Number Length (> 11 Digits)** | Cap input at maximum of 11 characters | User cannot type more than 11 digits | **Passed** |
| **Double-Booking Prevention** | Prevent booking same physician at same date and time slot | Collision caught; *"Physician already has an appointment..."* shown | **Passed** |
| **View All Appointments** | Display all booked appointments with formatted status pills | All records loaded with color-coded status badges | **Passed** |
| **Search by Patient Name** | Filter table in real-time to match patient name query | Table filtered to matching patient records | **Passed** |
| **Search by Appointment ID** | Locate specific appointment matching ID query | Matching appointment record displayed | **Passed** |
| **Search by Assigned Physician** | Display appointments assigned to specified doctor | Records filtered to selected physician | **Passed** |
| **Modify Appointment (Patient Details)** | Update patient information and save changes to MySQL | Patient details updated in database | **Passed** |
| **Modify Appointment (Conflict Check)** | Block rescheduling if new date/time conflicts with another booking | Conflict detected; reschedule blocked | **Passed** |
| **Cancel Appointment** | Update appointment status from `Scheduled` to `Cancelled` | Status changed to `Cancelled`; marked with red pill | **Passed** |
| **Delete Appointment** | Prompt confirmation and permanently delete record from database | Confirmation dialog shown; record deleted | **Passed** |
| **Daily Report by Date** | Display schedule, patient count, and status breakdown for selected date | Report loaded for the chosen date | **Passed** |
| **Real-Time Arrival Detection** | Trigger arrival alert when an appointment's date and time is reached | Amber arrival badge displayed in topbar | **Passed** |
| **Record Successful Outcome** | Mark arrived appointment as `Completed` with clinical notes | Appointment marked `Completed`; outcome recorded | **Passed** |
| **Record Unsuccessful Outcome** | Mark arrived appointment as `No Show` with reason | Appointment marked `No Show`; notes saved | **Passed** |
| **Snooze Arrival Alert** | Temporarily dismiss arrival prompt for 5 minutes | Alert dismissed; reappeared after 5 minutes | **Passed** |
| **Dashboard KPI Metrics** | Accurately calculate total, today's, completed, and missed bookings | Metric cards displayed correct aggregate counts | **Passed** |
| **Dashboard Donut Chart** | Display status distribution with center total and clean legend | Donut chart rendered with center count and bullet legend | **Passed** |
| **Dashboard Caseload Bar Chart** | Display consultation volume per doctor with integer tick counts | Horizontal bar chart rendered with doctor caseloads | **Passed** |
| **User Sign Out** | Terminate active session and return to login dialog | Main window closed; login dialog displayed | **Passed** |

### 2.3 Detailed Test Case Specifications

#### TC-01: Add Appointment Record
* **Description**: Verify scheduling a new appointment with complete valid parameters.
* **Input Data**:
  * Patient Name: `Maria Santos`
  * Contact Information: `09171234567`
  * Assigned Physician: `Dr. Emily Brown`
  * Appointment Date: `2026-10-15`
  * Appointment Time: `09:30`
* **Expected Result**: Record inserted into MySQL database; unique ID `APT-0001` generated; success message displayed.
* **Actual Result**: Record inserted into MySQL database; unique ID `APT-0001` generated; success message displayed.
* **Status**: **Passed**

#### TC-02: Contact Number Validation (11-Digit Rule)
* **Description**: Verify the contact input field rejects entries that do not match the required 11-digit standard.
* **Input Data**: `091712345` (9 digits)
* **Expected Result**: Submission blocked with validation error: *"Contact Information must be exactly 11 digits."*
* **Actual Result**: Validation error dialog displayed; record was not saved.
* **Status**: **Passed**

#### TC-03: Double-Booking Conflict Prevention
* **Description**: Verify the system detects and rejects an appointment when a physician is already scheduled for that exact time slot.
* **Input Data**:
  * Assigned Physician: `Dr. Emily Brown`
  * Appointment Date: `2026-10-15`
  * Appointment Time: `09:30`
* **Expected Result**: Conflict detected; booking blocked with warning citing the existing appointment ID.
* **Actual Result**: Booking blocked; warning message displayed showing conflict ID.
* **Status**: **Passed**

#### TC-04: Modify Existing Record & Conflict Verification
* **Description**: Verify updating an existing appointment's date and time slot while enforcing collision detection.
* **Input Data**: Select `APT-0001`, update time slot to `10:30`.
* **Expected Result**: Record updated in MySQL and reflected in all table views without triggering false positive conflicts with itself.
* **Actual Result**: Record updated successfully; excluded current ID from collision check; tables refreshed.
* **Status**: **Passed**

#### TC-05: Real-Time Arrival Detection & Outcome Logging
* **Description**: Verify the background timer alerts reception when an appointment time arrives and logs the consultation outcome.
* **Input Data**: Appointment scheduled for current date/time; select *"Completed (Successful)"* with clinical notes.
* **Expected Result**: Amber topbar badge appears; outcome dialog launches; status updates to `Completed` with notes stored.
* **Actual Result**: Badge appeared within 10 seconds; outcome dialog recorded status as `Completed`; database updated.
* **Status**: **Passed**

---

## 3. Problems Encountered and Solutions

### 3.1 Database Connection and Custom Port Misconfigurations
* **Challenge**: 
  Different development and production environments run MySQL on varying configurations (e.g., MariaDB/XAMPP defaults to port `3307`, whereas standalone MySQL defaults to port `3306`). On startup, incorrect port or password settings caused immediate crashes with `mysql.connector.Error: Can't connect to MySQL server`.
* **Solution**: 
  Implemented a resilient connection loop in `main.py` that intercepts database exceptions. If connection fails, it launches `DBSetupDialog`, allowing users to adjust host, port, user, and password via a user-friendly GUI. The validated configuration is automatically saved to `db_config.json`, and database tables are bootstrapped dynamically on reconnection.

### 3.2 Qt Stylesheet Inheritance and Border Leaking
* **Challenge**: 
  When styling card containers with `QFrame { border: 1px solid #E2E8F0; }`, Qt cascaded the border property down to all child `QLabel` elements because `QLabel` inherits from `QFrame`. This produced unwanted rectangular grey border boxes around card titles such as *"APPOINTMENT STATUS DISTRIBUTION"*.
* **Solution**: 
  Scoped the stylesheets using explicit ID selectors:
  ```css
  QFrame#cardBox {
      background-color: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: 10px;
  }
  QFrame#cardBox QLabel {
      border: none;
      background-color: transparent;
  }
  ```
  This effectively eliminated border leakage on interior labels across all screens.

### 3.3 Matplotlib Donut Chart Squeezing & Legend Overlap
* **Challenge**: 
  Inside the Dashboard status card, the default Matplotlib donut chart squeezed percentage labels (`100%`) against the inner ring boundary. Furthermore, default `FigureCanvas` dimensions exceeded the available viewport, causing horizontal scrollbars to appear.
* **Solution**: 
  - Redesigned the chart geometry: removed crowded inside-wedge percentages and implemented a clean center-hole metric displaying total appointments (`ax.text(0, 0.08, str(total))`).
  - Added a right-aligned legend using circular dot markers (`Line2D`) displaying category counts and percentages.
  - Configured `scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)` and assigned `QSizePolicy.Policy.Expanding` to canvas widgets so charts adjust responsively without horizontal scrolling.

### 3.4 Action Button Disappearance on Mouse Hover
* **Challenge**: 
  Hovering over action buttons (such as *"Generate Daily Report"*) caused the button to visually vanish from the screen. This was traced to hex color strings with alpha channel transparency improperly overriding Qt's hover pseudo-states.
* **Solution**: 
  Refactored button styling in `utils/widget_factory.py` to use programmatic color shade calculation (`QColor(colour).darker(112).name()`) applied to explicit `:hover` and `:pressed` selectors with opaque hex strings.

### 3.5 Double-Booking and Data Validation Logic Errors
* **Challenge**: 
  Accidental double-booking of physicians was possible if concurrent appointments were submitted. Furthermore, patient contact numbers were unconstrained, accepting non-numeric characters and arbitrary lengths.
* **Solution**: 
  - Added `find_conflict(physician, date, time)` in `AppointmentController` to reject duplicate reservations.
  - Implemented dual-layer contact validation: restricted UI input to numeric characters with an 11-digit cap (`QRegularExpressionValidator`) and enforced controller verification (`contact.isdigit() and len(contact) == 11`).

---

## 4. Conclusion

### 4.1 What Was Learned
- **Architectural Separation**: Implementing the **Model-View-Controller (MVC)** pattern provided clear boundaries between data manipulation, business logic, and presentation, simplifying testing and future maintenance.
- **Robust Database Integration**: Developed practical experience in connection pooling (`MySQLConnectionPool`), parameterized query security, and dynamic database schema bootstrapping.
- **Advanced Desktop UI/UX**: Mastered PyQt6 layout management, item delegates (`QStyledItemDelegate`) for custom table badges, stylesheet scoping, and background event handling via `QTimer`.
- **Integrated Clinical Analytics**: Learned how to embed Matplotlib visual figures inside Qt GUI widgets to provide actionable management insights.

### 4.2 Skills Developed
- **Object-Oriented Python**: Writing clean, modular, and maintainable software architectures.
- **Defensive Programming**: Enforcing strict input validation, collision detection, and graceful exception handling.
- **Clinical UI Ergonomics**: Implementing the Clean Medical Light design system (Slate 900 navigation, crisp cards, high-contrast typography, and intuitive status pills).
- **Asynchronous Event Tracking**: Managing background polling loops for real-time appointment arrival alerts without blocking the UI thread.

### 4.3 Importance of the Project
In outpatient healthcare facilities, manual scheduling is vulnerable to double-bookings, missed appointments, lost patient records, and uneven doctor workloads. **ClinicMS** solves these operational bottlenecks by:
1. **Guaranteed Scheduling Accuracy**: Automated collision detection protects doctor schedules.
2. **Transparent Clinic Operations**: Staff have instant visibility into daily schedules, patient volumes, and consultation outcomes.
3. **Audit Trail for Patient Adherence**: Logging outcomes (Successful vs. No Show) helps clinics analyze patient attendance patterns.
4. **Local Data Sovereignty**: Self-hosted MySQL storage ensures patient records remain secure and accessible offline.

### 4.4 Recommendations for Future Improvements
1. **Automated Reminders (SMS/Email)**: Integrate SMS (e.g., Twilio) or SMTP email services to send appointment notifications and reminders to patients 24 hours prior to consultations.
2. **Role-Based Access Control (RBAC)**: Expand user roles to distinguish between Receptionists (booking and billing) and Doctors (recording diagnoses and prescriptions).
3. **Electronic Health Records (EHR) Module**: Add patient medical history records, vital signs tracking (blood pressure, heart rate, temperature), and prescription generation.
4. **Cloud / Multi-Branch Database Sync**: Enable secure synchronization between clinic branches through a centralized cloud database.

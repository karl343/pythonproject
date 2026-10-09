from __future__ import annotations

from models.database import get_connection

_CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id       INT          AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role     VARCHAR(50)  NOT NULL DEFAULT 'staff'
)
"""

_CREATE_APPOINTMENTS = """
CREATE TABLE IF NOT EXISTS appointments (
    id           VARCHAR(20)  NOT NULL PRIMARY KEY,
    patient_name VARCHAR(255) NOT NULL,
    contact      VARCHAR(100) NOT NULL,
    physician    VARCHAR(255) NOT NULL,
    date         DATE         NOT NULL,
    time         TIME         NOT NULL,
    status       VARCHAR(50)  NOT NULL DEFAULT 'Scheduled'
)
"""

def bootstrap_schema() -> None:
    conn = get_connection()
    cur  = conn.cursor()
    try:
        cur.execute(_CREATE_USERS)
        cur.execute(_CREATE_APPOINTMENTS)

        cur.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            cur.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                ("admin", "admin123", "admin"),
            )
    finally:
        cur.close()
        conn.close()

class DataManager:

    def find_user(self, username: str) -> dict | None:
        conn = get_connection()
        cur  = conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT id, username, password, role FROM users WHERE username = %s",
                (username,),
            )
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def _next_id(self, cur) -> str:
        cur.execute("SELECT id FROM appointments ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        if row is None:
            return "APT-0001"

        last_num = int(row[0].split("-")[1])
        return f"APT-{last_num + 1:04d}"

    _SELECT = (
        "SELECT id, patient_name, contact, physician, "
        "DATE_FORMAT(date, '%Y-%m-%d') AS date, "
        "TIME_FORMAT(time, '%H:%i')    AS time, "
        "status "
        "FROM appointments "
    )

    def get_all_appointments(self) -> list[dict]:
        conn = get_connection()
        cur  = conn.cursor(dictionary=True)
        try:
            cur.execute(self._SELECT + "ORDER BY date, time")
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()

    def get_appointment_by_id(self, appt_id: str) -> dict | None:
        conn = get_connection()
        cur  = conn.cursor(dictionary=True)
        try:
            cur.execute(self._SELECT + "WHERE id = %s", (appt_id,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def get_appointments_by_date(self, date_str: str) -> list[dict]:
        conn = get_connection()
        cur  = conn.cursor(dictionary=True)
        try:
            cur.execute(self._SELECT + "WHERE date = %s ORDER BY time", (date_str,))
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()

    def find_conflict(
        self,
        physician: str,
        date_str: str,
        time_str: str,
        exclude_id: str | None = None,
    ) -> dict | None:
        conn = get_connection()
        cur  = conn.cursor(dictionary=True)
        try:
            if exclude_id:
                cur.execute(
                    "SELECT id FROM appointments "
                    "WHERE physician = %s AND date = %s AND time = %s "
                    "AND status != 'Cancelled' AND id != %s LIMIT 1",
                    (physician, date_str, time_str, exclude_id),
                )
            else:
                cur.execute(
                    "SELECT id FROM appointments "
                    "WHERE physician = %s AND date = %s AND time = %s "
                    "AND status != 'Cancelled' LIMIT 1",
                    (physician, date_str, time_str),
                )
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def search_appointments(self, query: str) -> list[dict]:
        conn = get_connection()
        cur  = conn.cursor(dictionary=True)
        try:
            like = f"%{query}%"
            cur.execute(
                self._SELECT +
                "WHERE patient_name LIKE %s OR id LIKE %s ORDER BY date, time",
                (like, like),
            )
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()

    def insert_appointment(self, data: dict) -> str:
        conn = get_connection()
        cur  = conn.cursor()
        try:
            new_id = self._next_id(cur)
            cur.execute(
                "INSERT INTO appointments "
                "(id, patient_name, contact, physician, date, time, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    new_id,
                    data["patient_name"],
                    data["contact"],
                    data["physician"],
                    data["date"],
                    data["time"],
                    data.get("status", "Scheduled"),
                ),
            )
            return new_id
        finally:
            cur.close()
            conn.close()

    def update_appointment(self, appt_id: str, data: dict) -> bool:
        conn = get_connection()
        cur  = conn.cursor()
        try:
            cur.execute(
                "UPDATE appointments "
                "SET patient_name=%s, contact=%s, physician=%s, "
                "    date=%s, time=%s, status=%s "
                "WHERE id=%s",
                (
                    data["patient_name"],
                    data["contact"],
                    data["physician"],
                    data["date"],
                    data["time"],
                    data.get("status", "Scheduled"),
                    appt_id,
                ),
            )
            return cur.rowcount > 0
        finally:
            cur.close()
            conn.close()

    def cancel_appointment(self, appt_id: str) -> bool:
        conn = get_connection()
        cur  = conn.cursor()
        try:
            cur.execute(
                "UPDATE appointments SET status='Cancelled' WHERE id=%s",
                (appt_id,),
            )
            return cur.rowcount > 0
        finally:
            cur.close()
            conn.close()

    def delete_appointment(self, appt_id: str) -> bool:
        conn = get_connection()
        cur  = conn.cursor()
        try:
            cur.execute("DELETE FROM appointments WHERE id=%s", (appt_id,))
            return cur.rowcount > 0
        finally:
            cur.close()
            conn.close()

    def update_appointment_status(self, appt_id: str, new_status: str) -> bool:
        conn = get_connection()
        cur  = conn.cursor()
        try:
            cur.execute(
                "UPDATE appointments SET status=%s WHERE id=%s",
                (new_status, appt_id),
            )
            return cur.rowcount > 0
        finally:
            cur.close()
            conn.close()

    def get_due_scheduled_appointments(self) -> list[dict]:
        conn = get_connection()
        cur  = conn.cursor(dictionary=True)
        try:
            cur.execute(
                self._SELECT +
                "WHERE status = 'Scheduled' AND CONCAT(date, ' ', time) <= DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s') "
                "ORDER BY date, time"
            )
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()

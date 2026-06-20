import pymysql
from pymysql.err import MySQLError

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Hacker@152002",  # change if needed
    "database": "student_db",
    "cursorclass": pymysql.cursors.DictCursor,
    "connect_timeout": 5,
}


def get_connection(use_db=True):
    config = DB_CONFIG.copy()
    if not use_db:
        config.pop("database", None)
    return pymysql.connect(**config)


def initialize_database():
    conn = None
    try:
        conn = get_connection(use_db=False)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                age INT NOT NULL,
                grade VARCHAR(10) NOT NULL
            )
            """
        )
        conn.commit()
    except MySQLError as error:
        print(f"❌ Database initialization failed: {error}")
        raise
    finally:
        if conn is not None and conn.open:
            cursor.close()
            conn.close()


def add_student(name, age, grade):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (name, age, grade) VALUES (%s, %s, %s)",
            (name.strip(), age, grade.strip()),
        )
        conn.commit()
        print("✅ Student added successfully!")
    except MySQLError as error:
        print(f"❌ Could not add student: {error}")
    finally:
        if conn is not None and conn.open:
            cursor.close()
            conn.close()


def view_students():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students ORDER BY id")
        rows = cursor.fetchall()
        if not rows:
            print("\nℹ️ No students found.")
            return
        print("\n--- Student Records ---")
        for row in rows:
            print(f"ID: {row['id']}, Name: {row['name']}, Age: {row['age']}, Grade: {row['grade']}")
    except MySQLError as error:
        print(f"❌ Could not retrieve students: {error}")
    finally:
        if conn is not None and conn.open:
            cursor.close()
            conn.close()


def search_students():
    keyword = input("Enter student name or ID to search: ").strip()
    if not keyword:
        print("⚠️ Search keyword cannot be empty.")
        return

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if keyword.isdigit():
            cursor.execute("SELECT * FROM students WHERE id = %s", (int(keyword),))
        else:
            cursor.execute("SELECT * FROM students WHERE name LIKE %s", (f"%{keyword}%",))
        rows = cursor.fetchall()
        if not rows:
            print("\nℹ️ No matching records found.")
            return
        print("\n--- Search Results ---")
        for row in rows:
            print(f"ID: {row['id']}, Name: {row['name']}, Age: {row['age']}, Grade: {row['grade']}")
    except MySQLError as error:
        print(f"❌ Search failed: {error}")
    finally:
        if conn is not None and conn.open:
            cursor.close()
            conn.close()


def update_student(student_id, name=None, age=None, grade=None):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        updates = []
        values = []

        if name:
            updates.append("name = %s")
            values.append(name.strip())
        if age is not None:
            updates.append("age = %s")
            values.append(age)
        if grade:
            updates.append("grade = %s")
            values.append(grade.strip())

        if not updates:
            print("⚠️ No updates provided.")
            return

        values.append(student_id)
        cursor.execute(
            f"UPDATE students SET {', '.join(updates)} WHERE id = %s",
            tuple(values),
        )
        conn.commit()
        if cursor.rowcount:
            print("✅ Student updated successfully!")
        else:
            print("⚠️ Student ID not found.")
    except MySQLError as error:
        print(f"❌ Could not update student: {error}")
    finally:
        if conn is not None and conn.open:
            cursor.close()
            conn.close()


def delete_student(student_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        conn.commit()
        if cursor.rowcount:
            print("🗑 Student deleted successfully!")
        else:
            print("⚠️ Student ID not found.")
    except MySQLError as error:
        print(f"❌ Could not delete student: {error}")
    finally:
        if conn is not None and conn.open:
            cursor.close()
            conn.close()


def input_int(prompt, allow_empty=False):
    while True:
        value = input(prompt).strip()
        if allow_empty and value == "":
            return None
        if value.isdigit():
            return int(value)
        print("❌ Please enter a valid integer.")


def menu():
    initialize_database()

    while True:
        print("\n--- Student Management System ---")
        print("1. Add Student")
        print("2. View Students")
        print("3. Search Students")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            name = input("Enter name: ").strip()
            if not name:
                print("❌ Name cannot be empty.")
                continue
            age = input_int("Enter age: ")
            grade = input("Enter grade: ").strip()
            if not grade:
                print("❌ Grade cannot be empty.")
                continue
            add_student(name, age, grade)

        elif choice == "2":
            view_students()

        elif choice == "3":
            search_students()

        elif choice == "4":
            student_id = input_int("Enter student ID to update: ")
            name = input("Enter new name (leave blank to skip): ").strip() or None
            age = input_int("Enter new age (leave blank to skip): ", allow_empty=True)
            grade = input("Enter new grade (leave blank to skip): ").strip() or None
            update_student(student_id, name, age, grade)

        elif choice == "5":
            student_id = input_int("Enter student ID to delete: ")
            delete_student(student_id)

        elif choice == "6":
            print("👋 Exiting...")
            break

        else:
            print("❌ Invalid choice!")


if __name__ == "__main__":
    menu()

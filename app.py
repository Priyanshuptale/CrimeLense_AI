import webbrowser
import os
from dotenv import load_dotenv
load_dotenv(override=True)


from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from flask import Flask, render_template,request,session, redirect,url_for,send_from_directory

from werkzeug.security import generate_password_hash, check_password_hash

import psycopg2

app = Flask(__name__)
app.secret_key = "crimelens-secret-key-2026"
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


def get_db_connection():
    connection = psycopg2.connect(
        host="localhost",
        database="crimeless-ai",
        user="postgres",
        password="232015",
        port="5432"
    )

    return connection

@app.route("/login", methods=["GET", "POST"])
def login():


    message = None

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT user_id, username, password_hash, role
            FROM users
            WHERE username = %s
        """, (username,))

        user = cursor.fetchone()
       
        cursor.close()
        connection.close()

        print("LOGIN USER:",user)

        if user and check_password_hash(user[2], password):

            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[3]

            return redirect("/")

        else:
            message = "Invalid username or password."

    return render_template(
        "login.html",
        message=message
    )
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
@app.route("/")
def home():

    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()
    cursor = connection.cursor()

    # Total Cases
    cursor.execute("SELECT COUNT(*) FROM cases")
    total_cases = cursor.fetchone()[0]

    # Open Cases
    cursor.execute("""
        SELECT COUNT(*)
        FROM cases
        WHERE status = 'Open'
    """)
    open_cases = cursor.fetchone()[0]

    # Total Evidence
    cursor.execute("SELECT COUNT(*) FROM evidence")
    total_evidence = cursor.fetchone()[0]

    # Total Suspects
    cursor.execute("SELECT COUNT(*) FROM suspects")
    total_suspects = cursor.fetchone()[0]

    # Total Witnesses
    cursor.execute("SELECT COUNT(*) FROM witnesses")
    total_witnesses = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return render_template(
        "index.html",
        total_cases=total_cases,
        open_cases=open_cases,
        total_evidence=total_evidence,
        total_suspects=total_suspects,
        total_witnesses=total_witnesses
    )
@app.route("/cases")
def cases():

    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM cases
        ORDER BY case_id DESC
    """)

    cases = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "cases.html",
        cases=cases
    )

@app.route("/case/<int:case_id>")
def case_details(case_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM cases WHERE case_id = %s",
        (case_id,)
    )

    case = cursor.fetchone()
    print("CASE")

    cursor.close()
    connection.close()

    return render_template("case_details.html", case=case)

@app.route("/add-evidence", methods=["GET", "POST"])
def add_evidence():

    if request.method == "POST":

        case_id = request.form["case_id"]
        evidence_type = request.form["evidence_type"]
        description = request.form["description"]
        collected_date = request.form["collected_date"]
        location = request.form["location"]
        status = request.form["status"]

        # Uploaded file
        evidence_file = request.files.get("evidence_file")

        file_name = None

        if evidence_file and evidence_file.filename:
            file_name = evidence_file.filename
            file_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                file_name
            )
            evidence_file.save(file_path)

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO evidence
            (case_id, evidence_type, description,
             collected_date, location, status, file_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            case_id,
            evidence_type,
            description,
            collected_date,
            location,
            status,
            file_name
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return "Evidence Added Successfully!"

    return render_template("add_evidence.html")
@app.route("/add-suspect", methods=["GET", "POST"])
def add_suspect():

    if request.method == "POST":

        case_id = request.form["case_id"]
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        description = request.form["description"]
        status = request.form["status"]

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO suspects
            (case_id, name, age, gender, description, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            case_id,
            name,
            age,
            gender,
            description,
            status
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return "Suspect Added Successfully!"

    return render_template("add_suspect.html")

@app.route("/add-witness", methods=["GET", "POST"])
def add_witness():

    if request.method == "POST":

        case_id = request.form["case_id"]
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        statement = request.form["statement"]
        contact_info = request.form["contact_info"]
        status = request.form["status"]

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO witnesses
            (case_id, name, age, gender, statement, contact_info, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            case_id,
            name,
            age,
            gender,
            statement,
            contact_info,
            status
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return "Witness Added Successfully!"

    return render_template("add_witness.html")
@app.route("/witnesses")
def witnesses():

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM witnesses
        ORDER BY witness_id DESC
    """)

    witnesses = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("witnesses.html", witnesses=witnesses)

@app.route("/suspects")
def suspects():

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM suspects
        ORDER BY suspect_id DESC
    """)

    suspects = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("suspects.html", suspects=suspects)

@app.route("/ai-analysis", methods=["GET", "POST"])
def ai_analysis():

    analysis = None

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT case_id, case_number, title
        FROM cases
        ORDER BY case_id DESC
    """)
    cases = cursor.fetchall()

    if request.method == "POST":

        case_id = request.form["case_id"]

        cursor.execute("""
            SELECT *
            FROM cases
            WHERE case_id = %s
        """, (case_id,))
        case = cursor.fetchone()

        cursor.execute("""
            SELECT evidence_type, description, collected_date,
                   location, status
            FROM evidence
            WHERE case_id = %s
            ORDER BY evidence_id DESC
        """, (case_id,))
        evidence_records = cursor.fetchall()

        cursor.execute("""
            SELECT name, statement, status
            FROM witnesses
            WHERE case_id = %s
            ORDER BY witness_id DESC
        """, (case_id,))
        witness_records = cursor.fetchall()

        if case:
            analysis = (
                "CRIMELENS AI - INVESTIGATION ASSISTANCE\n\n"
                f"Case Number: {case[1]}\n"
                f"Case Title: {case[2]}\n"
                f"Case Description: {case[3] or 'Not provided'}\n"
                f"Location: {case[4] or 'Not provided'}\n"
                f"Incident Date: {case[5] or 'Not provided'}\n"
                f"Status: {case[6]}\n\n"
                f"Evidence Records: {len(evidence_records)}\n"
            )

            if evidence_records:
                for index, item in enumerate(evidence_records, 1):
                    analysis += (
                        f"\nEvidence {index}:\n"
                        f"Type: {item[0] or 'Not provided'}\n"
                        f"Description: {item[1] or 'Not provided'}\n"
                        f"Date: {item[2] or 'Not provided'}\n"
                        f"Location: {item[3] or 'Not provided'}\n"
                        f"Status: {item[4] or 'Not provided'}\n"
                    )
            else:
                analysis += "\nNo evidence records linked to this case.\n"

            analysis += (
                f"\nWitness Records: {len(witness_records)}\n"
            )

            if witness_records:
                for index, item in enumerate(witness_records, 1):
                    analysis += (
                        f"\nWitness Record {index}:\n"
                        f"Name: {item[0] or 'Not provided'}\n"
                        f"Statement: {item[1] or 'Not provided'}\n"
                        f"Status: {item[2] or 'Not provided'}\n"
                    )
            else:
                analysis += "\nNo witness records linked to this case.\n"
                analysis += (
                "\nAI INVESTIGATION INSIGHTS:\n"
            )

            if not evidence_records:
                analysis += (
                    "- No evidence is currently linked to this case.\n"
                )
            else:
                analysis += (
                    f"- {len(evidence_records)} evidence record(s) "
                    "are available for review.\n"
                )

            if not witness_records:
                analysis += (
                    "- No witness records are currently linked "
                    "to this case.\n"
                )
            else:
                analysis += (
                    f"- {len(witness_records)} witness record(s) "
                    "are available for review.\n"
                )

            analysis += (
                "\nVerification Questions:\n"
                "- Is the evidence source documented?\n"
                "- Are the evidence dates consistent with the case timeline?\n"
                "- Are witness statements supported by available records?\n"
                "- Is any important case information missing?\n"
            )

            analysis += (
                "\nInvestigation Review:\n"
                "- Verify each record against its original source.\n"
                "- Review dates and locations for consistency.\n"
                "- Compare statements with available evidence.\n"
                "- Record missing information for follow-up.\n\n"
                "Note: This tool organizes records for review. "
                "It does not determine guilt or accuse anyone."
            )

    cursor.close()
    connection.close()

    return render_template(
        "ai_analysis.html",
        analysis=analysis,
        cases=cases
    )
@app.route("/evidence")
def evidence():
    if "user_id" not in session:
        return redirect("/login")
    case_id = request.args.get("case_id")
    evidence_type = request.args.get("evidence_type")
    status = request.args.get("status")
    location = request.args.get("location")

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        SELECT *
        FROM evidence
        WHERE 1=1
    """

    values = []

    if case_id:
        query += " AND case_id = %s"
        values.append(case_id)

    if evidence_type:
        query += " AND evidence_type ILIKE %s"
        values.append("%" + evidence_type + "%")

    if status:
        query += " AND status = %s"
        values.append(status)

    if location:
        query += " AND location ILIKE %s"
        values.append("%" + location + "%")

    query += " ORDER BY evidence_id DESC"

    cursor.execute(query, tuple(values))

    evidence = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "evidence.html",
        evidence=evidence
    )
@app.route("/reports")
def reports():

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM cases")
    total_cases = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM evidence")
    total_evidence = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM cases
        WHERE status = 'Open'
    """)
    open_cases = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return render_template(
        "reports.html",
        total_cases=total_cases,
        total_evidence=total_evidence,
        open_cases=open_cases
    )
@app.route("/add-case", methods=["GET", "POST"])
def add_case():

    if request.method == "POST":

        case_number = request.form["case_number"]
        title = request.form["title"]
        description = request.form["description"]
        location = request.form["location"]
        incident_date = request.form["incident_date"]
        status = request.form["status"]

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO cases
            (case_number, title, description, location, incident_date, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            case_number,
            title,
            description,
            location,
            incident_date,
            status
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return "Case Added Successfully!"

    return render_template("add_case.html")

@app.route("/db-test")
def db_test():

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT version();")
        version = cursor.fetchone()

        cursor.close()
        connection.close()

        return f"Database Connected Successfully!<br><br>{version[0]}"

    except Exception as error:
        return f"Database Connection Failed:<br><br>{error}"


if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=False, host="127.0.0.1", port=5000)
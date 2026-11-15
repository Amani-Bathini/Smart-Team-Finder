import os
import bcrypt
import mysql.connector
from database import get_db_connection

from mysql.connector import IntegrityError
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "development-secret-key")


# -----------------------------------
# DATABASE CONNECTION
# -----------------------------------

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


# -----------------------------------
# HOME PAGE
# -----------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------------
# REGISTER
# -----------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        hackerrank_username = request.form.get(
            "hackerrank_username", ""
        ).strip()
        skills = request.form.get("skills", "").strip()
        experience_level = request.form.get(
            "experience_level", ""
        ).strip()
        preferred_role = request.form.get(
            "preferred_role", ""
        ).strip()

        if not all([name, email, password, skills, experience_level]):
            return render_template(
                "register.html",
                message="Please fill in all required fields."
            )

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO developers
                (
                    name,
                    email,
                    password,
                    hackerrank_username,
                    skills,
                    experience_level,
                    preferred_role
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    name,
                    email,
                    hashed_password,
                    hackerrank_username,
                    skills,
                    experience_level,
                    preferred_role
                )
            )

            connection.commit()

            return redirect(url_for("login"))

        except IntegrityError:
            connection.rollback()

            return render_template(
                "register.html",
                message="This email is already registered."
            )

        except Exception as error:
            connection.rollback()

            return render_template(
                "register.html",
                message=f"Registration failed: {error}"
            )

        finally:
            cursor.close()
            connection.close()

    return render_template("register.html")


# -----------------------------------
# LOGIN
# -----------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT *
                FROM developers
                WHERE email = %s
                """,
                (email,)
            )

            developer = cursor.fetchone()

            if developer and bcrypt.checkpw(
                password.encode("utf-8"),
                developer["password"].encode("utf-8")
            ):

                session.clear()

                session["developer_id"] = developer["id"]
                session["developer_name"] = developer["name"]

                return redirect(url_for("dashboard"))

            return render_template(
                "login.html",
                message="Invalid email or password."
            )

        finally:
            cursor.close()
            connection.close()

    return render_template("login.html")


# -----------------------------------
# DASHBOARD
# -----------------------------------

@app.route("/dashboard")
def dashboard():

    if "developer_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT *
            FROM developers
            WHERE id = %s
            """,
            (session["developer_id"],)
        )

        developer = cursor.fetchone()

        if not developer:
            session.clear()
            return redirect(url_for("login"))

        dev_id = session["developer_id"]

        # 1. My Teams Count (Joined or Created)
        cursor.execute(
            """
            SELECT COUNT(DISTINCT team_id) AS count
            FROM team_members
            WHERE developer_id = %s
            """,
            (dev_id,)
        )
        my_teams_row = cursor.fetchone()
        my_teams_count = my_teams_row["count"] if my_teams_row and my_teams_row.get("count") else 0

        # 2. Pending Requests Count (relevant to teams created by this user)
        cursor.execute(
            """
            SELECT COUNT(tr.id) AS count
            FROM team_requests tr
            JOIN teams t ON tr.team_id = t.id
            WHERE t.created_by = %s AND tr.status = 'Pending'
            """,
            (dev_id,)
        )
        pending_row = cursor.fetchone()
        pending_requests_count = pending_row["count"] if pending_row and pending_row.get("count") else 0

        # 3. Available Developers Count (excluding current user)
        cursor.execute(
            """
            SELECT COUNT(id) AS count
            FROM developers
            WHERE id != %s
            """,
            (dev_id,)
        )
        devs_row = cursor.fetchone()
        developers_count = devs_row["count"] if devs_row and devs_row.get("count") else 0

        # 4. Dynamic Recommendations Count (matching teams with available slots)
        developer_skills = {
            skill.strip().lower()
            for skill in (developer.get("skills") or "").split(",")
            if skill.strip()
        }

        recommendations_count = 0
        if developer_skills:
            cursor.execute(
                """
                SELECT t.id, t.required_skills
                FROM teams t
                WHERE t.created_by != %s
                  AND t.id NOT IN (
                      SELECT team_id FROM team_members WHERE developer_id = %s
                  )
                """,
                (dev_id, dev_id)
            )
            candidate_teams = cursor.fetchall()
            for team in candidate_teams:
                req_skills = {
                    s.strip().lower()
                    for s in (team.get("required_skills") or "").split(",")
                    if s.strip()
                }
                if req_skills and developer_skills.intersection(req_skills):
                    recommendations_count += 1

        stats = {
            "my_teams": my_teams_count,
            "pending_requests": pending_requests_count,
            "developers": developers_count,
            "recommendations": recommendations_count
        }

        return render_template(
            "dashboard.html",
            developer=developer,
            stats=stats
        )

    finally:
        cursor.close()
        connection.close()


# -----------------------------------
# MY PROFILE
# -----------------------------------

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "developer_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            hackerrank_username = request.form.get("hackerrank_username", "").strip()
            skills = request.form.get("skills", "").strip()
            experience_level = request.form.get("experience_level", "").strip()
            preferred_role = request.form.get("preferred_role", "").strip()

            if name and skills and experience_level:
                cursor.execute(
                    """
                    UPDATE developers
                    SET name = %s,
                        hackerrank_username = %s,
                        skills = %s,
                        experience_level = %s,
                        preferred_role = %s
                    WHERE id = %s
                    """,
                    (
                        name,
                        hackerrank_username,
                        skills,
                        experience_level,
                        preferred_role,
                        session["developer_id"]
                    )
                )
                connection.commit()
                session["developer_name"] = name
                flash("Profile updated successfully!")

        cursor.execute(
            """
            SELECT *
            FROM developers
            WHERE id = %s
            """,
            (session["developer_id"],)
        )

        developer = cursor.fetchone()

        if not developer:
            session.clear()
            return redirect(url_for("login"))

        return render_template(
            "profile.html",
            developer=developer
        )

    finally:
        cursor.close()
        connection.close()


# -----------------------------------
# LOGOUT
# -----------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# -----------------------------------
# FIND DEVELOPERS
# -----------------------------------

@app.route("/find-developers")
def find_developers():

    if "developer_id" not in session:
        return redirect(url_for("login"))

    skill = request.args.get("skill", "").strip()
    experience = request.args.get("experience", "").strip()
    role = request.args.get("role", "").strip()

    query = """
        SELECT
            id,
            name,
            skills,
            experience_level,
            preferred_role,
            hackerrank_username
        FROM developers
        WHERE id != %s
    """

    values = [session["developer_id"]]

    if skill:
        query += " AND skills LIKE %s"
        values.append(f"%{skill}%")

    if experience:
        query += " AND experience_level = %s"
        values.append(experience)

    if role:
        query += " AND preferred_role LIKE %s"
        values.append(f"%{role}%")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query, tuple(values))

        developers = cursor.fetchall()

        return render_template(
            "find_developers.html",
            developers=developers
        )

    finally:
        cursor.close()
        connection.close()




# -----------------------------------
# CREATE TEAM
# -----------------------------------

@app.route("/create-team", methods=["GET", "POST"])
def create_team():

    if "developer_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        team_name = request.form.get("team_name", "").strip()
        description = request.form.get("description", "").strip()
        required_skills = request.form.get(
            "required_skills", ""
        ).strip()

        try:
            team_size = int(request.form.get("team_size", "0"))
        except ValueError:
            team_size = 0

        if not team_name or not required_skills:
            return render_template(
                "create_team.html",
                message="Please enter the team name and required skills."
            )

        if team_size < 2 or team_size > 20:
            return render_template(
                "create_team.html",
                message="Team size must be between 2 and 20."
            )

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Insert team details
            cursor.execute(
                """
                INSERT INTO teams
                (
                    team_name,
                    description,
                    required_skills,
                    team_size,
                    created_by
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    team_name,
                    description,
                    required_skills,
                    team_size,
                    session["developer_id"]
                )
            )

            team_id = cursor.lastrowid

            # Add the creator as team leader
            cursor.execute(
                """
                INSERT INTO team_members
                (team_id, developer_id, role)
                VALUES (%s, %s, %s)
                """,
                (
                    team_id,
                    session["developer_id"],
                    "Team Leader"
                )
            )

            connection.commit()

            return render_template(
                "create_team.html",
                message="Team created successfully!"
            )

        except Exception as error:
            connection.rollback()

            return render_template(
                "create_team.html",
                message=f"Could not create team: {error}"
            )

        finally:
            cursor.close()
            connection.close()

    return render_template("create_team.html")


# -----------------------------------
# FIND TEAMS
# -----------------------------------

@app.route("/find-teams")
def find_teams():

    if "developer_id" not in session:
        return redirect(url_for("login"))

    team_name = request.args.get("team_name", "").strip()
    skill = request.args.get("skill", "").strip()

    query = """
        SELECT
            t.id,
            t.team_name,
            t.description,
            t.required_skills,
            t.team_size,
            t.created_by,
            d.name AS creator_name,
            COUNT(tm.id) AS current_members
        FROM teams t
        JOIN developers d
            ON t.created_by = d.id
        LEFT JOIN team_members tm
            ON t.id = tm.team_id
        WHERE 1 = 1
    """

    values = []

    if team_name:
        query += " AND t.team_name LIKE %s"
        values.append(f"%{team_name}%")

    if skill:
        query += " AND t.required_skills LIKE %s"
        values.append(f"%{skill}%")

    query += """
        GROUP BY
            t.id,
            t.team_name,
            t.description,
            t.required_skills,
            t.team_size,
            t.created_by,
            d.name
        ORDER BY t.id DESC
    """

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query, tuple(values))

        teams = cursor.fetchall()

        # Get teams the current developer has joined
        cursor.execute(
            """
            SELECT team_id
            FROM team_members
            WHERE developer_id = %s
            """,
            (session["developer_id"],)
        )

        member_team_ids = {
            row["team_id"] for row in cursor.fetchall()
        }

        # Get teams where the current developer has pending join requests
        cursor.execute(
            """
            SELECT team_id
            FROM team_requests
            WHERE developer_id = %s AND status = 'Pending'
            """,
            (session["developer_id"],)
        )

        pending_team_ids = {
            row["team_id"] for row in cursor.fetchall()
        }

        return render_template(
            "find_teams.html",
            teams=teams,
            member_team_ids=member_team_ids,
            pending_team_ids=pending_team_ids,
            message=request.args.get("message")
        )

    finally:
        cursor.close()
        connection.close()




# -----------------------------------
# JOIN TEAM
# -----------------------------------

@app.route("/join-team/<int:team_id>", methods=["POST"])
def join_team(team_id):

    if "developer_id" not in session:
        return redirect(url_for("login"))

    developer_id = session["developer_id"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check whether team exists
        cursor.execute(
            """
            SELECT *
            FROM teams
            WHERE id = %s
            """,
            (team_id,)
        )

        team = cursor.fetchone()

        if not team:
            return redirect(url_for(
                "find_teams",
                message="Team not found."
            ))

        # Check existing membership
        cursor.execute(
            """
            SELECT id
            FROM team_members
            WHERE team_id = %s AND developer_id = %s
            """,
            (team_id, developer_id)
        )

        if cursor.fetchone():
            return redirect(url_for(
                "find_teams",
                message="You are already a member of this team."
            ))

        # Count current team members
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM team_members
            WHERE team_id = %s
            """,
            (team_id,)
        )

        member_count = cursor.fetchone()["total"]

        if member_count >= team["team_size"]:
            return redirect(url_for(
                "find_teams",
                message="Sorry, this team is already full."
            ))

        # Add developer to team
        cursor.execute(
            """
            INSERT INTO team_members
            (team_id, developer_id, role)
            VALUES (%s, %s, %s)
            """,
            (team_id, developer_id, "Member")
        )

        connection.commit()

        return redirect(url_for(
            "find_teams",
            message="Successfully joined the team!"
        ))

    except IntegrityError:
        connection.rollback()

        return redirect(url_for(
            "find_teams",
            message="You are already a member of this team."
        ))

    except Exception as error:
        connection.rollback()

        return redirect(url_for(
            "find_teams",
            message=f"Unable to join team: {error}"
        ))

    finally:
        cursor.close()
        connection.close()




# -----------------------------------
# SMART TEAM RECOMMENDATIONS
# -----------------------------------


@app.route("/recommendations")
def recommendations():

    if "developer_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        developer_id = session["developer_id"]

        # Get logged-in developer's skills
        cursor.execute("""
            SELECT skills
            FROM developers
            WHERE id = %s
        """, (developer_id,))

        developer = cursor.fetchone()

        if not developer:
            session.clear()
            return redirect(url_for("login"))

        developer_skills = {
            skill.strip().lower()
            for skill in (developer["skills"] or "").split(",")
            if skill.strip()
        }

        # Get all teams and their current member count
        cursor.execute("""
            SELECT
                t.id,
                t.team_name,
                t.description,
                t.required_skills,
                t.team_size,
                t.created_by,
                d.name AS creator_name,
                COUNT(DISTINCT tm.id) AS current_members
            FROM teams t
            JOIN developers d
                ON t.created_by = d.id
            LEFT JOIN team_members tm
                ON t.id = tm.team_id
            GROUP BY
                t.id,
                t.team_name,
                t.description,
                t.required_skills,
                t.team_size,
                t.created_by,
                d.name
            ORDER BY t.id DESC
        """)

        teams = cursor.fetchall()

        recommendations_list = []

        for team in teams:

            # Exclude teams created by the logged-in developer
            if team["created_by"] == developer_id:
                continue

            # Exclude already joined teams
            cursor.execute("""
                SELECT id
                FROM team_members
                WHERE team_id = %s AND developer_id = %s
            """, (team["id"], developer_id))

            if cursor.fetchone():
                continue

            required_skills = {
                skill.strip().lower()
                for skill in (team["required_skills"] or "").split(",")
                if skill.strip()
            }

            if not required_skills:
                continue

            matching_skills = developer_skills.intersection(
                required_skills
            )

            missing_skills = required_skills - developer_skills

            percentage = (
                len(matching_skills) / len(required_skills)
            ) * 100

            if matching_skills:

                available_slots = max(
                    0,
                    team["team_size"] - team["current_members"]
                )

                recommendations_list.append({
                    "team": team,
                    "matching_skills": sorted(matching_skills),
                    "missing_skills": sorted(missing_skills),
                    "percentage": round(percentage, 2),
                    "available_slots": available_slots,
                    "status": "Open" if available_slots > 0 else "Full"
                })

        recommendations_list.sort(
            key=lambda item: item["percentage"],
            reverse=True
        )

        return render_template(
            "recommendations.html",
            recommendations=recommendations_list
        )

    finally:
        cursor.close()
        connection.close()




@app.route('/request_to_join/<int:team_id>', methods=['POST'])
def request_to_join(team_id):

    if 'developer_id' not in session:
        return redirect(url_for('login'))

    developer_id = session['developer_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check whether developer is already a team member
        cursor.execute("""
            SELECT id FROM team_members
            WHERE team_id = %s AND developer_id = %s
        """, (team_id, developer_id))

        if cursor.fetchone():
            flash("You are already a member of this team!")
            return redirect(url_for('recommendations'))

        # Check whether request already exists
        cursor.execute("""
            SELECT id FROM team_requests
            WHERE team_id = %s AND developer_id = %s
        """, (team_id, developer_id))

        if cursor.fetchone():
            flash("You have already requested to join this team!")
            return redirect(url_for('recommendations'))

        # Insert join request
        cursor.execute("""
            INSERT INTO team_requests (team_id, developer_id)
            VALUES (%s, %s)
        """, (team_id, developer_id))

        conn.commit()

        flash("Your join request has been sent successfully!")

    except Exception as e:
        conn.rollback()
        print("Join Request Error:", e)
        flash("Unable to send join request.")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('recommendations'))



@app.route('/team_requests')
def team_requests():

    if 'developer_id' not in session:
        return redirect(url_for('login'))

    developer_id = session['developer_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                tr.id AS request_id,
                tr.team_id,
                tr.developer_id,
                tr.status,
                tr.requested_at,
                t.team_name,
                d.name AS developer_name,
                d.email,
                d.skills,
                d.experience_level,
                d.preferred_role

            FROM team_requests tr

            JOIN teams t ON tr.team_id = t.id

            JOIN developers d ON tr.developer_id = d.id

            WHERE t.created_by = %s

            ORDER BY tr.requested_at DESC
        """, (developer_id,))

        join_requests = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        'team_requests.html',
        join_requests=join_requests
    )




@app.route('/accept_request/<int:request_id>', methods=['POST'])
def accept_request(request_id):

    if 'developer_id' not in session:
        return redirect(url_for('login'))

    leader_id = session['developer_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get request and verify team ownership
        cursor.execute("""
            SELECT tr.team_id, tr.developer_id, tr.status,
                   t.team_size
            FROM team_requests tr
            JOIN teams t ON tr.team_id = t.id
            WHERE tr.id = %s AND t.created_by = %s
            FOR UPDATE
        """, (request_id, leader_id))

        result = cursor.fetchone()

        if not result:
            flash("Request not found or unauthorized!")
            return redirect(url_for('team_requests'))

        team_id, developer_id, status, team_size = result

        if status != 'Pending':
            flash("This request has already been processed!")
            return redirect(url_for('team_requests'))

        # Count current team members
        cursor.execute("""
            SELECT COUNT(*)
            FROM team_members
            WHERE team_id = %s
        """, (team_id,))

        current_members = cursor.fetchone()[0]

        # Check team capacity
        if current_members >= team_size:
            flash("Team is full! Cannot accept more members.")
            return redirect(url_for('team_requests'))

        # Add developer to team
        cursor.execute("""
            INSERT INTO team_members
            (team_id, developer_id, role)
            VALUES (%s, %s, 'Member')
        """, (team_id, developer_id))

        # Update request status
        cursor.execute("""
            UPDATE team_requests
            SET status = 'Accepted'
            WHERE id = %s
        """, (request_id,))

        conn.commit()

        flash("Developer accepted successfully!")

    except Exception as e:
        conn.rollback()
        print("Accept Request Error:", e)
        flash("Unable to accept request.")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('team_requests'))



@app.route('/reject_request/<int:request_id>', methods=['POST'])
def reject_request(request_id):

    if 'developer_id' not in session:
        return redirect(url_for('login'))

    leader_id = session['developer_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verify request ownership
        cursor.execute("""
            SELECT tr.id, tr.status
            FROM team_requests tr
            JOIN teams t ON tr.team_id = t.id
            WHERE tr.id = %s AND t.created_by = %s
        """, (request_id, leader_id))

        result = cursor.fetchone()

        if not result:
            flash("Request not found or unauthorized!")
            return redirect(url_for('team_requests'))

        if result[1] != 'Pending':
            flash("This request has already been processed!")
            return redirect(url_for('team_requests'))

        # Update request status
        cursor.execute("""
            UPDATE team_requests
            SET status = 'Rejected'
            WHERE id = %s
        """, (request_id,))

        conn.commit()

        flash("Join request rejected successfully!")

    except Exception as e:
        conn.rollback()
        print("Reject Request Error:", e)
        flash("Unable to reject request.")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('team_requests'))





@app.route('/my_teams')
def my_teams():

    if 'developer_id' not in session:
        return redirect(url_for('login'))

    leader_id = session['developer_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                t.id AS team_id,
                t.team_name,
                t.description,
                t.team_size,
                d.id AS developer_id,
                d.name AS developer_name,
                d.email,
                d.skills,
                tm.role

            FROM teams t

            LEFT JOIN team_members tm
                ON t.id = tm.team_id

            LEFT JOIN developers d
                ON tm.developer_id = d.id

            WHERE t.created_by = %s

            ORDER BY t.id, tm.id
        """, (leader_id,))

        results = cursor.fetchall()

        teams = {}

        for row in results:

            team_id = row['team_id']

            if team_id not in teams:
                teams[team_id] = {
                    'team_id': team_id,
                    'team_name': row['team_name'],
                    'description': row['description'],
                    'team_size': row['team_size'],
                    'members': []
                }

            if row['developer_id'] is not None:
                teams[team_id]['members'].append({
                    'name': row['developer_name'],
                    'email': row['email'],
                    'skills': row['skills'],
                    'role': row['role']
                })

        # Calculate available slots
        for team in teams.values():

            current_members = len(team['members'])

            team['available_slots'] = max(
                0, team['team_size'] - current_members
            )

            team['availability'] = (
                'Full' if team['available_slots'] == 0 else 'Open'
            )

    finally:
        cursor.close()
        conn.close()

    return render_template(
        'team_details.html',
        teams=teams.values()
    )





# -----------------------------------
# RUN APPLICATION
# -----------------------------------

if __name__ == "__main__":
    app.run(debug=True)
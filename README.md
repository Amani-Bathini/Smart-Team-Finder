# Smart Team Finder

A skill-based web application that helps developers find project teams and helps team leaders find developers. Built with **Python Flask** and **MySQL**.

## Features

- Secure registration and login (passwords hashed with **bcrypt**)
- Developer profile: skills, experience level, preferred role, HackerRank username
- Dashboard with counts for my teams, pending requests, developers and recommendations
- Find developers by skill, experience level and role
- Create teams with required skills and team size (2–20); creator becomes **Team Leader**
- Find teams by name or required skill
- **Smart recommendations**: teams ranked by skill-match percentage
- Join request workflow: request → leader **accepts / rejects** (team capacity is checked)
- My Teams page showing members and available slots

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | MySQL (`mysql-connector-python`) |
| Security | bcrypt, Flask sessions |
| Config | python-dotenv |
| Frontend | HTML templates (Jinja2) |

## How Recommendations Work

```
matching_skills = developer_skills ∩ team_required_skills
match % = len(matching_skills) / len(team_required_skills) × 100
```

Teams you created or already joined are excluded, and results are sorted from highest to lowest match.

## Project Structure

```
smart-team-finder/
├── app.py              # Flask app and all routes
├── database.py         # MySQL connection helper
├── requirements.txt    # Dependencies
├── requirements.py     # Optional dependency checker/installer
├── .env                # Local secrets (NOT committed)
├── .gitignore
└── templates/          # HTML pages (login, register, dashboard, etc.)
```

## Database

Database name: `smart_team_finder`. Tables used by the app:

- `developers` (id, name, email, password, hackerrank_username, skills, experience_level, preferred_role)
- `teams` (id, team_name, description, required_skills, team_size, created_by)
- `team_members` (id, team_id, developer_id, role)
- `team_requests` (id, team_id, developer_id, status, requested_at)

> schema.sql

## Setup and Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/<repo-name>.git
   cd <repo-name>
   ```
2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS / Linux
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Create the database** in MySQL and run your schema script:
   ```sql
   CREATE DATABASE smart_team_finder;
   ```
5. **Create a `.env` file** in the project root:
   ```
   DB_HOST=localhost
   DB_USER=your_mysql_user
   DB_PASSWORD=your_mysql_password
   DB_NAME=smart_team_finder
   SECRET_KEY=your_random_secret_key
   ```
6. **Run the app**
   ```bash
   python app.py
   ```
   Open http://127.0.0.1:5000

## Main Routes

| Route | Purpose |
|-------|---------|
| `/register`, `/login`, `/logout` | Authentication |
| `/dashboard`, `/profile` | User home and profile |
| `/find-developers` | Search developers |
| `/create-team`, `/find-teams`, `/my_teams` | Team management |
| `/recommendations` | Skill-matched team suggestions |
| `/request_to_join/<id>`, `/team_requests` | Send and review join requests |
| `/accept_request/<id>`, `/reject_request/<id>` | Leader decisions |

## Future Enhancements

- Email notifications for request updates
- Matching that also considers experience level and role
- In-app team chat
- Admin panel
- HackerRank profile integration

## Author

**Amani Bathini**

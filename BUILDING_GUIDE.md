# Building Guide — Pawfect Pet Grooming

This guide is a step-by-step companion for running, testing, understanding, and deploying the project.

## 1. What the system does
Pawfect is a small pet-grooming reservation system. The public homepage presents the fictional business and services. Customers create accounts and submit reservations. Admins review the reservation list and update appointment statuses. Customers may submit a text review and optional photo to the public gallery.

## 2. Main files
- `app.py`: database models, login/register routes, reservation CRUD, review-photo upload, role checks, and automatic initial database setup.
- `templates/`: HTML pages rendered by Flask/Jinja.
- `static/style.css`: pastel pink and white styling, including responsive layouts.
- `static/uploads/`: uploaded review photos during local development.
- `requirements.txt`: Python libraries used by the app.
- `.env.example`: example environment variables. Copy to `.env` for local customization if needed; never commit `.env`.
- `README.md`: complete operation, submission, and deployment instructions.

## 3. Run the system
Follow **Run locally on Windows (VS Code)** in `README.md`. The short version is: create a virtual environment, install `requirements.txt`, run `python app.py`, then visit `http://127.0.0.1:5000`.

## 4. Test the required features
1. Open the homepage without logging in: services and review area must be visible.
2. Register a new customer and log in.
3. Create a reservation for a pet using a future date and a listed time.
4. Edit the pending reservation and verify the changes appear.
5. Delete the pending reservation; accept the confirmation prompt.
6. Submit a review with an optional test image and verify it appears on the homepage gallery.
7. Log in with the demo admin credentials and confirm the reservation/review appears in the admin dashboard.
8. Edit a reservation as admin and change its status.
9. Log in as a customer and visit `/admin`; the page should return 403 Forbidden.
10. Restart `python app.py` and verify local SQLite data still exists.

## 5. How the database works
SQLAlchemy creates three tables: `User`, `Reservation`, and `Review`. User passwords are hashed using Werkzeug's `generate_password_hash()` and verified with `check_password_hash()`. A reservation links to the customer who made it. Routes check the logged-in account's role and reservation ownership before editing or deleting data.

## 6. Idea claim
Use the class-approved claim format, if this idea is still available:

**Pawfect Pet Grooming — online pet grooming reservations and photo reviews — Reservations**

Check with classmates/instructor before submitting because the class requires each student's business + system concept to be unique.

## 7. GitHub and deployment
Follow **GitHub submission** and **Deploy to Render** in `README.md`. Keep secrets out of GitHub. Use PostgreSQL for hosted reservation data, and plan separate persistent/object storage if you want review photos to survive hosted redeploys.

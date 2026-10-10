# Pawfect Pet Grooming — Online Reservations

**Pawfect Pet Grooming** is a fictional, woman-owned grooming studio concept with a pastel pink, white, and warm-neutral visual theme. Customers can request grooming appointments and share reviews with photos. Staff/admin can review reservations, update appointment statuses, and manage the gallery.

## Business problem
Small grooming studios may receive appointment requests through scattered messages and have no single place for customers to track requests or share photos. Pawfect keeps reservation records, statuses, customer accounts, and photo reviews in one simple web application.

## Features
- Public responsive landing page with business description, service menu, photos, review gallery, and booking call-to-action.
- Customer registration, login, and logout.
- Passwords are hashed with Werkzeug; plain-text passwords are not saved.
- Two roles: `customer` and `admin`.
- Reservation Create, Read, Update, and Delete. Customers may update/delete their own **Pending** reservations; admins can manage any reservation and change status.
- Customers can add a review, rating, and optional JPG/JPEG/PNG/WEBP/GIF photo (up to 5 MB). Their reviews/photos display on the public homepage.
- Customers can delete their own reviews; admins can remove any review.
- Input validation, protected routes, ownership checks, and confirmation before delete actions.
- SQLite database for local development; PostgreSQL supported using `DATABASE_URL` for deployment.
- `/health` health-check endpoint and `/robots.txt`.

## Technology
Python 3.11+, Flask, Flask-SQLAlchemy, SQLite/PostgreSQL, Jinja templates, HTML/CSS, Werkzeug password hashing, Gunicorn for deployment.

## Run locally on Windows (VS Code)
1. Install Python 3.11 or newer from [python.org](https://www.python.org/downloads/). During setup, check **Add Python to PATH**.
2. Extract this ZIP to a folder you can find, such as `Documents\pawfect-pet-grooming`.
3. Open VS Code → **File → Open Folder** → choose the `pawfect-pet-grooming` folder.
4. Open **Terminal → New Terminal**. Make sure the prompt is in the project folder (not inside `templates` or `static`).
5. Create a virtual environment:
   ```powershell
   python -m venv venv
   ```
6. Activate it:
   ```powershell
   venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, you may continue without activating by running `venv\Scripts\python.exe -m pip install -r requirements.txt`, then `venv\Scripts\python.exe app.py`.
7. Install libraries:
   ```powershell
   python -m pip install -r requirements.txt
   ```
8. Start the website:
   ```powershell
   python app.py
   ```
9. Open **http://127.0.0.1:5000** in your browser. Keep the VS Code terminal open while using it. Stop it with **Ctrl+C**.

The local database file `pawfect.db` is created automatically in the project directory, and the two demo accounts are created the first time the app runs.

## Demo accounts
- **Admin:** `admin@pawfect.test` / `PawfectAdmin123!`
- **Customer:** `customer@pawfect.test` / `Pawfect123!`

These are sample credentials for a school demo only. Do not use them for a real business. The application seeds these accounts by default. Set `SEED_DEMO=0` in the deployment environment after you've made any account changes you need. Set a long, random `SECRET_KEY` before public deployment.

## How to operate the site
### As a customer
1. Open the homepage and review the service cards.
2. Click **Book a Groom**. Register using a name, email, and password of at least eight characters, then log in.
3. Select **New Reservation** and fill out pet name, pet type, service, date, available time, and optional notes.
4. Submit the form. The new request appears under **My reservations** with `Pending` status.
5. Use **Edit** to update a pending request, or **Delete** to remove it. Deleting shows a browser confirmation prompt.
6. To add a photo review, scroll to **Share your experience** on the dashboard. Enter the pet's name and review, choose a 1–5 rating, optionally select a photo (JPG/JPEG/PNG/WEBP/GIF, maximum 5 MB), and post it. Your review appears in the public homepage gallery.
7. Use **Log out** in the top navigation.

### As an admin
1. Log in with `admin@pawfect.test` / `PawfectAdmin123!`.
2. The Admin Dashboard lists reservations, review posts, and registered accounts.
3. Choose **Edit / status** on a reservation to update its details or move it through statuses such as `Confirmed`, `In Grooming`, `Ready for Pickup`, or `Completed`.
4. Use **Delete** on a reservation or review when necessary; confirmation is required.
5. Log out when finished.

### Security test for the class demo
1. Log in as a customer.
2. Navigate directly to `http://127.0.0.1:5000/admin`.
3. The system should show a **403 Forbidden** page, because customers do not have the admin role.
4. A customer also cannot view, edit, or delete another customer's reservation by changing its URL.

## GitHub submission
1. Create a new **Public** repository on GitHub named `pawfect-pet-grooming`. Leave the README, `.gitignore`, and license options unchecked because these files are already included locally.
2. Install [Git for Windows](https://git-scm.com/download/win) if `git` is not recognized in the terminal. Restart VS Code after installing it.
3. In the VS Code terminal, from this project folder, run:
   ```powershell
   git init
   git config --global user.name "Your Name"
   git config --global user.email "YOUR_GITHUB_EMAIL"
   git add .
   git commit -m "Build Pawfect Pet Grooming reservation system"
   git branch -M main
   git remote add origin https://github.com/YOUR-GITHUB-USERNAME/pawfect-pet-grooming.git
   git push -u origin main
   ```
4. Replace the name, email, and URL placeholders with your own details. If `origin already exists`, run `git remote -v`; remove the incorrect one with `git remote remove origin`, then add the correct URL.
5. Refresh your GitHub repository. Do **not** upload `venv/`, `.env`, or `pawfect.db`. The included `.gitignore` should keep them out.
6. Submit the repository URL to your instructor; the assignment says to submit the GitHub repository link only.

## Deploy to Render
1. Push the project to GitHub using the instructions above.
2. Sign in to [Render](https://render.com/) and create a new **Web Service** connected to your repository.
3. Use build command `pip install -r requirements.txt` and start command `gunicorn app:app`. The included `render.yaml` also documents these settings.
4. Configure `SECRET_KEY` with a long random value in Render's environment settings. `SEED_DEMO=1` is useful for initial testing; set it to `0` once demo users are no longer wanted.
5. For durable reservation records, create a managed PostgreSQL database and set `DATABASE_URL` on the web service to its connection string. The app uses SQLite automatically on your computer if `DATABASE_URL` is empty.
6. Deploy, then open the public URL Render provides. Test registration, login, creating a reservation, and the admin dashboard.
7. **Photo storage note:** uploads in this starter app are written to `static/uploads`. Some hosts use temporary local filesystems, so photos can disappear on redeploy/restart. For a production system, use persistent disk or object storage for images. The database and image storage are separate concerns.
8. A public hosting URL works as soon as the deploy succeeds. Google search indexing is separate and is not instant or guaranteed; you may submit the public homepage to [Google Search Console](https://search.google.com/search-console/).

## AI disclosure
ChatGPT was used to help generate and explain the initial Flask routes, page templates, style system, and setup/deployment documentation. The student should personally run the app, test the required features, customize details, and be prepared to explain the implementation.

## Requirement checklist
- [x] Public business landing page, services, visuals, CTA, and responsive styling
- [x] Register/login/logout
- [x] Hashed passwords
- [x] Admin/customer roles and protected routes
- [x] Complete reservation CRUD, validation, persistent local database, delete confirmation
- [x] Review section with user-uploaded photos
- [x] README with business problem, features, stack, setup, demo accounts, deployment, and AI disclosure
- [ ] Verify uniqueness with classmates/instructor
- [ ] Test each flow on the computer used for submission
- [ ] Push source to GitHub and submit the repository URL

## Notes
This is a school-project starter, not a fully hardened commercial booking service. It does not automatically check appointment-slot conflicts, send email/SMS confirmations, process payments, or provide production-grade remote image storage. Do not use real customer information before adding these safeguards.

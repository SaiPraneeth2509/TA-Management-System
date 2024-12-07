# TA-Management-System

This is a web-based application designed to manage Teaching Assistant (TA) applications and assignments for Florida Atlantic University's Computer Science Department. The system features role-based dashboards and functionalities tailored for TA Applicants, Department Staff, TA Committee Members, and Instructors.

## Features

- **Role-based Access:**

  - TA Applicants can apply for courses, upload resumes, and track application status.
  - Department Staff can review applications, recommend them to the TA Committee, and notify applicants.
  - TA Committee Members can review recommended applications and assign TAs to courses.
  - Instructors can evaluate TA performance and provide feedback.

- **Application Workflow:**

  - Apply for courses.
  - Review and recommend applications.
  - Notify applicants of their application status.

- **Performance Metrics:**

  - View feedback and evaluations for TAs.
  - Approve or reject TA assignments based on performance.

- **Styling and UI:**
  - Responsive design using Bootstrap.
  - University branding with logo and name prominently displayed.

## Technologies Used

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, Bootstrap
- **Database:** SQLite (can be configured for other databases)
- **Version Control:** Git

## Setup Instructions

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/your-repository-name.git
   ```
2. Navigate to the project directory:
   ```bash
   cd your-repository-name
   ```
3. Install dependencies
4. Apply migrations
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Run the development server:
   ```bash
   python manage.py runserver
   ```
6. Open the app in your browser at http://127.0.0.1:8000

## Usage

Visit the appropriate dashboard based on your role:

- **TA Applicant**
- **Department Staff**
- **TA Committee**
- **Instructor**

Follow the application workflow to manage TA assignments and evaluations.

## Contribution

Contributions are welcome! Please fork this repository and create a pull request for review.

## License

This project is licensed under the MIT License.

## Author

Sai Praneeth Gurrapu

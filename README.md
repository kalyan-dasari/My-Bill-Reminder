# Personal Bill & Reminder Dashboard 🚀

A simple, local-first web application for managing your personal finances, bill payments, and reminders. Built with a Flask backend and SQLite database for easy, secure, and private data management. The frontend is a clean and responsive dashboard created with HTML, CSS, and Bootstrap.

## ✨ Features

- **Recharge Section:** Keep track of mobile or DTH recharges. See remaining days until expiry and receive timely reminders.
- **EMI Section:** Manage loan EMIs with due dates and amounts.
- **Monthly Bills:** Track recurring bills like rent, Netflix, or other subscriptions. Mark them as paid to keep your dashboard clean.
- **Custom Bills:** A flexible section for one-time or irregular bills like water or electricity.
- **Events:** A simple reminder for important dates and events.
- **Dashboard:** A central view showing upcoming bills, a summary of paid vs. upcoming expenses, and color-coded alerts for due bills.
  - **Color Codes:**
    - `🟢 Green`: Paid / On time
    - `🟠 Orange`: Due soon (1-3 days left)
    - `🔴 Red`: Overdue

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Styling:** Bootstrap 5
- **Backend:** Flask (Python)
- **Database:** SQLite3 (local file-based)

## 🚀 How to Run Locally

### Prerequisites

- Python 3.x installed on your system.
- Git (optional, but recommended for cloning the repository).

### Steps

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
    cd bill_reminder
    ```

2.  **Install Dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    
    # Install Flask
    pip install Flask
    ```

3.  **Run the Application:**
    The application will automatically create the `bills.db` SQLite file if it doesn't exist.
    ```bash
    python app.py
    ```

4.  **Access the Dashboard:**
    Open your web browser and navigate to:
    `http://127.0.0.1:5000`

<img width="637" height="405" alt="image" src="https://github.com/user-attachments/assets/0d1f2b4b-c54b-4f19-b569-3fca7b7a4089" />


## 🤝 Contribution

Contributions, issues, and feature requests are welcome. Feel free to check the [issues page](https://github.com/your-username/your-repository-name/issues).

---

This README provides all the necessary information for anyone to understand, run, and potentially contribute to your project. Remember to replace `your-username/your-repository-name` with your actual GitHub details.

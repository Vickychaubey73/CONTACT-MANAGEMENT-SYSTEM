## 📸 Screenshots

### 🖥️ Dashboard
![Dashboard](Screenshot(380).png)

### ➕ Add Contact
![Add Contact](add_contact.png)

### 📊 Stats Window
![Stats](stats.png)




# 🧩 Data Engineer Project – Contact Data Management & ETL Pipeline (Python + AWS + MySQL + Tkinter)

A **Data Engineering mini-project** demonstrating an **end-to-end data pipeline** with a simple user interface.  
The system can **ingest contact data (CSV)**, **transform & clean it using Python (Pandas)**,  
and **load it into both local (SQLite)** and **cloud databases (MySQL / AWS RDS)** —  
along with a fully functional **Tkinter GUI app** to visualize and manage the data interactively.

---

## 🚀 Key Highlights (Why It’s a Data Engineer Project)

- 🔹 **ETL Pipeline:** Python-based extract-transform-load process from CSV → Database  
- 🔹 **Cloud Integration:** Connects with **AWS RDS (MySQL)** for scalable cloud storage  
- 🔹 **Automation Ready:** Modular design can run on AWS Lambda or EC2  
- 🔹 **Analytics:** Basic reporting (gender distribution, total records)  
- 🔹 **Local Testing:** Works offline with SQLite  
- 🔹 **Interactive Dashboard:** Built with Tkinter for local data visualization

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|--------|-------------|----------|
| **Language** | Python | Core development |
| **Libraries** | Pandas, SQLite3, Tkinter, MySQL Connector | ETL, DB operations, GUI |
| **Database** | SQLite (local), MySQL / AWS RDS (cloud) | Data persistence |
| **Cloud Service** | AWS RDS, S3 (optional for backups) | Cloud storage & integration |
| **Deployment** | Local (PyInstaller exe) / Cloud-ready | Portable execution |

---

## 📁 Project Structure

```bash
.
├── index.py / contact_app_ultimate.py   # Main Tkinter GUI Application
├── etl_contacts.py                      # ETL Script (CSV → Clean → DB)
├── contacts_raw.csv                     # Sample raw dataset
├── requirements.txt                     # Project dependencies
├── README.md                            # Documentation
└── screenshots/                         # Optional (UI preview)


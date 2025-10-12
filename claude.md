
 # HotelSmart Project Plan

## Project Information

Project Name: HotelSmart
Objective: Develop a simple CRUD-based hotel and homestay management system to manage rooms, customers, orders, and administrators, with basic automation for operational efficiency.
Target Users: Hotel/homestay administrators and staff for managing operations; customer-facing features (e.g., booking interface) are out of scope for this phase.
Scope: Core CRUD functionality for four entities (Room, Customer, Order, Admin) with relationships, focusing on simplicity and usability for small-scale operations.
Assumptions: Local deployment for development, with potential for cloud hosting. Data privacy follows basic compliance (e.g., secure storage of customer data).

## Technology Stack

### Backend:

Framework: Flask (Python)
Database: SQLite (via SQLAlchemy for ORM)
Libraries: Flask-RESTful (API development), Flask-Login (authentication)

### Frontend:
Framework: React (JavaScript)
Libraries: Axios (API requests), Ant Design or Bootstrap (UI components)
Build Tool: Create React App
Communication: RESTful APIs (JSON over HTTP)
Development Tools: VS Code, Git (version control)
Deployment: Local server (Flask + npm); NOT cloud hosting

## Functional Module Design
The system is divided into four core modules, each corresponding to a key entity with CRUD operations and defined relationships.

### Room Management:
Functionality: Create, read, update, delete rooms (e.g., type, price, status).
Attributes: Room ID, type (e.g., single, double), price, status (available, occupied, cleaning, maintenance), amenities (e.g., Wi-Fi).
Relationships: One room can be linked to multiple orders.
API Endpoints: /rooms (GET, POST), /rooms/<id> (GET, PUT, DELETE).
Frontend: Room list view, add/edit form, status filter.

### Customer Management:
Functionality: Create, read, update, delete customer records.
Attributes: Customer ID, name, contact (phone/email), ID number (optional), booking history.
Relationships: One customer can have multiple orders.
API Endpoints: /customers (GET, POST), /customers/<id> (GET, PUT, DELETE).
Frontend: Customer list, search by name, view booking history.

### Order Management:
Functionality: Create, read, update, delete orders, with basic automation (e.g., availability check).
Attributes: Order ID, customer ID, room ID, check-in/out dates, status (booked, checked-in, canceled, completed), total price.
Relationships: One order links to one customer and one room; one room/customer can link to multiple orders.
API Endpoints: /orders (GET, POST), /orders/<id> (GET, PUT, DELETE).
Frontend: Order form, calendar view for room occupancy, status updates.

### Admin Management:
Functionality: Create, read, update, delete admin accounts, manage authentication.
Attributes: Admin ID, username, password (hashed), role (admin/staff).
Relationships: Optional link to orders (for tracking handled orders).
API Endpoints: /admins (GET, POST), /admins/<id> (GET, PUT, DELETE), /login (POST).
Frontend: Login page, admin dashboard, user management (for super admins).

### Basic Automation:
Price calculation based on room type and duration.
Room availability check during order creation.
Simple dashboard with metrics (e.g., occupancy rate).

## Directory Structure

```sh
HotelSmart/
├── backend/
│   ├── app.py              # Flask main application
│   ├── models/            # SQLAlchemy models
│   │   ├── room.py
│   │   ├── customer.py
│   │   ├── order.py
│   │   └── admin.py
│   ├── routes/            # API routes
│   │   ├── room_routes.py
│   │   ├── customer_routes.py
│   │   ├── order_routes.py
│   │   └── admin_routes.py
│   ├── config.py          # Configuration (e.g., database URI)
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable React components
│   │   │   ├── RoomList.js
│   │   │   ├── CustomerForm.js
│   │   │   ├── OrderCalendar.js
│   │   │   └── AdminLogin.js
│   │   ├── pages/         # Page components
│   │   │   ├── Home.js
│   │   │   ├── Rooms.js
│   │   │   ├── Customers.js
│   │   │   ├── Orders.js
│   │   │   └── Admins.js
│   │   ├── App.js         # Main React app
│   │   ├── index.js       # Entry point
│   │   └── services/      # API call functions
│   │       └── api.js
│   ├── public/            # Static assets
│   ├── package.json       # Node dependencies
│   └── tailwind.config.js # Optional Tailwind CSS config
├── .gitignore             # Git ignore file
└── README.md              # Project documentation
```

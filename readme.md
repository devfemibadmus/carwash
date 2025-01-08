
# Car Wash Simple API Running on Google Cloud Functions

This repository contains the backend for the carwash website: [CarWash Website](https://devfemibadmus.github.io/carwash/).

**Note**: The frontend is based on an existing template that has been modified to test the API functionality. The purpose of this project is to demonstrate backend development using Google Cloud Functions.

CarWash is a simple website designed for small businesses where customers can book orders for car wash services.

Visit the website and book an order: [CarWash](https://devfemibadmus.github.io/carwash/)

----------

### Features:

-   **Secure Authentication**:
    
    -   Integrated **Google Identity Services** for secure authentication. Admin accounts are restricted based on specific Gmail accounts to ensure only authorized users can access sensitive features like CRUD operations on car types and orders.
    -   **Session Authentication** is implemented to ensure only one active session per admin for security purposes, with no multiple concurrent sessions allowed.
-   **RESTful API**:
    -   Developed basic CRUD operations for managing car types and orders:
        -   `POST /cartype`: Create a new car type.
        -   `GET /cartype`: Retrieve all car types.
        -   `PUT /cartype`: Update a car type.
        -   `DELETE /cartype`: Delete a car type.
        -   `POST /order`: Create a new order.
        -   `GET /orders`: Retrieve all orders.
        -   `POST /payment/verify`: Endpoint for verifying payment status.
    - Test cases can be found in the `tests/` folder, and the live API can be accessed at: [https://us-central1-dev-femi-badmus.cloudfunctions.net/carwash](https://us-central1-dev-femi-badmus.cloudfunctions.net/carwash).
-   **Cloud Database (Firestore)**:
    
    -   Integrated **Google Firestore** as the cloud database for storing car types, orders, and user data. This is a NoSQL database that scales automatically with your needs.
-   **Map Integration (Google Maps API)**:
    
    -   Integrated **Google Maps API** to restrict users to specific locations based on their geographic area, ensuring they can view only prices relevant to their region.
-   **Payment Gateway Integration (Stripe)**:
    
    -   Integrated **Stripe** for processing payments. The payment system verifies transactions and updates order statuses.
-   **Role-Based Access Control (RBAC)**:
    
    -   **Admin Role**: Admin users can perform CRUD operations on car types and fetch all orders.
    -   **User Role**: Regular users can place orders but cannot perform administrative tasks.
    -   The backend API is secured with session-based authentication, and admin access is restricted to specific Gmail accounts in production.
-   **Logging and Monitoring**:
    
    -   Implemented **Google Cloud Run Function Monitoring** to ensure backend services are monitored, and logs are collected for better visibility of system health and error tracking.

----------

### Admin Section:

#### Endpoints:

-   **Admin Authentication**:
    -   `POST /admin/google`: Authenticates an admin using Google OAuth 2.0 token.
-   **Session Management**:
    -   `POST /admin/logout`: Logs out the current admin session.
    -   `GET /admin/check`: Checks if an admin is logged in and their session status.

#### Admin Features:

-   **Create Car Type** (`POST /cartype`): Allows the admin to create a new car type.
-   **Get All Car Types** (`GET /cartype`): Allows the admin to retrieve all available car types.
-   **Update Car Type** (`PUT /cartype`): Allows the admin to update an existing car type.
-   **Delete Car Type** (`DELETE /cartype`): Allows the admin to delete a car type.
-   **Get All Orders** (`GET /orders`): Allows the admin to retrieve all orders placed by users.

----------

### Authentication:

1.  **Google Sign-In**: The admin signs in using a Google token, which is verified.
2.  **Session Authentication**: A single session is created upon successful authentication. No multiple sessions are allowed.
3.  **Admin Restriction**: Google Auth is open for testing but in production, it should be restricted to specific admin Gmail accounts only.

----------

### Endpoints:

-   **Admin (CRUD on Car Types)**: Only admins can access and perform CRUD operations on car types.
-   **Order Management**:
    -   `POST /order`: Create an order.
    -   `GET /orders`: Retrieve all orders.
    -   `POST /payment/verify`: Verify payment for an order.

----------

### Security:

-   **Google Authentication**: Restricted to specific admin accounts.
-   **Session-Based Authentication**: One-time session, no multi-session allowed.
-   **Backend Security**: 100% secure with Google Auth and Firebase.

----------

### Benefits:

-   **Frontend Independence**: You can update the frontend anytime without touching the backend.
-   **Cost Efficiency**: The frontend can be hosted on GitHub Pages with a custom domain, and the backend on Google Cloud Functions, ensuring minimal cost due to pay-as-you-go pricing.
-   **Mobile or Web App Compatibility**: The API is RESTful and can be used by your mobile app, another web app, or your frontend/admin page.

----------

### Requirements:

-   **Stripe**: For payment integration.
-   **Google Cloud Functions**: For backend deployment.
-   **Firebase Admin**: For Firestore database management.

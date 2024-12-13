# ZeroStunt Web Service

ZeroStunt Web Service is a web service that allows you to predict the nutritional value of food by uploading images of food. It provides three main features:

- **Food Image Detector**: Analyzes and predicts the nutritional content of food based on the image provided.
- **Stunting Detector**: Analyzes food intake and predicts potential stunting risks based on nutritional content.
- **Food Evaluation and Recommendations**: Evaluates your food choices and offers recommendations for healthier alternatives.

## Authentication

To use the ZeroStunt Web Service, you must authenticate first. The authentication is based on a **username and password**. Follow the steps below to register and log in:

1. **Register**: Create an account using the registration service. 
    - Please **do not spam the registration service** as it can slow down the process and affect performance.

2. **Login**: After registering, log in using your username and password to access the services.

> **Note**: If you have any suggestions for improving security, feel free to contact me.

---

## Base URL

The base URL for the service is:  
`http://localhost:5000/`

---

## Available Services

### Authentication Services

- **POST** `/register`  
  Register a new user with the required details.

- **PUT** `/login`  
  Log in with your credentials to obtain an authentication token.

- **POST** `/verify-token`  
  Verify your token to ensure it is valid.

---

### User Management Services

- **GET** `/user/{uid}`  
  Retrieve user details using the user's unique ID (`uid`).

- **PUT** `/user/{uid}`  
  Update the user data for a specific user identified by their `uid`.

- **DELETE** `/user/{uid}`  
  Delete the user account for a given `uid`.

---

## TESTING
The testing link can be accessed using the following URL:
[Register Endpoint](http://34.128.103.130:9000/register)

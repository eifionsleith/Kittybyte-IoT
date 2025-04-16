# Design
## Auth (/auth)
### POST /auth/register
- Allows the user to create a new account.
- Request Body: Email, Password
- Response: Success message or error
### POST /auth/token
- Authenticates the user based on credentials, and returns a JWT access token
- Request Body: oauth2passwordbearerform
- Response: {"access_token": ..., "token_type": "bearer"} or error
### GET /users/me 
- Description: Retrieves the profile information of the currently authenticated user.
- Request Headers: Authorization: Bearer <token>
- Response: User profile data - user id, email, registration date, etc.
### PUT /users/me
- Description: Allows authenticated user to update their own profile, e.g. password, email, username
- Request Headers: Authorization: Bearer <token>
- Request Body: Fields to update.
- Response: Updated user profile data, or error.

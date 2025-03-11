## Dev Setup
- Configure your .venv `python -m venv .venv && source .venv/bin/activate`
- Install requirements `pip install requirements.txt`
- Configure `.env`
```
# Example Config
JWT_SECRET_TOKEN={Generate using: openssl rand -hex 32}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRY_MINUTES=30
DATABASE_URL=sqlite:///.test.db
DATABASE_ECHO_ALL=False
```
- Run using `fastapi dev src/main.py`
- Access Swagger documentation at `localhost:8000/docs`

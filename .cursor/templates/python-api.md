# Python API Template

## Project Structure
```
python-api/
├── app/
│   ├── api/
│   ├── models/
│   ├── services/
│   ├── utils/
│   └── main.py
├── tests/
├── docs/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Technology Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Authentication**: JWT
- **Testing**: pytest
- **Documentation**: OpenAPI/Swagger
- **Deployment**: Docker

## Key Features
- RESTful API design
- Automatic API documentation
- Database migrations
- Authentication & authorization
- Input validation
- Error handling
- Rate limiting

## Getting Started
1. Clone template
2. Install dependencies: `pip install -r requirements.txt`
3. Setup database
4. Run migrations
5. Start server: `uvicorn app.main:app --reload`
6. Run tests: `pytest`

## Cursor Rules Applied
- Python development rules
- API design rules
- Testing rules
- Security rules
- Documentation rules
- DevOps rules

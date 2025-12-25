 # SQLModel Database Modeling Skill

  ## Purpose
  Expertise in creating SQLModel models with proper type hints, relationships, indexes, and database connections.

  ## Context
  Used for defining database models that combine SQLAlchemy ORM with Pydantic validation.

  ## Pattern
  ```python
  from sqlmodel import SQLModel, Field, Relationship, create_engine, Session
  from typing import Optional, List
  from datetime import datetime
  import uuid

  # Model definition with type hints
  class User(SQLModel, table=True):
      __tablename__ = "users"

      id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
      username: str = Field(max_length=50, unique=True, index=True)
      email: str = Field(max_length=100, unique=True, index=True)
      password_hash: str = Field(max_length=255)
      created_at: datetime = Field(default_factory=datetime.utcnow)
      updated_at: datetime = Field(default_factory=datetime.utcnow)

      # Relationship
      tasks: List["Task"] = Relationship(back_populates="user")

  # Database connection
  engine = create_engine(os.getenv("DATABASE_URL"), echo=True)

  def get_session():
      with Session(engine) as session:
          yield session

  Best Practices

  - Use UUID for primary keys
  - Add indexes on foreign keys and frequently queried columns
  - Use Field() for constraints (max_length, unique, default)
  - Define relationships with Relationship()
  - Use type hints for all fields
  - Create migration scripts with SQLModel.metadata.create_all()

  Validation

  - All models have tablename defined
  - All fields have type hints
  - Foreign keys use proper references
  - Indexes created for performance
  - Test database connection

  
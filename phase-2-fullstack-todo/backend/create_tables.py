"""Create database tables for ChatKit models."""

from sqlmodel import SQLModel

from db import engine

# Create all tables
SQLModel.metadata.create_all(engine)
print(
    "Successfully created all ChatKit tables: chatkit_sessions, chat_threads, chat_messages, client_effects, chat_tools"
)

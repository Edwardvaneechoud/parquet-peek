# Parquet Peek Vue Backend

A FastAPI backend service that provides paginated access to Parquet files. Part of the Parquet Peek Vue tutorial project demonstrating how to build a Parquet file viewer using Vue.js and Python.

## Features

- FastAPI-based REST API
- Polars for efficient Parquet file handling
- Lazy loading for large files
- Pagination support
- Data type inference
- CORS configured for Vue.js development

## Quick Start

```bash
# Install dependencies
poetry install

# Run the backend server
poetry run backend
```

The server will start on `http://localhost:8000`.

## API Endpoints

- `GET /` - Health check endpoint
- `GET /api/parquet` - Get paginated Parquet data
  - Query parameters:
    - `file_path`: Path to the Parquet file
    - `page`: Page number (default: 1)
    - `page_size`: Records per page (default: 100)
- `GET /api/parquet_length` - Get total record count
  - Query parameters:
    - `file_path`: Path to the Parquet file

## Development

This backend is built with:
- FastAPI for the web framework
- Polars for Parquet file handling
- Poetry for dependency management
- Pydantic for data validation

## Project Structure

```
backend/
├── parquet_peek_vue/
│   ├── __init__.py
│   └── main.py
├── pyproject.toml
└── README.md
```
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import polars as pl
import uvicorn
from pathlib import Path


# Create FastAPI app
app = FastAPI()

# Set the base data directory
DATA_DIR = Path(__file__).parent.parent / "data"

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Data Loading and Processing ---
def load_parquet_file(file_path: str) -> pl.LazyFrame:
    """Loads a parquet file and returns a Polars LazyFrame."""

    # Sanitize the filename to prevent path traversal
    file_path = Path(file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File {file_path} not found")
    try:
        return pl.scan_parquet(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_data_type(df: pl.LazyFrame) -> Dict[str, str]:
    """Determines and returns the data type of each column in a Polars LazyFrame."""
    schema = {}
    pl_schema = df.collect_schema()
    for col in pl_schema.names():
        dtype_val = pl_schema[col]

        if isinstance(dtype_val, pl.String):
            schema[col] = "string"
        elif dtype_val.is_numeric():
            schema[col] = "number"
        elif isinstance(dtype_val, pl.Boolean):
            schema[col] = "boolean"
        elif isinstance(dtype_val, pl.Date) or isinstance(dtype_val, pl.Datetime):
            schema[col] = "timestamp"
        else:
            schema[col] = "other"
    return schema


def paginate_data(df: pl.LazyFrame, page: int, page_size: int) -> pl.DataFrame:
    """Paginates a Polars LazyFrame based on page and page_size."""
    return df.sort(by="id").slice((page - 1) * page_size, page_size).collect()


def get_total_records(df: pl.LazyFrame) -> int:
    """Retrieves the total records in a lazy data frame."""
    return df.select(pl.len()).collect().item(0, 0)


class ParquetResponse(BaseModel):
    data: List[Dict[str, Any]]
    schema_value: Dict[str, str]


@app.get("/")
async def root():
    """Test endpoint to verify server is running"""
    return {"message": "Parquet viewer backend is running"}


@app.get("/api/parquet", response_model=ParquetResponse)
async def read_parquet(file_path: str, page: int = 1, page_size: int = 100):
    """Read a parquet file with pagination"""
    try:
        df = load_parquet_file(file_path)
        schema_value = get_data_type(df)
        result = paginate_data(df, page, page_size)

        return ParquetResponse(
            data=result.to_dicts(),
            schema_value=schema_value
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/parquet_length", response_model=int)
async def read_parquet_length(file_path: str) -> int:
    """Read a parquet file length"""
    try:
        df = load_parquet_file(file_path)
        return get_total_records(df)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Entry point for the FastAPI application."""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()

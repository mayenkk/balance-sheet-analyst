# This file is a stub for Vercel Python serverless deployment.
# For Vercel, place your FastAPI app in backend/app/main.py and use a vercel.json config at the project root.
# See README for Vercel deployment instructions.

# Example: To run locally, use:
# uvicorn app.main:app --reload

import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 
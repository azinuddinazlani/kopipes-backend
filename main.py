from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.db_connection import init_table
from routers import user, skill_assess, employer, seed, job_listing  # Remove product_router as it doesn't exist
import uvicorn

init_table()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

#router
app.include_router(user.router, prefix="/users", tags=["users"])
# Remove product_router as it doesn't exist
# app.include_router(skill_assess.router, prefix="/skill-assess", tags=["skill-assess"])
app.include_router(employer.router, prefix="/employer", tags=["employer"])
app.include_router(job_listing.router, prefix="/jobs", tags=["jobs"])
app.include_router(seed.router, prefix="/seed", tags=["seed"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
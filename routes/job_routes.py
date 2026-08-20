from datetime import datetime
from typing import List
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from database import jobs_collection
from fastapi import APIRouter, Depends, HTTPException, status
from models import JobCreate, JobResponse, JobStatus, JobUpdate
from security import get_current_user

router = APIRouter(prefix="/api/jobs", tags=["Jobs Management"])


def validate_object_id(id_str: str) -> ObjectId:
  if not ObjectId.is_valid(id_str):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid Job ID format",
    )
  return ObjectId(id_str)


# 1. Create Job
@router.post(
    "/", response_model=JobResponse, status_code=status.HTTP_201_CREATED
)
async def create_job(
    job: JobCreate, current_user: dict = Depends(get_current_user)
):
  job_data = job.model_dump()
  job_data["user_id"] = str(current_user["_id"])
  job_data["created_at"] = datetime.utcnow()
  job_data["application_date"] = job_data.get("application_date") or job_data["created_at"]

  try:
    result = await jobs_collection.insert_one(job_data)
  except DuplicateKeyError:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="This job is already saved in your applications",
    )
  created_job = await jobs_collection.find_one({"_id": result.inserted_id})

  return {
      "id": str(created_job["_id"]),
      "user_id": created_job["user_id"],
      "title": created_job.get("title", ""),
      "company": created_job.get("company", ""),
      "location": created_job.get("location"),
      "status": created_job.get("status", "Applied"),
      "notes": created_job.get("notes"),
      "job_url": created_job.get("job_url"),
      "source": created_job.get("source"),
      "salary": created_job.get("salary"),
      "experience_level": created_job.get("experience_level"),
      "work_type": created_job.get("work_type"),
      "resume_version": created_job.get("resume_version"),
      "follow_up_date": created_job.get("follow_up_date"),
      "application_date": created_job.get("application_date"),
      "response_date": created_job.get("response_date"),
      "created_at": created_job.get("created_at"),
  }


# 2. Get All Jobs for Current User
@router.get("/", response_model=List[JobResponse])
async def get_user_jobs(current_user: dict = Depends(get_current_user)):
  user_id = str(current_user["_id"])
  cursor = jobs_collection.find({"user_id": user_id})

  jobs = []
  async for job in cursor:
    jobs.append({
        "id": str(job["_id"]),
        "user_id": job["user_id"],
        "title": job.get("title", ""),
        "company": job.get("company", ""),
        "location": job.get("location"),
        "status": job.get("status", "Applied"),
        "notes": job.get("notes"),
        "job_url": job.get("job_url"),
        "source": job.get("source"),
        "salary": job.get("salary"),
        "experience_level": job.get("experience_level"),
        "work_type": job.get("work_type"),
        "resume_version": job.get("resume_version"),
        "follow_up_date": job.get("follow_up_date"),
        "application_date": job.get("application_date"),
        "response_date": job.get("response_date"),
        "created_at": job.get("created_at"),
    })
  return jobs


# 3. Update Job by ID (PATCH)
@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    job: JobUpdate,
    current_user: dict = Depends(get_current_user),
):
  obj_id = validate_object_id(job_id)
  user_id = str(current_user["_id"])

  current_job = await jobs_collection.find_one({"_id": obj_id, "user_id": user_id})
  if not current_job:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Job not found or unauthorized",
    )

  update_data = {k: v for k, v in job.model_dump().items() if v is not None}
  if job.status in {JobStatus.INTERVIEW, JobStatus.OFFER, JobStatus.REJECTED} and not current_job.get("response_date"):
    update_data["response_date"] = datetime.utcnow()
  if not update_data:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
    )

  result = await jobs_collection.find_one_and_update(
      {"_id": obj_id, "user_id": user_id},
      {"$set": update_data},
      return_document=True,
  )

  if not result:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Job not found or unauthorized",
    )

  return {
      "id": str(result["_id"]),
      "user_id": result["user_id"],
      "title": result.get("title", ""),
      "company": result.get("company", ""),
      "location": result.get("location"),
      "status": result.get("status", "Applied"),
      "notes": result.get("notes"),
      "job_url": result.get("job_url"),
      "source": result.get("source"),
      "salary": result.get("salary"),
      "experience_level": result.get("experience_level"),
      "work_type": result.get("work_type"),
      "resume_version": result.get("resume_version"),
      "follow_up_date": result.get("follow_up_date"),
      "application_date": result.get("application_date"),
      "response_date": result.get("response_date"),
      "created_at": result.get("created_at"),
  }


# 4. Delete Job by ID
@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: str, current_user: dict = Depends(get_current_user)
):
  obj_id = validate_object_id(job_id)
  user_id = str(current_user["_id"])

  result = await jobs_collection.delete_one(
      {"_id": obj_id, "user_id": user_id}
  )

  if result.deleted_count == 0:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Job not found or unauthorized",
    )
  return None
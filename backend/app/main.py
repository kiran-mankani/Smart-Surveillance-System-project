import sys
from datetime import datetime, timedelta
from app.database import predictions_collection
from pathlib import Path
import tempfile

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

from ml_model.inference.predict_video import predict as predict_video


import os
import random
import shutil

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Header
)

from fastapi.middleware.cors import CORSMiddleware

from app.database import users_collection, predictions_collection
from app.email_utils import send_otp_email

from app.models import (
    User,
    LoginUser,
    VerifyOTP,
    ForgotPassword,
    VerifyResetOTP,
    ResetPassword
)

from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)

from ml_model.inference.predict_video import (
    predict as predict_video
)

app = FastAPI()

# UPLOAD_FOLDER = "uploads"
UPLOAD_FOLDER = Path(tempfile.gettempdir()) / "surveillance-uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)










app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def home():

    return {
        "message": "Smart Surveillance API is running"
    }










@app.post("/register")
def register(user: User):

    existing_user = users_collection.find_one(
        {
            "email": user.email
        }
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    user_dict = user.dict()

    user_dict["password"] = hash_password(
        user.password
    )

    otp = str(random.randint(100000, 999999))

    user_dict["verification_otp"] = otp
    user_dict["is_verified"] = False

    users_collection.insert_one(user_dict)

    print("Generated OTP:", otp)

    email_sent = send_otp_email(
        user.email,
        otp
    )

    if not email_sent:
        raise HTTPException(
            status_code=500,
            detail="Failed to send OTP email"
        )

    return {
        "success": True,
        "message": "Registration successful. Check your email for OTP."
    }




@app.post("/verify-email")
def verify_email(data: VerifyOTP):

    user = users_collection.find_one(
        {
            "email": data.email
        }
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    received_otp = str(data.otp).strip()
    database_otp = str(
        user.get("verification_otp", "")
    ).strip()

    print("Received OTP:", received_otp)
    print("Database OTP:", database_otp)

    if received_otp != database_otp:

        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    users_collection.update_one(

        {
            "email": data.email
        },

        {
            "$set": {
                "is_verified": True,
                "verification_otp": None
            }
        }

    )

    return {
        "success": True,
        "message": "Email verified successfully"
    }















@app.post("/login")
def login(user: LoginUser):

    db_user = users_collection.find_one(
        {
            "email": user.email
        }
    )

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not db_user.get("is_verified", False):
        raise HTTPException(
            status_code=400,
            detail="Please verify your email first."
        )

    if not verify_password(
        user.password,
        db_user["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    token = create_access_token(
        {
            "sub": user.email
        }
    )

    return {
        "success": True,
        "message": "Login Successful",
        "access_token": token,
        "token_type": "bearer"
    }
# ============================================================
# PROFILE
# ============================================================

@app.get("/profile")
async def get_profile(
    authorization: str = Header(None)
):

    # --------------------------------------------------------
    # 1. CHECK AUTHORIZATION
    # --------------------------------------------------------

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization token is required"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format"
        )

    token = authorization.split(" ", 1)[1]


    # --------------------------------------------------------
    # 2. VERIFY TOKEN
    # --------------------------------------------------------

    try:

        payload = verify_token(token)

        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )

        user_email = (
            payload.get("sub")
            or payload.get("email")
            or payload.get("user")
        )

        if not user_email:
            raise HTTPException(
                status_code=401,
                detail="User information not found in token"
            )

    except HTTPException:
        raise

    except Exception as e:

        print("Profile token error:", e)

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


    # --------------------------------------------------------
    # 3. FIND USER IN MONGODB
    # --------------------------------------------------------

    db_user = users_collection.find_one(
        {
            "email": user_email
        }
    )


    if not db_user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )


    # --------------------------------------------------------
    # 4. RETURN USER PROFILE
    # --------------------------------------------------------

    return {

        "success": True,

        "user": {

            "name": db_user.get(
                "name",
                ""
            ),

            "email": db_user.get(
                "email",
                user_email
            ),

            "is_verified": db_user.get(
                "is_verified",
                False
            ),

            "is_active": db_user.get(
                "is_active",
                True
            ),

            "role": db_user.get(
                "role",
                "User"
            )
        }
    }
@app.post("/forgot-password")
def forgot_password(data: ForgotPassword):

    user = users_collection.find_one(
        {
            "email": data.email
        }
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    otp = str(random.randint(100000, 999999))

    users_collection.update_one(
        {
            "email": data.email
        },
        {
            "$set": {
                "reset_otp": otp
            }
        }
    )

    send_otp_email(
        data.email,
        otp
    )

    return {
        "success": True,
        "message": "Reset OTP sent successfully"
    }






















@app.post("/verify-reset-otp")
def verify_reset_otp(data: VerifyResetOTP):

    user = users_collection.find_one(
        {
            "email": data.email
        }
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if str(user.get("reset_otp")).strip() != str(data.otp).strip():

        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    return {
        "success": True,
        "message": "OTP verified successfully"
    }



















@app.post("/set-new-password")
def set_new_password(data: ResetPassword):

    user = users_collection.find_one(
        {
            "email": data.email
        }
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    users_collection.update_one(

        {
            "email": data.email
        },

        {
            "$set": {
                "password": hash_password(data.new_password),
                "reset_otp": None
            }
        }

    )

    return {
        "success": True,
        "message": "Password updated successfully"
    }




















@app.post("/resend-otp")
def resend_otp(data: ForgotPassword):

    user = users_collection.find_one(
        {
            "email": data.email
        }
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    otp = str(random.randint(100000, 999999))

    users_collection.update_one(
        {
            "email": data.email
        },
        {
            "$set": {
                "verification_otp": otp
            }
        }
    )

    email_sent = send_otp_email(
        data.email,
        otp
    )

    if not email_sent:
        raise HTTPException(
            status_code=500,
            detail="Failed to send OTP"
        )

    return {
        "success": True,
        "message": "New OTP sent successfully"
    }







# ============================================================
# VIDEO PREDICTION
# ============================================================

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    authorization: str = Header(None)
):

    # -----------------------------
    # 1. Check JWT
    # -----------------------------

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization token is required"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format"
        )

    token = authorization.split(" ", 1)[1]

    try:

        payload = verify_token(token)

        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )

        user_email = (
            payload.get("sub")
            or payload.get("email")
            or payload.get("user")
        )

    except HTTPException:
        raise

    except Exception as e:

        print("Token verification error:", e)

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


    # -----------------------------
    # 2. Check file
    # -----------------------------

    if not file:
        raise HTTPException(
            status_code=400,
            detail="No video file uploaded"
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid file name"
        )


    # -----------------------------
    # 3. Check extension
    # -----------------------------

    allowed_extensions = {
        ".mp4",
        ".avi",
        ".mov",
        ".mkv",
        ".wmv"
    }

    file_extension = Path(
        file.filename
    ).suffix.lower()

    if file_extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail="Unsupported video format"
        )


    # -----------------------------
    # 4. Save temporary video
    # -----------------------------

    safe_filename = os.path.basename(
        file.filename
    )

    file_path = Path(
        UPLOAD_FOLDER
    ) / safe_filename


    try:

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )


        # -----------------------------
        # 5. AI Prediction
        # -----------------------------

        predicted_class, confidence = predict_video(
            str(file_path)
        )


        # -----------------------------
        # 6. Convert confidence
        # -----------------------------

        try:

            confidence = float(
                confidence
            )

        except (ValueError, TypeError):

            confidence = None


        # -----------------------------
        # 7. Save to MongoDB
        # -----------------------------

        prediction_document = {

            "user_email": user_email,

            "video_name": file.filename,

            "uploaded_file": safe_filename,

            "predicted_class": predicted_class,

            "confidence": confidence,

            "prediction_time": datetime.now(),

            "status": "success"

        }


        try:

            predictions_collection.insert_one(
                prediction_document
            )

            print(
                "Prediction saved to MongoDB"
            )

        except Exception as db_error:

            print(
                "MongoDB prediction save error:",
                db_error
            )


        # -----------------------------
        # 8. Return result
        # -----------------------------

        return {

            "success": True,

            "message":
                "Prediction completed successfully",

            "video":
                file.filename,

            "predicted_class":
                predicted_class,

            "confidence":
                confidence

        }


    except HTTPException:

        raise


    except Exception as e:

        print(
            "Prediction Error:",
            e
        )


        # Save failed prediction

        try:

            predictions_collection.insert_one({

                "user_email":
                    user_email,

                "video_name":
                    file.filename,

                "uploaded_file":
                    safe_filename,

                "predicted_class":
                    None,

                "confidence":
                    None,

                "prediction_time":
                    datetime.now(),

                "status":
                    "failed",

                "error":
                    str(e)

            })

        except Exception as db_error:

            print(
                "MongoDB error while saving failed prediction:",
                db_error
            )


        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


    finally:

        # Delete temporary video

        try:

            if file_path.exists():

                file_path.unlink()

                print(
                    "Temporary video deleted:",
                    file_path
                )

        except Exception as delete_error:

            print(
                "Could not delete temporary video:",
                delete_error
            )

# ============================================================
# DASHBOARD STATS
# ============================================================

# ============================================================
# DASHBOARD STATS
# ============================================================

@app.get("/dashboard-stats")
async def dashboard_stats(
    authorization: str = Header(None)
):

    # --------------------------------------------------------
    # 1. CHECK JWT TOKEN
    # --------------------------------------------------------

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization token is required"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format"
        )

    token = authorization.split(" ", 1)[1]

    try:

        payload = verify_token(token)

        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )

        user_email = (
            payload.get("sub")
            or payload.get("email")
            or payload.get("user")
        )

    except Exception as e:

        print("Dashboard token error:", e)

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


    # --------------------------------------------------------
    # 2. USER FILTER
    # --------------------------------------------------------

    user_filter = {
        "user_email": user_email
    }


    try:

        # ----------------------------------------------------
        # TOTAL VIDEOS
        # ----------------------------------------------------

        total_videos = predictions_collection.count_documents(
            user_filter
        )


        # ----------------------------------------------------
        # TOTAL SUCCESSFUL PREDICTIONS
        # ----------------------------------------------------

        total_predictions = predictions_collection.count_documents({
            "user_email": user_email,
            "status": "success"
        })


        # ----------------------------------------------------
        # FAILED PREDICTIONS
        # ----------------------------------------------------

        failed_predictions = predictions_collection.count_documents({
            "user_email": user_email,
            "status": "failed"
        })


        # ----------------------------------------------------
        # TODAY'S UPLOADS
        # ----------------------------------------------------

        today = datetime.now().date()

        start_of_day = datetime.combine(
            today,
            datetime.min.time()
        )

        end_of_day = start_of_day + timedelta(days=1)

        today_uploads = predictions_collection.count_documents({
            "user_email": user_email,
            "prediction_time": {
                "$gte": start_of_day,
                "$lt": end_of_day
            }
        })


        # ----------------------------------------------------
        # AVERAGE CONFIDENCE
        # ----------------------------------------------------

        confidence_docs = list(
            predictions_collection.find(
                {
                    "user_email": user_email,
                    "status": "success",
                    "confidence": {
                        "$exists": True
                    }
                },
                {
                    "_id": 0,
                    "confidence": 1
                }
            )
        )


        if confidence_docs:

            values = []

            for doc in confidence_docs:

                try:

                    value = float(
                        doc.get("confidence")
                    )

                    if value <= 1:
                        value = value * 100

                    values.append(value)

                except Exception:
                    pass


            if values:

                accuracy = round(
                    sum(values) / len(values),
                    2
                )

            else:

                accuracy = None

        else:

            accuracy = None


        # ----------------------------------------------------
        # LATEST PREDICTIONS
        # ----------------------------------------------------

        latest_predictions = list(
            predictions_collection.find(
                user_filter,
                {
                    "_id": 0,
                    "video_name": 1,
                    "predicted_class": 1,
                    "confidence": 1,
                    "prediction_time": 1,
                    "status": 1
                }
            )
            .sort(
                "prediction_time",
                -1
            )
            .limit(10)
        )


        # ----------------------------------------------------
        # CONVERT DATETIME TO JSON
        # ----------------------------------------------------

        for prediction in latest_predictions:

            if prediction.get("prediction_time"):

                prediction["prediction_time"] = (
                    prediction["prediction_time"].isoformat()
                )


        # ----------------------------------------------------
        # RETURN DASHBOARD DATA
        # ----------------------------------------------------

        return {

            "success": True,

            "total_videos": total_videos,

            "total_predictions": total_predictions,

            "failed_predictions": failed_predictions,

            "accuracy": accuracy,

            "today_uploads": today_uploads,

            "latest_predictions": latest_predictions
        }


    except Exception as e:

        print(
            "Dashboard stats error:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to load dashboard statistics"
        )

    # ============================================================
# PREDICTION HISTORY
# ============================================================

@app.get("/prediction-history")
async def prediction_history(
    authorization: str = Header(None)
):

    # --------------------------------------------------------
    # 1. CHECK JWT TOKEN
    # --------------------------------------------------------

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization token is required"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format"
        )

    token = authorization.split(" ", 1)[1]


    # --------------------------------------------------------
    # 2. VERIFY TOKEN
    # --------------------------------------------------------

    try:

        payload = verify_token(token)

        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )

        user_email = (
            payload.get("sub")
            or payload.get("email")
            or payload.get("user")
        )

        if not user_email:
            raise HTTPException(
                status_code=401,
                detail="User information not found"
            )

    except HTTPException:
        raise

    except Exception as e:

        print(
            "History token error:",
            e
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


    # --------------------------------------------------------
    # 3. GET USER'S PREDICTION HISTORY
    # --------------------------------------------------------

    try:

        history = list(
            predictions_collection.find(
                {
                    "user_email": user_email
                },
                {
                    "_id": 0,
                    "video_name": 1,
                    "predicted_class": 1,
                    "confidence": 1,
                    "prediction_time": 1,
                    "status": 1
                }
            ).sort(
                "prediction_time",
                -1
            )
        )


        # ----------------------------------------------------
        # 4. CONVERT DATETIME TO JSON
        # ----------------------------------------------------

        for item in history:

            if item.get("prediction_time"):

                item["prediction_time"] = (
                    item["prediction_time"].isoformat()
                )


        # ----------------------------------------------------
        # 5. RETURN HISTORY
        # ----------------------------------------------------

        return {

            "success": True,

            "history": history

        }


    except Exception as e:

        print(
            "Prediction history error:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to load prediction history"
        )
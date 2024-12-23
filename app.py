from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn

app = FastAPI()

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adjustments based on demographic data
def adjust_demographics(age: int, gender: str, happiness: int) -> int:
    age_adj = 1 if age < 18 else (2 if age > 60 else 0)
    gender_adj = 1 if gender == "male" else 0
    happiness_adj = 2 if happiness <= 3 else (-1 if happiness >= 7 else 0)
    return age_adj + gender_adj + happiness_adj

# Determine severity based on PHQ-9 score
def classify_severity(total: int) -> str:
    ranges = {
        "none": (0, 4),
        "mild": (5, 9),
        "moderate": (10, 14),
        "moderately_severe": (15, 19),
        "severe": (20, 27),
    }
    for severity, (low, high) in ranges.items():
        if low <= total <= high:
            return severity
    return "unknown"

# Generate recommendations
def recommend(severity: str) -> str:
    recommendations = {
        "none": "Maintain a healthy lifestyle and monitor mental wellness.",
        "mild": "Try self-help strategies and monitor symptoms.",
        "moderate": "Consult a mental health professional.",
        "moderately_severe": "Seek medical advice and consider therapy.",
        "severe": "Seek immediate psychiatric help.",
    }
    return recommendations.get(severity, "No recommendation available.")

# Analyze mood trend
def mood_trend(phq_scores: List[int]) -> str:
    if all(phq_scores[i] <= phq_scores[i + 1] for i in range(len(phq_scores) - 1)):
        return "increasing"
    elif all(phq_scores[i] >= phq_scores[i + 1] for i in range(len(phq_scores) - 1)):
        return "decreasing"
    else:
        return "fluctuating"

# Evaluate risk factors based on demographic data
def evaluate_risk_factors(age: int, gender: str, trend: str) -> str:
    if age < 18:
        return "Increased risk due to age group. Monitor mental health closely."
    if age > 60:
        return "Increased risk due to age group. Regular checkups are recommended."
    if gender == "male" and trend == "increasing":
        return "Increased risk for males with worsening symptoms. Seek professional help."
    return "Risk factors are within normal range."

@app.post("/")
async def depression_detection(
    age: int = Form(...),
    gender: str = Form(...),
    happiness: int = Form(...),
    days: int = Form(...),
    request: Request = None
):
    # Collect PHQ-9 scores
    form_data = await request.form()
    phq_scores = []
    for i in range(1, days + 1):
        day_score = sum(
            int(form_data.get(f"q{j}_day{i}", 0)) 
            for j in range(1, 10)
        )
        phq_scores.append(day_score)

    # Process diagnostic data
    adjustment = adjust_demographics(age, gender, happiness)
    total_score = sum(phq_scores) + adjustment
    severity = classify_severity(total_score)
    recommendation = recommend(severity)

    # Analyze mood trend
    trend = mood_trend(phq_scores)

    # Evaluate risk factors
    risk_factor = evaluate_risk_factors(age, gender, trend)

    # Return results as JSON
    return {
        "age": age,
        "gender": gender,
        "happiness_score": happiness,
        "num_days": days,
        "phq_scores": phq_scores,
        "total_score": total_score,
        "severity": severity,
        "trend": trend,
        "recommendation": recommendation,
        "risk_factor": risk_factor
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
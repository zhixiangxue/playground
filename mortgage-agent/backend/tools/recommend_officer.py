"""Loan officer recommendation tool"""
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .requirements import LoanRequirements


def recommend_loan_officer(requirements: 'LoanRequirements') -> str:
    """
    Generate a list of matching loan officers for the user.
    
    ⚠️ CRITICAL: ONLY call when user EXPLICITLY ASKS for recommendations.
    Examples: "recommend loan officers", "find me loan officers", "who can help with my loan"
    
    ❌ DO NOT call automatically when:
    - Information is complete (they might not want recommendations yet)
    - User just updated their information
    - User hasn't mentioned wanting loan officer recommendations
    - You're just confirming or summarizing information
    
    ✅ ONLY call when:
    - User directly requests loan officer recommendations
    - User asks "who can help me" or similar questions
    
    Args:
        requirements: User's loan requirements (shared instance from agent)
        
    Returns:
        JSON string with chatkit action to display officer list
    """
    # Check if enough information is available
    missing = requirements.get_missing_fields()
    
    if "Missing:" in missing:
        # Information incomplete
        return json.dumps({
            "status": "insufficient_info",
            "message": "I need more information to recommend the right loan officer for you.",
            "missing_fields": missing,
            "suggestion": "Please complete the loan application form or provide the missing information."
        }, ensure_ascii=False)
    
    # Get user requirements for matching
    loan_amount = requirements.loan_amount or 0
    credit_score = requirements.credit_score or ""
    loan_purpose = requirements.loan_purpose or ""
    property_location = requirements.property_location or ""
    income_type = requirements.income_type or ""
    
    # Match loan officers based on requirements
    officers = _match_loan_officers(
        loan_amount=loan_amount,
        credit_score=credit_score,
        loan_purpose=loan_purpose,
        location=property_location,
        income_type=income_type
    )
    
    # Build URL with officers data as JSON in payload
    import urllib.parse
    officers_json = json.dumps(officers, ensure_ascii=False)
    encoded_officers = urllib.parse.quote(officers_json)
    
    officer_page_url = f"officers.html?data={encoded_officers}"
    
    # Return chatkit action with iframe rendering
    return json.dumps({
        "action": "chatkit",
        "type": "officers_list",
        "render": "iframe",
        "url": officer_page_url,
        "payload": {
            "officers": officers,
            "total_count": len(officers)
        },
        "message": f"Based on your requirements, I've found {len(officers)} suitable loan officers for you."
    }, ensure_ascii=False)


def _match_loan_officers(
    loan_amount: int,
    credit_score: str,
    loan_purpose: str,
    location: str,
    income_type: str
) -> list:
    """
    Match loan officers based on user requirements.
    
    This is a simplified version. In production, this would query a database
    or API with real loan officer data.
    """
    # Mock loan officers database
    all_officers = [
        {
            "name": "Sarah Johnson",
            "title": "Senior Loan Officer",
            "specialties": ["purchase", "refinance"],
            "location": "California",
            "min_credit": 620,
            "max_loan": 2000000,
            "rating": 4.9,
            "years_experience": 12,
            "contact": "sarah.johnson@example.com",
            "phone": "(555) 123-4567",
            "bio": "Specializes in first-time homebuyers and conventional loans"
        },
        {
            "name": "Michael Chen",
            "title": "VA Loan Specialist",
            "specialties": ["purchase", "refinance", "va_loan"],
            "location": "California",
            "min_credit": 580,
            "max_loan": 1500000,
            "rating": 4.8,
            "years_experience": 8,
            "contact": "michael.chen@example.com",
            "phone": "(555) 234-5678",
            "bio": "Veteran affairs specialist, helping military families"
        },
        {
            "name": "Emily Rodriguez",
            "title": "Jumbo Loan Expert",
            "specialties": ["purchase", "investment", "jumbo"],
            "location": "California",
            "min_credit": 700,
            "max_loan": 5000000,
            "rating": 4.9,
            "years_experience": 15,
            "contact": "emily.rodriguez@example.com",
            "phone": "(555) 345-6789",
            "bio": "High-value property specialist with extensive portfolio"
        },
        {
            "name": "David Kim",
            "title": "Self-Employed Specialist",
            "specialties": ["purchase", "refinance", "self_employed"],
            "location": "California",
            "min_credit": 640,
            "max_loan": 3000000,
            "rating": 4.7,
            "years_experience": 10,
            "contact": "david.kim@example.com",
            "phone": "(555) 456-7890",
            "bio": "Expert in alternative income documentation and self-employed borrowers"
        },
        {
            "name": "Jennifer Williams",
            "title": "First-Time Buyer Specialist",
            "specialties": ["purchase"],
            "location": "California",
            "min_credit": 600,
            "max_loan": 1000000,
            "rating": 4.8,
            "years_experience": 7,
            "contact": "jennifer.williams@example.com",
            "phone": "(555) 567-8901",
            "bio": "Passionate about helping first-time buyers achieve homeownership"
        }
    ]
    
    # Extract numeric credit score (take the lower bound)
    credit_numeric = 700  # default
    if credit_score:
        try:
            credit_numeric = int(credit_score.split('-')[0])
        except:
            pass
    
    # Filter officers based on requirements
    matched_officers = []
    
    for officer in all_officers:
        # Check credit score requirement
        if credit_numeric < officer["min_credit"]:
            continue
        
        # Check loan amount
        if loan_amount > officer["max_loan"]:
            continue
        
        # Check location (simplified - just check if California)
        if location and "california" not in location.lower() and "ca" not in location.lower():
            if officer["location"] != "California":
                continue
        
        # Check specialty match
        specialty_match = False
        if loan_purpose in officer["specialties"]:
            specialty_match = True
        
        # Check income type specialty
        if income_type == "self_employed" and "self_employed" in officer["specialties"]:
            specialty_match = True
        
        # Add to matched list
        matched_officers.append({
            "name": officer["name"],
            "title": officer["title"],
            "rating": officer["rating"],
            "years_experience": officer["years_experience"],
            "specialties": officer["specialties"],
            "contact": officer["contact"],
            "phone": officer["phone"],
            "bio": officer["bio"],
            "match_score": 0.9 if specialty_match else 0.7
        })
    
    # Sort by match score and rating
    matched_officers.sort(key=lambda x: (x["match_score"], x["rating"]), reverse=True)
    
    # Return top 3 matches
    return matched_officers[:3]

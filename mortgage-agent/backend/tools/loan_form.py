"""Loan form URL generator tool"""
import json
import asyncio
from urllib.parse import urlencode


def generate_loan_form_url(
    property_location: str = "",
    loan_purpose: str = "",
    property_type: str = "",
    property_status: str = "",
    loan_amount: str = "",
    down_payment: str = "",
    credit_score: str = "",
    income_type: str = "",
    military: str = "",
    self_employed: str = "",
    tax_returns: str = ""
) -> str:
    """
    **CALL THIS IMMEDIATELY when user wants to apply for a mortgage or start the loan application process.**
    
    This is the PRIMARY action tool - call it as soon as user expresses intent to apply, even without any information.
    The form will collect all necessary details interactively.
    
    Optional pre-fill parameters (all are optional, can call with no arguments):
        property_location: Property location (e.g., "Los Angeles, CA")
        loan_purpose: Loan purpose (purchase/refinance/investment/second_home)
        property_type: Property type (single_family/condo/townhouse/multi_unit/commercial)
        property_status: Property status (pre_construction/existing/foreclosure)
        loan_amount: Loan amount in USD
        down_payment: Down payment percentage (0-5/5-10/10-20/20+)
        credit_score: Credit score range (300-579/580-669/670-739/740-799/800-850)
        income_type: Income type (w2/self_employed/investment/other)
        military: Military status (yes/no)
        self_employed: Self-employed status (yes/no)
        tax_returns: Tax returns availability (yes/no)
        
    Returns:
        JSON string with chatkit action format
    """
    # Add delay to see the tool call indicator in action (for demo purposes)
    import time
    time.sleep(1.5)  # 1.5 second delay
    # Build query parameters (only include non-empty values)
    params = {}
    if property_location:
        params['propertyLocation'] = property_location
    if loan_purpose:
        params['loanPurpose'] = loan_purpose
    if property_type:
        params['propertyType'] = property_type
    if property_status:
        params['propertyStatus'] = property_status
    if loan_amount:
        params['loanAmount'] = loan_amount
    if down_payment:
        params['downPayment'] = down_payment
    if credit_score:
        params['creditScore'] = credit_score
    if income_type:
        params['incomeType'] = income_type
    if military:
        params['military'] = military
    if self_employed:
        params['selfEmployed'] = self_employed
    if tax_returns:
        params['taxReturns'] = tax_returns
    
    # Build full URL
    base_url = "loankit.html"
    if params:
        query_string = urlencode(params)
        full_url = f"{base_url}?{query_string}"
    else:
        full_url = base_url
    
    # Return special chatkit action format
    result = {
        "action": "chatkit",
        "type": "loan_form",
        "render": "iframe",
        "url": full_url,
        "method": "GET",
        "payload": params
    }
    
    return json.dumps(result, ensure_ascii=False)

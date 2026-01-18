"""Loan requirements slot parameter manager - based on loankit.html fields"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


class LoanRequirements:
    """Track and update user's loan requirements during conversation"""
    
    def __init__(self):
        # Property information
        self.property_location = None
        self.loan_purpose = None
        self.property_type = None
        self.property_status = None
        
        # Loan details
        self.loan_amount = None
        self.down_payment = None
        self.credit_score = None
        self.income_type = None
        
        # Special circumstances
        self.military = None
        self.self_employed = None
        self.tax_returns = None
    
    def _display_current_info(self):
        """Display current loan requirements in a beautiful table"""
        table = Table(title="💰 Loan Application Information", box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan", width=20)
        table.add_column("Value", style="green", width=40)
        
        # Property Information Section
        table.add_row("[bold]Property Info[/bold]", "")
        table.add_row("  Location", self.property_location or "[dim]Not set[/dim]")
        table.add_row("  Loan Purpose", self._format_value(self.loan_purpose))
        table.add_row("  Property Type", self._format_value(self.property_type))
        table.add_row("  Property Status", self._format_value(self.property_status))
        
        # Loan Details Section
        table.add_row("", "")  # Empty row for spacing
        table.add_row("[bold]Loan Details[/bold]", "")
        table.add_row("  Loan Amount", f"${self.loan_amount:,.0f}" if self.loan_amount else "[dim]Not set[/dim]")
        table.add_row("  Down Payment", f"{self.down_payment}%" if self.down_payment else "[dim]Not set[/dim]")
        table.add_row("  Credit Score", self._format_value(self.credit_score))
        table.add_row("  Income Type", self._format_value(self.income_type))
        
        # Special Circumstances
        table.add_row("", "")  # Empty row for spacing
        table.add_row("[bold]Special Info[/bold]", "")
        table.add_row("  Military", self._format_yes_no(self.military))
        table.add_row("  Self-Employed", self._format_yes_no(self.self_employed))
        table.add_row("  Tax Returns (2+ yrs)", self._format_yes_no(self.tax_returns))
        
        console.print()
        console.print(table)
        console.print()
    
    def _format_value(self, value):
        """Format value with proper styling"""
        if value is None:
            return "[dim]Not set[/dim]"
        return value.replace('_', ' ').title()
    
    def _format_yes_no(self, value):
        """Format yes/no values with emoji"""
        if value is None:
            return "[dim]Not set[/dim]"
        return "✅ Yes" if value == 'yes' else "❌ No"
    
    def update_property_location(self, location: str) -> str:
        """Update property location (e.g., 'Los Angeles, CA')"""
        self.property_location = location
        self._display_current_info()
        return f"✓ Property location updated: {location}"
    
    def update_loan_purpose(self, purpose: str) -> str:
        """
        Update loan purpose
        
        Args:
            purpose: purchase/refinance/investment/second_home
        """
        valid_purposes = ['purchase', 'refinance', 'investment', 'second_home']
        if purpose not in valid_purposes:
            return f"Invalid loan purpose. Must be one of: {', '.join(valid_purposes)}"
        self.loan_purpose = purpose
        self._display_current_info()
        return f"✓ Loan purpose updated: {purpose}"
    
    def update_property_type(self, prop_type: str) -> str:
        """
        Update property type
        
        Args:
            prop_type: single_family/condo/townhouse/multi_unit/commercial
        """
        valid_types = ['single_family', 'condo', 'townhouse', 'multi_unit', 'commercial']
        if prop_type not in valid_types:
            return f"Invalid property type. Must be one of: {', '.join(valid_types)}"
        self.property_type = prop_type
        self._display_current_info()
        return f"✓ Property type updated: {prop_type}"
    
    def update_property_status(self, status: str) -> str:
        """
        Update property status
        
        Args:
            status: pre_construction/existing/foreclosure
        """
        valid_statuses = ['pre_construction', 'existing', 'foreclosure']
        if status not in valid_statuses:
            return f"Invalid property status. Must be one of: {', '.join(valid_statuses)}"
        self.property_status = status
        self._display_current_info()
        return f"✓ Property status updated: {status}"
    
    def update_loan_amount(self, amount: float) -> str:
        """Update loan amount in USD"""
        self.loan_amount = amount
        self._display_current_info()
        return f"✓ Loan amount updated: ${amount:,.0f}"
    
    def update_down_payment(self, percentage: str) -> str:
        """
        Update down payment percentage
        
        Args:
            percentage: 0-5/5-10/10-20/20+
        """
        valid_ranges = ['0-5', '5-10', '10-20', '20+']
        if percentage not in valid_ranges:
            return f"Invalid down payment range. Must be one of: {', '.join(valid_ranges)}"
        self.down_payment = percentage
        self._display_current_info()
        return f"✓ Down payment updated: {percentage}%"
    
    def update_credit_score(self, score_range: str) -> str:
        """
        Update credit score range
        
        Args:
            score_range: 300-579/580-669/670-739/740-799/800-850
        """
        valid_ranges = ['300-579', '580-669', '670-739', '740-799', '800-850']
        if score_range not in valid_ranges:
            return f"Invalid credit score range. Must be one of: {', '.join(valid_ranges)}"
        self.credit_score = score_range
        self._display_current_info()
        return f"✓ Credit score updated: {score_range}"
    
    def update_income_type(self, income_type: str) -> str:
        """
        Update income type
        
        Args:
            income_type: w2/self_employed/investment/other
        """
        valid_types = ['w2', 'self_employed', 'investment', 'other']
        if income_type not in valid_types:
            return f"Invalid income type. Must be one of: {', '.join(valid_types)}"
        self.income_type = income_type
        self._display_current_info()
        return f"✓ Income type updated: {income_type}"
    
    def update_military(self, is_military: str) -> str:
        """
        Update military status
        
        Args:
            is_military: yes/no
        """
        if is_military not in ['yes', 'no']:
            return "Invalid military status. Must be 'yes' or 'no'"
        self.military = is_military
        self._display_current_info()
        return f"✓ Military status updated: {is_military}"
    
    def update_self_employed(self, is_self_employed: str) -> str:
        """
        Update self-employed status
        
        Args:
            is_self_employed: yes/no
        """
        if is_self_employed not in ['yes', 'no']:
            return "Invalid self-employed status. Must be 'yes' or 'no'"
        self.self_employed = is_self_employed
        self._display_current_info()
        return f"✓ Self-employed status updated: {is_self_employed}"
    
    def update_tax_returns(self, has_tax_returns: str) -> str:
        """
        Update tax returns availability (2+ years)
        
        Args:
            has_tax_returns: yes/no
        """
        if has_tax_returns not in ['yes', 'no']:
            return "Invalid tax returns status. Must be 'yes' or 'no'"
        self.tax_returns = has_tax_returns
        self._display_current_info()
        return f"✓ Tax returns status updated: {has_tax_returns}"
    
    def get_summary(self) -> str:
        """Get summary of all collected requirements"""
        fields = {
            "Property Location": self.property_location or "Not set",
            "Loan Purpose": self.loan_purpose or "Not set",
            "Property Type": self.property_type or "Not set",
            "Property Status": self.property_status or "Not set",
            "Loan Amount": f"${self.loan_amount:,.0f}" if self.loan_amount else "Not set",
            "Down Payment": f"{self.down_payment}%" if self.down_payment else "Not set",
            "Credit Score": self.credit_score or "Not set",
            "Income Type": self.income_type or "Not set",
            "Military": self.military or "Not set",
            "Self-Employed": self.self_employed or "Not set",
            "Tax Returns": self.tax_returns or "Not set"
        }
        
        summary = "📋 Current Loan Requirements:\n"
        for key, value in fields.items():
            summary += f"  • {key}: {value}\n"
        
        return summary
    
    def get_missing_fields(self) -> str:
        """Get list of missing required fields"""
        missing = []
        if not self.property_location:
            missing.append("property location")
        if not self.loan_purpose:
            missing.append("loan purpose")
        if not self.property_type:
            missing.append("property type")
        if not self.property_status:
            missing.append("property status")
        if not self.loan_amount:
            missing.append("loan amount")
        if not self.down_payment:
            missing.append("down payment")
        if not self.credit_score:
            missing.append("credit score")
        if not self.income_type:
            missing.append("income type")
        
        if not missing:
            return "All basic information collected!"
        
        return f"Missing: {', '.join(missing)}"

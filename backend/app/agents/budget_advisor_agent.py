class BudgetAdvisorAgent:
    def __init__(self):
        print("Initializing Budget Advisor Agent.")

    def check_budget(self, price: float, user_budget: float):
        """
        Compares the product price against the user's budget.
        """
        print("Budget Advisor Agent checking budget...")
        if price <= user_budget:
            advice = f"This item is within your budget of ${user_budget:.2f}."
        elif price <= user_budget * 1.2: # Within 20% over
            advice = f"This item is slightly over your budget of ${user_budget:.2f}, but might be worth considering."
        else:
            advice = f"This item is significantly over your budget of ${user_budget:.2f}."
        
        return {"advice": advice}

# Singleton instance
budget_agent = BudgetAdvisorAgent()
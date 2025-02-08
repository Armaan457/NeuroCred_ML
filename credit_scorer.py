import numpy as np
from typing import Dict, Tuple

class CIBILScoreCalculator:
    def __init__(self):
        self.weights = {
            'payment_history': 0.35,
            'credit_utilization': 0.30,
            'credit_age': 0.15,
            'credit_mix': 0.10,
            'new_credit': 0.10
        }
        
        self.MIN_SCORE = 300
        self.MAX_SCORE = 900
        self.SCORE_RANGE = self.MAX_SCORE - self.MIN_SCORE

    def calculate_payment_history_score(self, on_time_payments_percent: float, 
                                     days_late_avg: float = 0) -> float:

        base_score = on_time_payments_percent / 100
        
        # Penalty for late payments
        if days_late_avg > 0:
            late_penalty = min(days_late_avg / 90, 1)  # Max penalty at 90 days
            base_score *= (1 - late_penalty * 0.5)
            
        return base_score

    def calculate_credit_utilization_score(self, utilization_percent: float) -> float:
        if utilization_percent <= 10:
            return 0.95
        elif utilization_percent <= 30:
            return 1.0
        elif utilization_percent <= 50:
            return 0.85
        elif utilization_percent <= 75:
            return 0.60
        else:
            return 0.30

    def calculate_credit_age_score(self, years: float) -> float:
        if years >= 5:
            return 1.0
        elif years >= 3:
            return 0.85
        elif years >= 1:
            return 0.70
        else:
            return 0.40

    def calculate_credit_mix_score(self, 
                                 num_secured_loans: int,
                                 num_unsecured_loans: int,
                                 has_credit_card: bool) -> float:

        total_products = num_secured_loans + num_unsecured_loans + int(has_credit_card)
        
        if total_products == 0:
            return 0.30
        
        # Calculate diversity score
        diversity_score = min(num_secured_loans, 2) * 0.3 + \
                         min(num_unsecured_loans, 2) * 0.2 + \
                         int(has_credit_card) * 0.2
        
        return min(diversity_score, 1.0)

    def calculate_new_credit_score(self, 
                                 num_inquiries_6months: int,
                                 num_new_accounts_6months: int) -> float:

        inquiry_penalty = min(num_inquiries_6months * 0.15, 0.60)
        new_account_penalty = min(num_new_accounts_6months * 0.20, 0.60)
        
        return 1.0 - max(inquiry_penalty, new_account_penalty)

    def calculate_final_score(self, components: Dict[str, float]) -> Tuple[int, Dict[str, float]]:
        weighted_scores = {}
        total_score = 0
        
        for component, score in components.items():
            weighted_score = score * self.weights[component] * self.SCORE_RANGE
            weighted_scores[component] = weighted_score
            total_score += weighted_score
            
        final_score = int(round(total_score + self.MIN_SCORE))
        
        final_score = max(min(final_score, self.MAX_SCORE), self.MIN_SCORE)
        
        return final_score, weighted_scores

    def calculate_score(self,
                       on_time_payments_percent: float,
                       days_late_avg: float = 0,
                       utilization_percent: float = 0,
                       credit_age_years: float = 0,
                       num_secured_loans: int = 0,
                       num_unsecured_loans: int = 0,
                       has_credit_card: bool = False,
                       num_inquiries_6months: int = 0,
                       num_new_accounts_6months: int = 0) -> Tuple[int, Dict[str, float]]:

        components = {
            'payment_history': self.calculate_payment_history_score(
                on_time_payments_percent, days_late_avg
            ),
            'credit_utilization': self.calculate_credit_utilization_score(
                utilization_percent
            ),
            'credit_age': self.calculate_credit_age_score(
                credit_age_years
            ),
            'credit_mix': self.calculate_credit_mix_score(
                num_secured_loans, num_unsecured_loans, has_credit_card
            ),
            'new_credit': self.calculate_new_credit_score(
                num_inquiries_6months, num_new_accounts_6months
            )
        }
        
        return self.calculate_final_score(components)

# Example usage
calculator = CIBILScoreCalculator()

# Calculate score for a sample user
score, contributions = calculator.calculate_score(
    on_time_payments_percent=95,
    days_late_avg=5,
    utilization_percent=25,
    credit_age_years=3,
    num_secured_loans=1,
    num_unsecured_loans=1,
    has_credit_card=True,
    num_inquiries_6months=1,
    num_new_accounts_6months=0
)

print(f"Final CIBIL Score: {score}")
print("\nComponent Contributions:")
for component, contribution in contributions.items():
    print(f"{component}: {contribution:.2f}")
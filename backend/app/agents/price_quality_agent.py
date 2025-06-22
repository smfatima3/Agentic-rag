class PriceQualityAgent:
    def __init__(self):
        print("Initializing Price-Quality Agent.")
        # This agent is currently rule-based, no model loading needed.

    def assess_value(self, price: float, review_summary: str, product_features: str):
        """
        Assesses the value-for-money of a product based on price and qualitative data.
        Currently uses simple heuristics.
        """
        print("Price-Quality Agent assessing value...")
        score = 0
        assessment = ""

        # Heuristic 1: Analyze review summary for positive keywords
        positive_words = ["good", "excellent", "great", "love", "durable", "high quality", "amazing"]
        if any(word in review_summary.lower() for word in positive_words):
            score += 1

        # Heuristic 2: Analyze product features for premium keywords
        premium_words = ["premium", "pro", "plus", "metal", "advanced"]
        if any(word in product_features.lower() for word in premium_words):
            score += 1
            
        # Heuristic 3: Price-based assessment
        if price < 50:
            score += 1
            price_comment = "is very affordable."
        elif 50 <= price < 150:
            price_comment = "is in a moderate price range."
        else:
            price_comment = "is a premium-priced item."

        # Final assessment based on score
        if score >= 3:
            assessment = f"Excellent value. The product {price_comment} and has highly positive feedback and features."
        elif score == 2:
            assessment = f"Good value. The product {price_comment} and shows positive signs in reviews or features."
        else:
            assessment = f"Fair value. The product {price_comment} Consider if its specific features meet your needs."

        return {"assessment": assessment}

# Singleton instance
price_agent = PriceQualityAgent()
from .review_analyzer_agent import review_agent
from .product_research_agent import product_agent
from .price_quality_agent import price_agent
from .budget_advisor_agent import budget_agent
from PIL import Image
import json
import asyncio

class LeadAgent:
    def __init__(self):
        print("Initializing Lead Agent (Streaming).")
        self.review_agent = review_agent
        self.product_agent = product_agent
        self.price_agent = price_agent
        self.budget_agent = budget_agent

    async def run_analysis_stream(self, query: str, image: Image.Image, price: float, user_budget: float):
        """
        Orchestrates the analysis, yielding real-time updates for each agent's progress.
        """
        print("--- Lead Agent starting full analysis (streaming) ---")

        # 1. Review Analyzer Agent
        yield f"data: {json.dumps({'agent': 'ReviewAnalyzer', 'status': 'thinking'})}\n\n"
        review_analysis = self.review_agent.analyze_with_image(image)
        yield f"data: {json.dumps({'agent': 'ReviewAnalyzer', 'status': 'responded', 'output': review_analysis['summary']})}\n\n"
        await asyncio.sleep(0.1) # short delay for streaming

        # 2. Product Research Agent
        yield f"data: {json.dumps({'agent': 'ProductResearcher', 'status': 'thinking'})}\n\n"
        visual_prompt = "Describe this product in detail. What are its key visual features, materials, and potential uses?"
        visual_analysis = self.product_agent.analyze_image(image, visual_prompt)
        yield f"data: {json.dumps({'agent': 'ProductResearcher', 'status': 'responded', 'output': visual_analysis['analysis']})}\n\n"
        await asyncio.sleep(0.1)

        # 3. Price-Quality Agent
        yield f"data: {json.dumps({'agent': 'PriceQuality', 'status': 'thinking'})}\n\n"
        price_assessment = self.price_agent.assess_value(
            price=price,
            review_summary=review_analysis['summary'],
            product_features=visual_analysis['analysis']
        )
        yield f"data: {json.dumps({'agent': 'PriceQuality', 'status': 'responded', 'output': price_assessment['assessment']})}\n\n"
        await asyncio.sleep(0.1)

        # 4. Budget Advisor Agent
        yield f"data: {json.dumps({'agent': 'BudgetAdvisor', 'status': 'thinking'})}\n\n"
        budget_advice = self.budget_agent.check_budget(price, user_budget)
        yield f"data: {json.dumps({'agent': 'BudgetAdvisor', 'status': 'responded', 'output': budget_advice['advice']})}\n\n"
        await asyncio.sleep(0.1)

        print("--- Synthesizing final recommendation. ---")

        # 5. Yield the final synthesized result
        final_recommendation = {
            "title": review_analysis['top_products'][0]['product_title'] if review_analysis['top_products'] else "Recommended Product",
            "visual_summary": visual_analysis['analysis'],
            "review_summary": review_analysis['summary'],
            "value_assessment": price_assessment['assessment'],
            "budget_advice": budget_advice['advice'],
            "similar_products": review_analysis['top_products']
        }
        yield f"data: {json.dumps({'agent': 'LeadAgent', 'status': 'complete', 'output': final_recommendation})}\n\n"
        print("--- Full analysis stream complete. ---")

# Singleton instance
lead_agent = LeadAgent()
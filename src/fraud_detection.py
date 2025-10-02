"""
Fraud detection and risk analysis for UMD audit project.

This module identifies potential fraud risks and suspicious patterns in the data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from .data_loader import UMDDataLoader


class FraudDetector:
    """Class to perform fraud detection and risk analysis."""

    def __init__(self, data_loader: UMDDataLoader):
        """
        Initialize the fraud detector.

        Args:
            data_loader: UMDDataLoader instance with loaded data
        """
        self.loader = data_loader
        self.risk_factors = []
        self.suspicious_patterns = {}

    def identify_fraud_risk_factors(self) -> List[Dict]:
        """
        Identify the three most significant fraud risk factors based on the case study.

        Returns:
            List of fraud risk factors with analysis
        """
        print("Identifying fraud risk factors...")

        risk_factors = [
            {
                "factor": "Aggressive Sales Targets and Incentive Compensation",
                "description": "Management sets unrealistic sales targets with revenue-based incentive compensation",
                "assertion_affected": ["Existence/Occurrence", "Cutoff"],
                "potential_issue": "Pressure to meet targets may lead to premature revenue recognition",
                "evidence": "214% Q4 sales increase, revenue-based bonuses, aggressive growth targets",
            },
            {
                "factor": "Related Party Transactions with Distributors",
                "description": "Significant sales to distributors with close relationships",
                "assertion_affected": ["Valuation", "Completeness"],
                "potential_issue": "Distributors may be pressured to buy inventory they cannot sell",
                "evidence": "73 distributors, inventory held by company, distributor hesitancy",
            },
            {
                "factor": "Weak Internal Controls Over Revenue Recognition",
                "description": "Limited controls over timing of revenue recognition with distributors",
                "assertion_affected": ["Cutoff", "Accuracy"],
                "potential_issue": "Revenue may be recognized before transfer of control",
                "evidence": "Terms allow company to hold inventory, final sales not guaranteed",
            },
        ]

        self.risk_factors = risk_factors
        return risk_factors

    def analyze_sales_patterns(self) -> Dict:
        """
        Analyze sales patterns for suspicious activity.

        Returns:
            Dictionary with sales pattern analysis
        """
        print("Analyzing sales patterns...")

        sales_orders = self.loader.get_dataframe("sales_orders")
        if sales_orders is None:
            return {"error": "Sales orders data not loaded"}

        patterns = {
            "quarterly_sales": {},
            "unusual_patterns": [],
            "high_risk_transactions": [],
        }

        # Analyze quarterly sales trends
        if "OrderDate" in sales_orders.columns:
            sales_orders["Quarter"] = sales_orders["OrderDate"].dt.to_period("Q")
            quarterly_sales = sales_orders.groupby("Quarter")["SubTotal"].sum()

            patterns["quarterly_sales"] = quarterly_sales.to_dict()

            # Check for unusual Q4 spike
            q4_sales = quarterly_sales.get("2017Q4", 0)
            other_quarters = [v for k, v in quarterly_sales.items() if k != "2017Q4"]
            avg_other_quarters = np.mean(other_quarters) if other_quarters else 0

            if avg_other_quarters > 0:
                q4_growth = (q4_sales - avg_other_quarters) / avg_other_quarters
                if q4_growth > 1.0:  # 100%+ growth
                    patterns["unusual_patterns"].append(
                        {
                            "type": "q4_spike",
                            "description": f"Q4 sales {q4_growth:.1%} above average of other quarters",
                            "risk_level": "high",
                        }
                    )

        # Look for unusual timing patterns
        if "ModifiedTime" in sales_orders.columns:
            # Check for transactions modified after hours
            after_hours = sales_orders[
                (sales_orders["ModifiedTime"] >= "18:00")
                | (sales_orders["ModifiedTime"] <= "06:00")
            ]

            if not after_hours.empty:
                patterns["unusual_patterns"].append(
                    {
                        "type": "after_hours_modifications",
                        "description": f"{len(after_hours)} transactions modified after hours",
                        "risk_level": "medium",
                    }
                )

        # Look for round number transactions (potential red flag)
        round_amounts = sales_orders[
            (sales_orders["SubTotal"] % 1000 == 0)
            & (sales_orders["SubTotal"] > 10000)  # Focus on larger amounts
        ]

        if not round_amounts.empty:
            patterns["unusual_patterns"].append(
                {
                    "type": "round_amounts",
                    "description": f"{len(round_amounts)} large round-amount transactions",
                    "risk_level": "medium",
                }
            )

        self.suspicious_patterns = patterns
        return patterns

    def analyze_customer_patterns(self) -> Dict:
        """
        Analyze customer/distributor patterns for suspicious activity.

        Returns:
            Dictionary with customer pattern analysis
        """
        print("Analyzing customer patterns...")

        sales_orders = self.loader.get_dataframe("sales_orders")
        customer_master = self.loader.get_dataframe("customer_master")

        if sales_orders is None or customer_master is None:
            return {"error": "Required data not loaded"}

        patterns = {
            "new_customers": {},
            "high_concentration": [],
            "unusual_relationships": [],
        }

        # Analyze new customers vs existing
        if "OrderDate" in sales_orders.columns:
            # Get customers by first order date
            first_orders = sales_orders.groupby("CustID")["OrderDate"].min()
            new_customers_2017 = first_orders[first_orders.dt.year == 2017]

            patterns["new_customers"] = {
                "total_new_2017": len(new_customers_2017),
                "by_territory": new_customers_2017.reset_index()
                .merge(
                    customer_master[["CustID", "TerritoryID"]], on="CustID", how="left"
                )
                .groupby("TerritoryID")
                .size()
                .to_dict(),
            }

        # Check for customer concentration
        customer_totals = sales_orders.groupby("CustID")["SubTotal"].sum()
        total_sales = sales_orders["SubTotal"].sum()

        # Find top customers
        top_customers = customer_totals.nlargest(10)
        concentration_ratio = (
            top_customers.sum() / total_sales if total_sales > 0 else 0
        )

        if concentration_ratio > 0.5:  # Top 10 customers > 50% of sales
            patterns["high_concentration"].append(
                {
                    "type": "customer_concentration",
                    "description": f"Top 10 customers represent {concentration_ratio:.1%} of sales",
                    "risk_level": "high",
                }
            )

        # Check for unusual distributor relationships
        territory_sales = sales_orders.groupby("TerritoryID")["SubTotal"].sum()
        total_territory_sales = territory_sales.sum()

        if total_territory_sales > 0:
            # Calculate territory concentration
            max_territory_pct = territory_sales.max() / total_territory_sales
            if max_territory_pct > 0.4:  # One territory > 40% of sales
                max_territory = territory_sales.idxmax()
                patterns["unusual_relationships"].append(
                    {
                        "type": "territory_concentration",
                        "description": f"Territory {max_territory} has {max_territory_pct:.1%} of sales",
                        "risk_level": "medium",
                    }
                )

        return patterns

    def generate_audit_recommendations(self) -> List[str]:
        """
        Generate specific audit recommendations based on analysis.

        Returns:
            List of audit recommendations
        """
        recommendations = []

        # Based on fraud risk factors
        for risk in self.risk_factors:
            if "revenue recognition" in risk["potential_issue"].lower():
                recommendations.append(
                    "Perform detailed testing of revenue recognition timing, especially for Q4 transactions"
                )
            if "distributors" in risk["description"].lower():
                recommendations.append(
                    "Obtain confirmations from distributors regarding inventory held by company"
                )

        # Based on suspicious patterns
        if self.suspicious_patterns:
            patterns = self.suspicious_patterns

            if patterns.get("unusual_patterns"):
                for pattern in patterns["unusual_patterns"]:
                    if pattern["type"] == "q4_spike":
                        recommendations.append(
                            "Investigate Q4 sales spike through detailed transaction testing and distributor confirmations"
                        )
                    elif pattern["type"] == "after_hours_modifications":
                        recommendations.append(
                            "Review system logs for after-hours modifications and obtain explanations"
                        )

        # General recommendations
        recommendations.extend(
            [
                "Interview sales personnel about pressure to meet targets",
                "Review distributor agreements for right of return provisions",
                "Test cutoff procedures around year-end",
                "Consider engaging forensic specialists if material issues found",
            ]
        )

        return recommendations


def main():
    """Main function for testing fraud detection."""
    print("UMD Fraud Detection Analysis")
    print("=" * 50)

    # Initialize data loader
    loader = UMDDataLoader()
    loader.load_all_files()
    loader.clean_data_types()

    # Initialize fraud detector
    detector = FraudDetector(loader)

    try:
        # Identify fraud risk factors
        risk_factors = detector.identify_fraud_risk_factors()
        print("\nFraud Risk Factors:")
        for i, risk in enumerate(risk_factors, 1):
            print(f"{i}. {risk['factor']}")
            print(f"   Potential Issue: {risk['potential_issue']}")
            print(f"   Assertions Affected: {', '.join(risk['assertion_affected'])}")
            print()

        # Analyze sales patterns
        sales_patterns = detector.analyze_sales_patterns()
        print("Sales Pattern Analysis:")
        if "quarterly_sales" in sales_patterns:
            print("Quarterly Sales:")
            for quarter, amount in sales_patterns["quarterly_sales"].items():
                print(f"  {quarter}: ${amount:,.2f}")

        if sales_patterns.get("unusual_patterns"):
            print("\nUnusual Patterns:")
            for pattern in sales_patterns["unusual_patterns"]:
                print(
                    f"  {pattern['type']}: {pattern['description']} (Risk: {pattern['risk_level']})"
                )

        # Analyze customer patterns
        customer_patterns = detector.analyze_customer_patterns()
        print("\nCustomer Pattern Analysis:")
        if "new_customers" in customer_patterns:
            new_custs = customer_patterns["new_customers"]
            print(f"New customers in 2017: {new_custs['total_new_2017']}")

        if customer_patterns.get("high_concentration"):
            for conc in customer_patterns["high_concentration"]:
                print(f"  {conc['description']} (Risk: {conc['risk_level']})")

        # Generate recommendations
        recommendations = detector.generate_audit_recommendations()
        print("\nAudit Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")

    except Exception as e:
        print(f"Error in fraud detection: {e}")


if __name__ == "__main__":
    main()

"""
Main analysis script for UMD audit project.

This script orchestrates all analysis modules and provides comprehensive audit findings.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict
import json
import logging

from .data_loader import UMDDataLoader
from .three_way_match import ThreeWayMatchAnalyzer
from .credit_analysis import CreditAnalyzer
from .aging_analysis import AgingAnalyzer
from .fraud_detection import FraudDetector


class UMDAuditAnalysis:
    """Main class for comprehensive UMD audit analysis."""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the audit analysis.

        Args:
            data_dir: Directory containing Excel files
        """
        self.data_dir = data_dir
        self.loader = UMDDataLoader(data_dir)
        self.analyzers = {}

        # Initialize all analyzers
        self.analyzers["three_way"] = None
        self.analyzers["credit"] = None
        self.analyzers["aging"] = None
        self.analyzers["fraud"] = None

        self.results = {}

    def run_complete_analysis(self) -> Dict:
        """
        Run all audit analysis procedures.

        Returns:
            Dictionary with all analysis results
        """
        print("Starting UMD Audit Analysis")
        print("=" * 60)

        # Step 1: Load and clean data
        print("\n1. Loading and cleaning data...")
        try:
            self.loader.load_all_files()
            self._validate_data_loading()
        except Exception as e:
            error_msg = f"Data loading failed: {e}"
            print(f"⚠️  {error_msg}")
            logging.error(error_msg)
            self.results["data_loading_errors"] = [error_msg]
            # Continue with partial data if possible
            return self.results

        try:
            self.loader.clean_data_types()
            self._validate_data_cleaning()
        except Exception as e:
            error_msg = f"Data cleaning failed: {e}"
            print(f"⚠️  {error_msg}")
            logging.error(error_msg)
            self.results["data_cleaning_errors"] = [error_msg]
            # Continue with uncleaned data if possible

        # Step 2: Get data summary
        summary = self.loader.get_data_summary()
        self.results["data_summary"] = summary

        # Step 3: Verify revenue and AR balances
        print("\n2. Verifying financial statement balances...")
        revenue_df = self.loader.get_revenue_transactions()
        ar_df = self.loader.get_ar_balance()

        self.results["revenue_verification"] = {
            "transaction_count": len(revenue_df),
            "total_revenue": revenue_df["SubTotal"].sum()
            if not revenue_df.empty
            else 0,
            "expected_revenue": 84867855,
        }

        self.results["ar_verification"] = {
            "invoice_count": len(ar_df),
            "expected_balance": 11988886,
        }

        # Step 4: Three-way match analysis
        print("\n3. Performing three-way match analysis...")
        try:
            three_way_analyzer = ThreeWayMatchAnalyzer(self.loader)
            three_way_matches = three_way_analyzer.perform_three_way_match()
            three_way_summary = three_way_analyzer.get_match_summary()
            three_way_discrepancies = three_way_analyzer.analyze_discrepancies()

            self.analyzers["three_way"] = three_way_analyzer
            self.results["three_way_match"] = {
                "matches": three_way_summary,
                "discrepancies": three_way_discrepancies,
            }
            print("✓ Three-way match analysis completed")
        except Exception as e:
            error_msg = f"Three-way match analysis failed: {e}"
            print(f"⚠️  {error_msg}")
            logging.error(error_msg)
            self.results["three_way_match"] = {"error": error_msg}
            self.results["analyzer_errors"] = self.results.get(
                "analyzer_errors", []
            ) + [error_msg]

        # Step 5: Credit analysis
        print("\n4. Performing credit analysis...")
        try:
            credit_analyzer = CreditAnalyzer(self.loader)
            credit_violations = credit_analyzer.analyze_credit_limits()
            balance_analysis = credit_analyzer.analyze_balance_vs_credit_limit()
            credit_patterns = credit_analyzer.get_credit_violation_patterns()
            balance_patterns = credit_analyzer.get_balance_violation_patterns()

            self.analyzers["credit"] = credit_analyzer
            self.results["credit_analysis"] = {
                "violations": credit_violations.to_dict()
                if not credit_violations.empty
                else {},
                "balance_analysis": balance_analysis.to_dict()
                if balance_analysis is not None
                else {},
                "patterns": credit_patterns,
                "balance_patterns": balance_patterns,
            }
            print("✓ Credit analysis completed")
        except Exception as e:
            error_msg = f"Credit analysis failed: {e}"
            print(f"⚠️  {error_msg}")
            logging.error(error_msg)
            self.results["credit_analysis"] = {"error": error_msg}
            self.results["analyzer_errors"] = self.results.get(
                "analyzer_errors", []
            ) + [error_msg]

        # Step 6: Aging analysis
        print("\n5. Performing aging analysis...")
        try:
            aging_analyzer = AgingAnalyzer(self.loader)
            aging_report = aging_analyzer.perform_aging_analysis()
            allowance_assessment = aging_analyzer.assess_allowance_reasonableness()

            self.analyzers["aging"] = aging_analyzer
            self.results["aging_analysis"] = {
                "aging_report": aging_report.to_dict()
                if not aging_report.empty
                else {},
                "allowance_assessment": allowance_assessment,
            }
            print("✓ Aging analysis completed")
        except Exception as e:
            error_msg = f"Aging analysis failed: {e}"
            print(f"⚠️  {error_msg}")
            logging.error(error_msg)
            self.results["aging_analysis"] = {"error": error_msg}
            self.results["analyzer_errors"] = self.results.get(
                "analyzer_errors", []
            ) + [error_msg]

        # Step 7: Fraud detection
        print("\n6. Performing fraud detection analysis...")
        try:
            fraud_detector = FraudDetector(self.loader)
            risk_factors = fraud_detector.identify_fraud_risk_factors()
            sales_patterns = fraud_detector.analyze_sales_patterns()
            customer_patterns = fraud_detector.analyze_customer_patterns()
            recommendations = fraud_detector.generate_audit_recommendations()

            self.analyzers["fraud"] = fraud_detector
            self.results["fraud_detection"] = {
                "risk_factors": risk_factors,
                "sales_patterns": sales_patterns,
                "customer_patterns": customer_patterns,
                "recommendations": recommendations,
            }
            print("✓ Fraud detection analysis completed")
        except Exception as e:
            error_msg = f"Fraud detection analysis failed: {e}"
            print(f"⚠️  {error_msg}")
            logging.error(error_msg)
            self.results["fraud_detection"] = {"error": error_msg}
            self.results["analyzer_errors"] = self.results.get(
                "analyzer_errors", []
            ) + [error_msg]

        # Step 8: Validate analyzer results
        print("\n7. Validating analyzer results...")
        validation_success = self._validate_analyzer_results()
        if not validation_success:
            print(
                "⚠️  Analyzer result validation found issues - proceeding with caution"
            )

        # Step 9: Overall risk assessment
        print("\n8. Assessing overall audit risk...")
        overall_risk = self._assess_overall_risk()

        self.results["overall_assessment"] = overall_risk

        print("\n✓ Audit analysis completed")
        return self.results

    def _assess_overall_risk(self) -> Dict:
        """
        Assess overall audit risk based on all findings with weighted scoring.

        Returns:
            Dictionary with overall risk assessment
        """
        risk_score = 0.0
        risk_factors = []
        risk_weights = {
            "three_way": 0.25,  # 25% - Core operational risk
            "credit": 0.20,  # 20% - Credit risk
            "aging": 0.15,  # 15% - Aging/collectibility risk
            "fraud": 0.30,  # 30% - Fraud risk (highest weight)
            "data_quality": 0.10,  # 10% - Data quality issues
        }

        # Three-way match risk (weighted)
        if "three_way_match" in self.results:
            three_way = self.results["three_way_match"]
            if "error" not in three_way:
                three_way_disc = three_way.get("discrepancies", {})
                risk_level = three_way_disc.get("risk_assessment", "low")

                if risk_level == "high":
                    risk_score += risk_weights["three_way"] * 3
                    risk_factors.append("High three-way match discrepancies found")
                elif risk_level == "moderate":
                    risk_score += risk_weights["three_way"] * 2
                    risk_factors.append("Moderate three-way match discrepancies found")
                else:
                    risk_score += risk_weights["three_way"] * 1
            else:
                # Analyzer failed - add penalty
                risk_score += risk_weights["three_way"] * 2
                risk_factors.append(
                    "Three-way match analysis failed - manual review required"
                )

        # Credit analysis risk (weighted)
        if "credit_analysis" in self.results:
            credit = self.results["credit_analysis"]
            if "error" not in credit:
                # Credit limit violations
                credit_patterns = credit.get("patterns", {})
                credit_risk = credit_patterns.get("risk_assessment", "low")
                if credit_risk == "high":
                    risk_score += risk_weights["credit"] * 3
                    risk_factors.append("High credit limit violations identified")
                elif credit_risk == "moderate":
                    risk_score += risk_weights["credit"] * 2
                    risk_factors.append("Moderate credit limit violations identified")

                # Balance vs credit limit issues
                balance_patterns = credit.get("balance_patterns", {})
                balance_risk = balance_patterns.get("risk_assessment", "low")
                if balance_risk == "high":
                    risk_score += risk_weights["credit"] * 2.5
                    risk_factors.append("High balance vs credit limit issues found")
                elif balance_risk == "moderate":
                    risk_score += risk_weights["credit"] * 1.5
                    risk_factors.append("Moderate balance vs credit limit issues found")
            else:
                # Analyzer failed - add penalty
                risk_score += risk_weights["credit"] * 2
                risk_factors.append("Credit analysis failed - manual review required")

        # Aging analysis risk (weighted)
        if "aging_analysis" in self.results:
            aging = self.results["aging_analysis"]
            if "error" not in aging:
                allowance_assessment = aging.get("allowance_assessment", {})
                assessment = allowance_assessment.get("assessment", "reasonable")

                if assessment == "questionable":
                    difference = allowance_assessment.get("difference", 0)
                    # Weight based on magnitude of difference
                    severity = min(abs(difference) / 100000, 3)  # Cap at 3x weight
                    risk_score += risk_weights["aging"] * (2 + severity)
                    risk_factors.append(
                        "Allowance for doubtful accounts may be unreasonable"
                    )
                elif assessment == "aggressive":
                    risk_score += risk_weights["aging"] * 2.5
                    risk_factors.append("Aggressive allowance for doubtful accounts")
            else:
                # Analyzer failed - add penalty
                risk_score += risk_weights["aging"] * 2
                risk_factors.append("Aging analysis failed - manual review required")

        # Fraud detection risk (weighted highest)
        if "fraud_detection" in self.results:
            fraud = self.results["fraud_detection"]
            if "error" not in fraud:
                # Count high-risk patterns
                sales_patterns = fraud.get("sales_patterns", {})
                unusual_patterns = sales_patterns.get("unusual_patterns", [])
                high_risk_count = sum(
                    1 for p in unusual_patterns if p.get("risk_level") == "high"
                )
                medium_risk_count = sum(
                    1 for p in unusual_patterns if p.get("risk_level") == "medium"
                )

                fraud_score = (high_risk_count * 3) + (medium_risk_count * 2)
                if fraud_score > 0:
                    # Normalize to weight allocation
                    normalized_fraud_score = min(fraud_score / 3, 3)  # Cap at 3x weight
                    risk_score += risk_weights["fraud"] * normalized_fraud_score
                    risk_factors.extend(
                        [
                            p["description"]
                            for p in unusual_patterns
                            if p.get("risk_level") in ["high", "medium"]
                        ]
                    )
            else:
                # Analyzer failed - add penalty
                risk_score += risk_weights["fraud"] * 2
                risk_factors.append(
                    "Fraud detection analysis failed - manual review required"
                )

        # Data quality risk
        if (
            "data_loading_errors" in self.results
            or "data_cleaning_errors" in self.results
        ):
            error_count = len(self.results.get("data_loading_errors", [])) + len(
                self.results.get("data_cleaning_errors", [])
            )
            risk_score += risk_weights["data_quality"] * min(error_count * 2, 3)
            risk_factors.append("Data quality issues detected")

        if "analyzer_errors" in self.results:
            analyzer_error_count = len(self.results["analyzer_errors"])
            risk_score += risk_weights["data_quality"] * min(
                analyzer_error_count * 1.5, 3
            )
            risk_factors.append("Analyzer failures detected")

        # Cross-validation: Check consistency between different analyzers
        consistency_score = self._cross_validate_analyzer_results()
        if consistency_score < 0.7:  # Less than 70% consistency
            risk_score += 0.5  # Add 0.5 to overall score for inconsistency
            risk_factors.append("Inconsistencies detected between analyzer results")

        # Determine overall risk level (normalized to 0-5 scale)
        max_possible_score = 5.0
        normalized_risk_score = min(risk_score, max_possible_score)

        if normalized_risk_score >= 3.5:
            overall_risk = "high"
        elif normalized_risk_score >= 2.0:
            overall_risk = "moderate"
        else:
            overall_risk = "low"

        return {
            "risk_score": round(normalized_risk_score, 2),
            "risk_level": overall_risk,
            "risk_factors": risk_factors,
            "risk_weights_used": risk_weights,
            "recommendations": self._generate_weighted_recommendations(
                overall_risk, risk_factors
            ),
        }

    def _cross_validate_analyzer_results(self) -> float:
        """Cross-validate results between analyzers for consistency."""
        consistency_score = 1.0

        # Check revenue consistency between data loader and analyzers
        if "revenue_verification" in self.results and "three_way_match" in self.results:
            revenue_data = self.results["revenue_verification"]
            three_way = self.results["three_way_match"]

            if "error" not in three_way:
                calculated_revenue = revenue_data.get("total_revenue", 0)
                expected_revenue = revenue_data.get("expected_revenue", 0)

                if expected_revenue > 0:
                    variance = (
                        abs(calculated_revenue - expected_revenue) / expected_revenue
                    )
                    if variance > 0.1:  # More than 10% variance
                        consistency_score -= 0.3

        # Check aging analysis consistency with credit analysis
        if "aging_analysis" in self.results and "credit_analysis" in self.results:
            aging = self.results["aging_analysis"]
            credit = self.results["credit_analysis"]

            if "error" not in aging and "error" not in credit:
                # If there are many credit violations, aging should show collection issues
                credit_violations = credit.get("patterns", {}).get(
                    "total_violations", 0
                )
                aging_assessment = aging.get("allowance_assessment", {}).get(
                    "assessment", "reasonable"
                )

                if credit_violations > 100 and aging_assessment == "reasonable":
                    consistency_score -= (
                        0.2  # Inconsistency: high violations but reasonable aging
                    )

        return max(consistency_score, 0.0)

    def _generate_weighted_recommendations(
        self, risk_level: str, risk_factors: list
    ) -> list:
        """Generate recommendations based on risk level and specific factors."""
        base_recommendations = {
            "high": [
                "Engage forensic specialists for detailed investigation",
                "Perform extended procedures on high-risk areas",
                "Increase sample sizes significantly for testing",
                "Consider additional audit procedures beyond standard scope",
                "Increase professional skepticism throughout engagement",
            ],
            "moderate": [
                "Increase sample sizes for testing in identified risk areas",
                "Perform extended procedures on moderate-risk areas",
                "Consider engaging specialists for complex areas",
                "Increase professional skepticism throughout engagement",
                "Monitor for changes in risk factors",
            ],
            "low": [
                "Standard audit procedures appear sufficient",
                "Monitor for changes in risk factors",
                "Document and assess control effectiveness",
            ],
        }

        recommendations = base_recommendations.get(
            risk_level, base_recommendations["low"]
        )

        # Add specific recommendations based on risk factors
        if any("fraud" in factor.lower() for factor in risk_factors):
            recommendations.insert(0, "Implement additional fraud detection procedures")
        if any("allowance" in factor.lower() for factor in risk_factors):
            recommendations.insert(0, "Review allowance methodology and documentation")
        if any("credit" in factor.lower() for factor in risk_factors):
            recommendations.insert(0, "Review credit approval and monitoring processes")

        return recommendations[:6]  # Limit to top 6 recommendations

    def generate_audit_report(self, output_file: str = None) -> str:
        """
        Generate a comprehensive audit report.

        Args:
            output_file: Optional file to save the report

        Returns:
            String containing the audit report
        """
        report = []
        report.append("UMD AUDIT ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Data Quality Assessment
        data_quality_issues = []
        if "data_loading_errors" in self.results:
            data_quality_issues.extend(self.results["data_loading_errors"])
        if "data_cleaning_errors" in self.results:
            data_quality_issues.extend(self.results["data_cleaning_errors"])
        if "analyzer_errors" in self.results:
            data_quality_issues.extend(self.results["analyzer_errors"])
        if "validation_warnings" in self.results:
            data_quality_issues.extend(self.results["validation_warnings"])

        if data_quality_issues:
            report.append("DATA QUALITY ASSESSMENT")
            report.append("-" * 25)
            report.append("⚠️  Issues detected during analysis:")
            for issue in data_quality_issues:
                report.append(f"• {issue}")
            report.append("Note: Results may be impacted by data quality issues.")
            report.append("")

        # Executive Summary
        report.append("EXECUTIVE SUMMARY")
        report.append("-" * 20)

        if "overall_assessment" in self.results:
            assessment = self.results["overall_assessment"]
            report.append(
                f"Overall Risk Assessment: {assessment['risk_level'].upper()}"
            )
            report.append(f"Risk Score: {assessment['risk_score']}/5")
            report.append("")

            # Add risk weighting information for transparency
            if "risk_weights_used" in assessment:
                report.append("Risk Weighting Applied:")
                weights = assessment["risk_weights_used"]
                report.append(f"• Three-way matching: {weights['three_way']:.0%}")
                report.append(f"• Credit analysis: {weights['credit']:.0%}")
                report.append(f"• Aging analysis: {weights['aging']:.0%}")
                report.append(f"• Fraud detection: {weights['fraud']:.0%}")
                report.append(f"• Data quality: {weights['data_quality']:.0%}")
                report.append("")

            if assessment["risk_factors"]:
                report.append("Key Risk Factors:")
                for factor in assessment["risk_factors"]:
                    report.append(f"• {factor}")
                report.append("")

            # Add specific findings summary
            findings_summary = []
            if (
                "three_way_match" in self.results
                and "error" not in self.results["three_way_match"]
            ):
                three_way = self.results["three_way_match"]
                matches = three_way.get("matches", {})
                if matches:
                    match_rates = [
                        stats.get("match_rate", 0) for stats in matches.values()
                    ]
                    avg_match_rate = (
                        sum(match_rates) / len(match_rates) if match_rates else 0
                    )
                    findings_summary.append(
                        f"Three-way match rate: {avg_match_rate:.1%}"
                    )

            if (
                "credit_analysis" in self.results
                and "error" not in self.results["credit_analysis"]
            ):
                credit = self.results["credit_analysis"]
                violations = credit.get("patterns", {}).get("total_violations", 0)
                if violations > 0:
                    findings_summary.append(f"Credit violations: {violations:,}")

            if (
                "aging_analysis" in self.results
                and "error" not in self.results["aging_analysis"]
            ):
                aging = self.results["aging_analysis"]
                allowance = aging.get("allowance_assessment", {})
                if allowance.get("assessment") == "questionable":
                    findings_summary.append("Aging allowance assessment: questionable")

            if (
                "fraud_detection" in self.results
                and "error" not in self.results["fraud_detection"]
            ):
                fraud = self.results["fraud_detection"]
                high_risks = [
                    p
                    for p in fraud.get("sales_patterns", {}).get("unusual_patterns", [])
                    if p.get("risk_level") == "high"
                ]
                if high_risks:
                    findings_summary.append(
                        f"High fraud risk patterns: {len(high_risks)}"
                    )

            if findings_summary:
                report.append("Key Findings Summary:")
                for finding in findings_summary:
                    report.append(f"• {finding}")
                report.append("")

        # Financial Statement Verification
        report.append("FINANCIAL STATEMENT VERIFICATION")
        report.append("-" * 35)

        if "revenue_verification" in self.results:
            rev = self.results["revenue_verification"]
            report.append("Revenue Analysis:")
            report.append(f"• Transactions identified: {rev['transaction_count']:,}")
            report.append(f"• Total revenue calculated: ${rev['total_revenue']:,.2f}")
            report.append(f"• Expected revenue: ${rev['expected_revenue']:,.2f}")
            report.append("")

        if "ar_verification" in self.results:
            ar = self.results["ar_verification"]
            report.append("Accounts Receivable Analysis:")
            report.append(f"• Unpaid invoices identified: {ar['invoice_count']:,}")
            report.append(f"• Expected AR balance: ${ar['expected_balance']:,.2f}")
            report.append("")

        # Three-way Match Results
        if "three_way_match" in self.results:
            report.append("THREE-WAY MATCH RESULTS")
            report.append("-" * 25)

            three_way = self.results["three_way_match"]
            for match_type, stats in three_way["matches"].items():
                report.append(f"{match_type.replace('_', ' ').title()}:")
                report.append(f"• Match rate: {stats['match_rate']:.2%}")
                report.append("")

        # Credit Analysis
        if "credit_analysis" in self.results:
            report.append("CREDIT ANALYSIS")
            report.append("-" * 15)

            credit = self.results["credit_analysis"]
            if credit["patterns"]["total_violations"] > 0:
                report.append(
                    f"• Credit limit violations: {credit['patterns']['total_violations']:,}"
                )
            if credit["balance_patterns"]["total_excess_customers"] > 0:
                report.append(
                    f"• Customers exceeding limits: {credit['balance_patterns']['total_excess_customers']:,}"
                )
            report.append("")

        # Aging Analysis
        if "aging_analysis" in self.results:
            report.append("AGING ANALYSIS")
            report.append("-" * 15)

            aging = self.results["aging_analysis"]
            if aging["allowance_assessment"]["assessment"]:
                report.append(
                    f"• Allowance assessment: {aging['allowance_assessment']['assessment']}"
                )
                if aging["allowance_assessment"]["difference"] != 0:
                    report.append(
                        f"• Recommended adjustment: ${aging['allowance_assessment']['difference']:,.2f}"
                    )
            report.append("")

        # Fraud Detection
        if "fraud_detection" in self.results:
            report.append("FRAUD RISK ASSESSMENT")
            report.append("-" * 22)

            fraud = self.results["fraud_detection"]
            report.append("Key Fraud Risk Factors:")
            for risk in fraud["risk_factors"]:
                report.append(f"• {risk['factor']}")
            report.append("")

            if fraud["recommendations"]:
                report.append("Recommended Actions:")
                for rec in fraud["recommendations"][:5]:  # Show top 5
                    report.append(f"• {rec}")
                report.append("")

        # Overall Recommendations
        if "overall_assessment" in self.results:
            report.append("OVERALL AUDIT RECOMMENDATIONS")
            report.append("-" * 32)

            overall = self.results["overall_assessment"]
            for rec in overall["recommendations"]:
                report.append(f"• {rec}")
            report.append("")

        final_report = "\n".join(report)

        if output_file:
            with open(output_file, "w") as f:
                f.write(final_report)
            print(f"✓ Report saved to: {output_file}")

        return final_report

    def _validate_data_loading(self):
        """Validate that all required data files were loaded successfully."""
        required_dfs = [
            "sales_orders",
            "customer_invoices",
            "products",
            "shipments",
            "customer_master",
        ]
        missing_dfs = []

        for df_name in required_dfs:
            if not hasattr(self.loader, "dfs") or df_name not in self.loader.dfs:
                missing_dfs.append(df_name)
                continue

            df = self.loader.dfs[df_name]
            if df is None or df.empty:
                missing_dfs.append(df_name)
                continue

            # Check for minimum expected size
            min_rows = 10  # Reasonable minimum for audit data
            if len(df) < min_rows:
                print(
                    f"⚠️  Warning: {df_name} has only {len(df)} rows (minimum expected: {min_rows})"
                )
                logging.warning(f"DataFrame {df_name} has insufficient rows: {len(df)}")

        if missing_dfs:
            error_msg = f"Missing required DataFrames: {', '.join(missing_dfs)}"
            raise ValueError(error_msg)

        print(
            f"✓ All required data files loaded successfully ({len(required_dfs)} DataFrames)"
        )

    def _validate_data_cleaning(self):
        """Validate that data cleaning was successful and key columns are properly formatted."""
        validation_errors = []

        # Validate key financial columns in sales_orders
        if "sales_orders" in self.loader.dfs:
            so_df = self.loader.dfs["sales_orders"]
            if "SubTotal" in so_df.columns:
                try:
                    # Check if SubTotal is numeric and has reasonable values
                    subtotal_values = pd.to_numeric(so_df["SubTotal"], errors="coerce")
                    if subtotal_values.isna().any():
                        validation_errors.append(
                            "Non-numeric values found in sales_orders.SubTotal"
                        )

                    # Check for negative values (unusual for revenue)
                    negative_count = (subtotal_values < 0).sum()
                    if negative_count > 0:
                        print(
                            f"⚠️  Warning: {negative_count} negative SubTotal values found in sales_orders"
                        )

                    # Check if total is reasonable (not zero or extremely large)
                    total_revenue = subtotal_values.sum()
                    if total_revenue <= 0:
                        validation_errors.append("Total revenue is zero or negative")
                    elif total_revenue > 1e9:  # $1B seems excessive for this dataset
                        print(
                            f"⚠️  Warning: Total revenue is very large: ${total_revenue:,.2f}"
                        )

                except Exception as e:
                    validation_errors.append(
                        f"Error validating sales_orders.SubTotal: {e}"
                    )

        # Validate key columns in customer_invoices
        if "customer_invoices" in self.loader.dfs:
            ci_df = self.loader.dfs["customer_invoices"]
            if "Amount" in ci_df.columns:
                try:
                    amount_values = pd.to_numeric(ci_df["Amount"], errors="coerce")
                    if amount_values.isna().any():
                        validation_errors.append(
                            "Non-numeric values found in customer_invoices.Amount"
                        )

                    # Check for reasonable amount ranges
                    if (amount_values < 0).any():
                        print("⚠️  Warning: Negative invoice amounts found")

                except Exception as e:
                    validation_errors.append(
                        f"Error validating customer_invoices.Amount: {e}"
                    )

        if validation_errors:
            error_msg = f"Data validation failed: {'; '.join(validation_errors)}"
            raise ValueError(error_msg)

        print("✓ Data cleaning validation passed")

    def _validate_analyzer_results(self):
        """Validate that analyzer results are reasonable and complete."""
        validation_warnings = []

        # Validate three-way match results
        if "three_way_match" in self.results:
            three_way = self.results["three_way_match"]
            if "matches" in three_way:
                for match_type, stats in three_way["matches"].items():
                    match_rate = stats.get("match_rate", 0)
                    if match_rate < 0.5:  # Less than 50% match rate is concerning
                        validation_warnings.append(
                            f"Low {match_type} match rate: {match_rate:.2%}"
                        )
                    elif match_rate > 1.0:  # Shouldn't exceed 100%
                        validation_warnings.append(
                            f"Invalid {match_type} match rate: {match_rate:.2%}"
                        )

        # Validate credit analysis results
        if "credit_analysis" in self.results:
            credit = self.results["credit_analysis"]
            total_violations = credit.get("patterns", {}).get("total_violations", 0)
            if total_violations > 1000:  # Arbitrary high threshold
                validation_warnings.append(
                    f"Very high number of credit violations: {total_violations}"
                )

        # Validate aging analysis results
        if "aging_analysis" in self.results:
            aging = self.results["aging_analysis"]
            allowance_assessment = aging.get("allowance_assessment", {})
            if allowance_assessment.get("assessment") == "questionable":
                difference = allowance_assessment.get("difference", 0)
                if abs(difference) > 1000000:  # $1M difference is significant
                    validation_warnings.append(
                        f"Large allowance adjustment recommended: ${difference:,.2f}"
                    )

        if validation_warnings:
            print("⚠️  Validation warnings:")
            for warning in validation_warnings:
                print(f"  - {warning}")
            self.results["validation_warnings"] = validation_warnings

        return len(validation_warnings) == 0


def main():
    """Main function to run the complete UMD audit analysis."""
    print("UMD Comprehensive Audit Analysis")
    print("=" * 60)

    try:
        # Initialize and run analysis
        analysis = UMDAuditAnalysis()
        results = analysis.run_complete_analysis()

        # Generate report
        report = analysis.generate_audit_report("umd_audit_report.txt")

        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print("Key findings have been saved to umd_audit_report.txt")
        print("Review the full report for detailed analysis and recommendations.")

    except Exception as e:
        print(f"Error running analysis: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

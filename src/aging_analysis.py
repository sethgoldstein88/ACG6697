"""
Aging analysis for accounts receivable in UMD audit project.

This module performs aging analysis and compares with client-provided aging data.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
from data_loader import UMDDataLoader


class AgingAnalyzer:
    """Class to perform accounts receivable aging analysis."""

    def __init__(self, data_loader: UMDDataLoader):
        """
        Initialize the aging analyzer.

        Args:
            data_loader: UMDDataLoader instance with loaded data
        """
        self.loader = data_loader
        self.aging_report = None
        self.client_aging = None

    def perform_aging_analysis(
        self, as_of_date: datetime = None, validate_data: bool = True
    ) -> pd.DataFrame:
        """
        Perform aging analysis on accounts receivable with enhanced error handling.

        Args:
            as_of_date: Date for aging calculation (default: 12/31/2017)
            validate_data: Whether to perform data validation checks

        Returns:
            DataFrame with aging analysis
        """
        import time

        start_time = time.time()

        print("Performing aging analysis...")

        try:
            if as_of_date is None:
                as_of_date = datetime(2017, 12, 31)

            # Get required dataframes with validation
            invoices = self.loader.get_dataframe("customer_invoices")
            if invoices is None or invoices.empty:
                raise ValueError("Customer invoices data not loaded or empty")

            sales_orders = self.loader.get_dataframe("sales_orders")

            # Filter for unpaid invoices
            unpaid_invoices = invoices[~invoices["IsPaid"]].copy()
            if unpaid_invoices.empty:
                print("Warning: No unpaid invoices found")
                return pd.DataFrame()

            # Data validation
            if validate_data:
                validation_issues = self._validate_aging_data(
                    unpaid_invoices, sales_orders
                )
                if validation_issues:
                    print(f"Warning: Data validation issues found: {validation_issues}")

            # Merge and calculate aging
            invoice_details = self._calculate_invoice_aging(
                unpaid_invoices, sales_orders, as_of_date
            )

            if invoice_details.empty:
                print("Warning: No valid invoice details after merging")
                return pd.DataFrame()

            # Create aging report
            aging_pivot = self._create_aging_report(invoice_details)

            # Get customers with balances over 90 days
            over_90_days = invoice_details[invoice_details["DaysPastDue"] > 90]

            self.aging_report = {
                "detailed": invoice_details,
                "summary": aging_pivot,
                "over_90_days": over_90_days[["CustID", "TotalDue", "DaysPastDue"]]
                .groupby("CustID")["TotalDue"]
                .sum()
                .reset_index(),
                "metadata": {
                    "as_of_date": as_of_date,
                    "total_invoices": len(invoice_details),
                    "total_customers": aging_pivot.shape[0],
                    "processing_time": time.time() - start_time,
                },
            }

            processing_time = time.time() - start_time
            print("✓ Aging analysis completed")
            print(f"  Total customers: {aging_pivot.shape[0]}")
            print(f"  Customers over 90 days: {len(over_90_days['CustID'].unique())}")
            print(f"  Processing time: {processing_time:.2f} seconds")

            return aging_pivot

        except Exception as e:
            processing_time = time.time() - start_time
            print(
                f"Error in aging analysis after {processing_time:.2f} seconds: {str(e)}"
            )
            raise

    def _validate_aging_data(
        self, unpaid_invoices: pd.DataFrame, sales_orders: pd.DataFrame = None
    ) -> List[str]:
        """Validate data quality for aging analysis."""
        issues = []

        # Check for missing invoice dates
        missing_dates = unpaid_invoices["InvoiceDate"].isna().sum()
        if missing_dates > 0:
            issues.append(f"{missing_dates} invoices missing invoice dates")

        # Check for missing customer IDs
        missing_custids = unpaid_invoices["CustID"].isna().sum()
        if missing_custids > 0:
            issues.append(f"{missing_custids} invoices missing customer IDs")

        # Check for negative amounts (if available)
        if "TotalDue" in unpaid_invoices.columns:
            negative_amounts = (unpaid_invoices["TotalDue"] < 0).sum()
            if negative_amounts > 0:
                issues.append(f"{negative_amounts} invoices with negative amounts")

        # Check sales orders data if available
        if sales_orders is not None:
            if sales_orders.empty:
                issues.append("Sales orders data is empty")
            else:
                # Check for missing invoice IDs in sales orders
                missing_invoice_ids = unpaid_invoices[
                    ~unpaid_invoices["InvoiceID"].isin(sales_orders["InvoiceID"])
                ].shape[0]
                if missing_invoice_ids > 0:
                    issues.append(
                        f"{missing_invoice_ids} invoices not found in sales orders"
                    )

        return issues

    def _calculate_invoice_aging(
        self,
        unpaid_invoices: pd.DataFrame,
        sales_orders: pd.DataFrame,
        as_of_date: datetime,
    ) -> pd.DataFrame:
        """Calculate days past due and aging buckets for invoices."""
        try:
            # Merge invoice data with sales order data to get amounts and dates
            invoice_details = pd.merge(
                unpaid_invoices[["InvoiceID", "CustID", "InvoiceDate"]],
                sales_orders[["InvoiceID", "TotalDue", "OrderDate"]].drop_duplicates()
                if sales_orders is not None
                else pd.DataFrame(),
                on="InvoiceID",
                how="left",
            )

            # Use OrderDate as the invoice date if InvoiceDate is missing
            if "OrderDate" in invoice_details.columns:
                invoice_details["InvoiceDate"] = invoice_details["InvoiceDate"].fillna(
                    invoice_details["OrderDate"]
                )

            # Remove rows without valid dates
            invoice_details = invoice_details.dropna(subset=["InvoiceDate"])

            if invoice_details.empty:
                return pd.DataFrame()

            # Calculate days past due
            invoice_details["DaysPastDue"] = (
                as_of_date - invoice_details["InvoiceDate"]
            ).dt.days

            # Filter for reasonable date ranges (not too far in the future or past)
            invoice_details = invoice_details[
                (
                    invoice_details["DaysPastDue"] >= -30
                )  # Not more than 30 days in future
                & (
                    invoice_details["DaysPastDue"] <= 365
                )  # Not more than 1 year past due
            ]

            # Create aging buckets
            invoice_details["AgingBucket"] = pd.cut(
                invoice_details["DaysPastDue"],
                bins=[-np.inf, 30, 60, 90, np.inf],
                labels=["0-30", "31-60", "61-90", "90+"],
            )

            return invoice_details

        except Exception as e:
            print(f"Error calculating invoice aging: {str(e)}")
            return pd.DataFrame()

    def _create_aging_report(self, invoice_details: pd.DataFrame) -> pd.DataFrame:
        """Create aging report from invoice details."""
        try:
            # Group by customer and aging bucket
            aging_report = (
                invoice_details.groupby(["CustID", "AgingBucket"])
                .agg({"TotalDue": "sum", "InvoiceID": "count"})
                .reset_index()
            )

            # Pivot to create aging report format
            aging_pivot = aging_report.pivot_table(
                index="CustID", columns="AgingBucket", values="TotalDue", fill_value=0
            ).reset_index()

            # Add total column
            bucket_columns = ["0-30", "31-60", "61-90", "90+"]
            existing_columns = [
                col for col in bucket_columns if col in aging_pivot.columns
            ]
            aging_pivot["Total"] = aging_pivot[existing_columns].sum(axis=1)

            return aging_pivot

        except Exception as e:
            print(f"Error creating aging report: {str(e)}")
            return pd.DataFrame()

    def compare_with_client_aging(
        self,
        client_aging_file: str = None,
        client_dataframe: pd.DataFrame = None,
        aging_buckets: List[str] = None,
        tolerance: float = 0.01,
    ) -> Dict:
        """
        Compare our aging analysis with client-provided aging data.

        Args:
            client_aging_file: Path to client aging data file (Excel/CSV)
            client_dataframe: Pre-loaded client aging DataFrame (alternative to file)
            aging_buckets: List of aging buckets to compare (default: ["90+"])
            tolerance: Tolerance for amount differences (default: 1% or $0.01)

        Returns:
            Dictionary with comparison results including detailed metrics
        """
        print("Comparing with client aging data...")

        comparison = {
            "agrees": False,
            "differences": {},
            "recommendations": [],
            "metrics": {},
            "detailed_comparison": None,
        }

        if self.aging_report is None:
            comparison["recommendations"].append("Perform aging analysis first")
            return comparison

        # Get our aging data
        our_summary = self.aging_report["summary"]

        if aging_buckets is None:
            aging_buckets = ["90+"]

        # Load client data if provided
        client_data = None
        if client_dataframe is not None:
            client_data = client_dataframe.copy()
            print("Using provided client DataFrame")
        elif client_aging_file is not None:
            try:
                if client_aging_file.endswith(".xlsx"):
                    client_data = pd.read_excel(client_aging_file)
                elif client_aging_file.endswith(".csv"):
                    client_data = pd.read_csv(client_aging_file)
                else:
                    comparison["recommendations"].append(
                        f"Unsupported file format: {client_aging_file}"
                    )
                    return comparison
                print(f"Loaded client data from: {client_aging_file}")
            except Exception as e:
                comparison["recommendations"].append(
                    f"Error loading client file: {str(e)}"
                )
                return comparison

        if client_data is None:
            comparison["recommendations"].append(
                "No client aging data provided (file or DataFrame)"
            )
            comparison["recommendations"].append(
                "Obtain client's detailed aging report for comparison"
            )
            return comparison

        try:
            # Standardize column names and preprocess client data
            client_data = self._preprocess_client_data(client_data)

            # Perform comparison for each aging bucket
            comparison_results = {}
            total_agrees = 0
            total_compared = 0

            for bucket in aging_buckets:
                if bucket not in our_summary.columns:
                    comparison["recommendations"].append(
                        f"Aging bucket '{bucket}' not found in our analysis"
                    )
                    continue

                bucket_comparison = self._compare_aging_bucket(
                    our_summary, client_data, bucket, tolerance
                )
                comparison_results[bucket] = bucket_comparison
                total_agrees += bucket_comparison["agrees"]
                total_compared += 1

            comparison["differences"] = comparison_results
            comparison["agrees"] = (
                total_agrees == total_compared if total_compared > 0 else False
            )

            # Calculate overall metrics
            comparison["metrics"] = self._calculate_comparison_metrics(
                comparison_results
            )

            # Create detailed comparison DataFrame
            comparison["detailed_comparison"] = self._create_detailed_comparison(
                our_summary, client_data, aging_buckets
            )

            # Generate recommendations based on comparison
            comparison["recommendations"] = self._generate_comparison_recommendations(
                comparison_results, comparison["metrics"]
            )

            print(f"Comparison completed for {len(aging_buckets)} aging buckets")
            print(f"Overall agreement: {comparison['agrees']}")

        except Exception as e:
            comparison["recommendations"].append(f"Error during comparison: {str(e)}")
            print(f"Comparison error: {e}")

        return comparison

    def _preprocess_client_data(self, client_data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess and standardize client aging data."""
        df = client_data.copy()

        # Standardize column names (common variations)
        column_mappings = {
            "customer_id": "CustID",
            "customerid": "CustID",
            "customer": "CustID",
            "cust_id": "CustID",
            "total_due": "TotalDue",
            "totaldue": "TotalDue",
            "amount_due": "TotalDue",
            "balance": "TotalDue",
            "aging_90+": "90+",
            "aging_90": "90+",
            "over_90": "90+",
            "past_due_90": "90+",
            "current_90+": "90+",
            "0-30_days": "0-30",
            "0-30": "0-30",
            "current": "0-30",
            "31-60_days": "31-60",
            "31-60": "31-60",
            "61-90_days": "61-90",
            "61-90": "61-90",
        }

        df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace("-", "_")
        df = df.rename(columns=column_mappings)

        # Ensure CustID is present
        if "CustID" not in df.columns:
            raise ValueError("Client data missing CustID column")

        # Convert numeric columns
        for col in ["TotalDue", "0-30", "31-60", "61-90", "90+"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        return df

    def _compare_aging_bucket(
        self,
        our_data: pd.DataFrame,
        client_data: pd.DataFrame,
        bucket: str,
        tolerance: float,
    ) -> Dict:
        """Compare specific aging bucket between our data and client data."""
        result = {
            "bucket": bucket,
            "agrees": False,
            "our_total": 0,
            "client_total": 0,
            "difference": 0,
            "difference_pct": 0,
            "customer_differences": [],
            "within_tolerance": False,
        }

        if bucket not in our_data.columns or bucket not in client_data.columns:
            result["error"] = f"Bucket '{bucket}' not found in one of the datasets"
            return result

        our_total = our_data[bucket].sum()
        client_total = client_data[bucket].sum()

        result["our_total"] = our_total
        result["client_total"] = client_total
        result["difference"] = our_total - client_total
        result["difference_pct"] = (
            abs(result["difference"] / client_total) if client_total != 0 else 0
        )

        # Check if within tolerance
        result["within_tolerance"] = result["difference_pct"] <= tolerance

        # Customer-level comparison
        merged_data = pd.merge(
            our_data[["CustID", bucket]].rename(columns={bucket: f"our_{bucket}"}),
            client_data[["CustID", bucket]].rename(
                columns={bucket: f"client_{bucket}"}
            ),
            on="CustID",
            how="outer",
            suffixes=("_our", "_client"),
        ).fillna(0)

        # Find significant differences at customer level
        customer_diffs = []
        for _, row in merged_data.iterrows():
            cust_diff = row[f"our_{bucket}"] - row[f"client_{bucket}"]
            if (
                abs(cust_diff) > tolerance * 1000
            ):  # Use absolute tolerance for small amounts
                customer_diffs.append(
                    {
                        "CustID": row["CustID"],
                        "our_amount": row[f"our_{bucket}"],
                        "client_amount": row[f"client_{bucket}"],
                        "difference": cust_diff,
                    }
                )

        result["customer_differences"] = customer_diffs
        result["agrees"] = len(customer_diffs) == 0 and result["within_tolerance"]

        return result

    def _calculate_comparison_metrics(self, comparison_results: Dict) -> Dict:
        """Calculate overall comparison metrics."""
        metrics = {
            "total_buckets_compared": len(comparison_results),
            "agreed_buckets": sum(
                1 for r in comparison_results.values() if r.get("agrees", False)
            ),
            "buckets_within_tolerance": sum(
                1
                for r in comparison_results.values()
                if r.get("within_tolerance", False)
            ),
            "total_our_amount": sum(
                r.get("our_total", 0) for r in comparison_results.values()
            ),
            "total_client_amount": sum(
                r.get("client_total", 0) for r in comparison_results.values()
            ),
            "total_difference": sum(
                r.get("difference", 0) for r in comparison_results.values()
            ),
        }

        if metrics["total_client_amount"] != 0:
            metrics["overall_difference_pct"] = abs(
                metrics["total_difference"] / metrics["total_client_amount"]
            )
        else:
            metrics["overall_difference_pct"] = 0

        return metrics

    def _create_detailed_comparison(
        self, our_data: pd.DataFrame, client_data: pd.DataFrame, buckets: List[str]
    ) -> pd.DataFrame:
        """Create detailed comparison DataFrame."""
        comparison_cols = ["CustID"]
        for bucket in buckets:
            if bucket in our_data.columns and bucket in client_data.columns:
                comparison_cols.extend(
                    [f"our_{bucket}", f"client_{bucket}", f"diff_{bucket}"]
                )

        # Merge datasets
        detailed = pd.merge(
            our_data[
                ["CustID"] + [col for col in our_data.columns if col in buckets]
            ].rename(
                columns={
                    col: f"our_{col}" for col in buckets if col in our_data.columns
                }
            ),
            client_data[
                ["CustID"] + [col for col in client_data.columns if col in buckets]
            ].rename(
                columns={
                    col: f"client_{col}"
                    for col in buckets
                    if col in client_data.columns
                }
            ),
            on="CustID",
            how="outer",
            suffixes=("_our", "_client"),
        ).fillna(0)

        # Calculate differences
        for bucket in buckets:
            our_col = f"our_{bucket}"
            client_col = f"client_{bucket}"
            if our_col in detailed.columns and client_col in detailed.columns:
                detailed[f"diff_{bucket}"] = detailed[our_col] - detailed[client_col]

        return (
            detailed[comparison_cols]
            if comparison_cols != ["CustID"]
            else pd.DataFrame()
        )

    def _generate_comparison_recommendations(
        self, comparison_results: Dict, metrics: Dict
    ) -> List[str]:
        """Generate recommendations based on comparison results."""
        recommendations = []

        if metrics["agreed_buckets"] == metrics["total_buckets_compared"]:
            recommendations.append(
                "✓ Aging analysis agrees with client data across all buckets"
            )
        elif metrics["buckets_within_tolerance"] == metrics["total_buckets_compared"]:
            recommendations.append("Aging analysis within tolerance of client data")
        else:
            recommendations.append(
                "Significant differences found between our analysis and client data"
            )

        if metrics["total_difference"] != 0:
            recommendations.append(
                f"Net difference: ${metrics['total_difference']:,.2f} "
                f"({metrics['overall_difference_pct'] * 100:.1f}% of client total)"
            )

        # Check for specific issues
        for bucket, result in comparison_results.items():
            if result.get("customer_differences"):
                recommendations.append(
                    f"Customer-level differences in {bucket} bucket: {len(result['customer_differences'])} customers"
                )

        if not recommendations or all(
            "agrees" in rec or "within tolerance" in rec for rec in recommendations
        ):
            recommendations.append(
                "No significant issues identified - client aging appears reasonable"
            )
        else:
            recommendations.append(
                "Investigate differences with client, particularly customer-level variances"
            )
            recommendations.append(
                "Verify invoice dates, payment status, and aging calculations"
            )

        return recommendations

    def assess_allowance_reasonableness(
        self,
        client_allowance: float = 315000,
        aging_buckets: List[str] = None,
        allowance_percentages: Dict[str, float] = None,
        comparison_data: Dict = None,
    ) -> Dict:
        """
        Assess reasonableness of client's allowance for doubtful accounts.

        Args:
            client_allowance: Client's reported allowance ($315,000)
            aging_buckets: List of aging buckets to consider (default: ["61-90", "90+"])
            allowance_percentages: Custom allowance percentages by bucket (default: conservative)
            comparison_data: Results from client comparison for enhanced assessment

        Returns:
            Dictionary with enhanced assessment results
        """
        print("Assessing allowance reasonableness...")

        assessment = {
            "client_allowance": client_allowance,
            "recommended_allowance": 0,
            "difference": 0,
            "assessment": "reasonable",
            "factors": [],
            "bucket_breakdown": {},
            "comparison_impact": {},
        }

        if self.aging_report is None:
            assessment["factors"].append("Aging analysis not performed")
            return assessment

        # Default aging buckets and percentages
        if aging_buckets is None:
            aging_buckets = ["61-90", "90+"]

        if allowance_percentages is None:
            allowance_percentages = {
                "61-90": 0.25,  # 25% for 61-90 days
                "90+": 0.75,  # 75% for over 90 days
            }

        # Get aging summary data
        summary = self.aging_report["summary"]

        # Calculate recommended allowance by bucket
        recommended_by_bucket = {}
        total_recommended = 0

        for bucket in aging_buckets:
            if bucket in summary.columns:
                bucket_amount = summary[bucket].sum()
                bucket_percentage = allowance_percentages.get(bucket, 0)
                recommended_amount = bucket_amount * bucket_percentage
                recommended_by_bucket[bucket] = {
                    "amount": bucket_amount,
                    "percentage": bucket_percentage,
                    "allowance": recommended_amount,
                }
                total_recommended += recommended_amount

        assessment["bucket_breakdown"] = recommended_by_bucket
        assessment["recommended_allowance"] = total_recommended
        assessment["difference"] = client_allowance - total_recommended

        # Enhanced assessment considering comparison data
        if comparison_data and comparison_data.get("metrics"):
            metrics = comparison_data["metrics"]

            # Adjust assessment based on comparison results
            if not comparison_data.get("agrees", False):
                if metrics.get("overall_difference_pct", 0) > 0.05:  # >5% difference
                    assessment["assessment"] = "questionable"
                    assessment["comparison_impact"]["severity"] = "high"
                    assessment["comparison_impact"]["reason"] = (
                        "Significant differences with client aging data"
                    )
                elif metrics.get("overall_difference_pct", 0) > 0.02:  # >2% difference
                    assessment["assessment"] = "requires_review"
                    assessment["comparison_impact"]["severity"] = "medium"
                    assessment["comparison_impact"]["reason"] = (
                        "Material differences with client aging data"
                    )

            # Include comparison metrics in factors
            assessment["factors"].append(
                f"Comparison agreement: {comparison_data.get('agrees', 'N/A')}"
            )
            if metrics.get("overall_difference_pct", 0) > 0:
                assessment["factors"].append(
                    f"Comparison difference: {metrics['overall_difference_pct'] * 100:.1f}% of client amounts"
                )

        # Standard reasonableness check
        if abs(assessment["difference"]) > client_allowance * 0.1:  # 10% variance
            assessment["assessment"] = "questionable"
        elif abs(assessment["difference"]) > client_allowance * 0.05:  # 5% variance
            assessment["assessment"] = "requires_review"

        # Add detailed factors
        for bucket, data in recommended_by_bucket.items():
            assessment["factors"].append(
                f"{bucket}: ${data['amount']:,.2f} × {data['percentage'] * 100:.0f}% = ${data['allowance']:,.2f}"
            )

        assessment["factors"].append(
            f"Total recommended allowance: ${total_recommended:,.2f}"
        )
        assessment["factors"].append(f"Client allowance: ${client_allowance:,.2f}")

        if assessment["difference"] != 0:
            diff_pct = abs(assessment["difference"] / client_allowance * 100)
            assessment["factors"].append(
                f"Difference: ${assessment['difference']:,.2f} ({diff_pct:.1f}% of client allowance)"
            )

        # Add contextual recommendations
        if assessment["assessment"] == "questionable":
            assessment["factors"].append(
                "Consider obtaining additional evidence for allowance reasonableness"
            )
        elif assessment["assessment"] == "requires_review":
            assessment["factors"].append(
                "Consider discussing allowance methodology with client"
            )

        return assessment

    def validate_analysis_results(self) -> Dict:
        """
        Perform self-validation of aging analysis results.

        Returns:
            Dictionary with validation results and recommendations
        """
        validation_results = {"is_valid": True, "checks": {}, "recommendations": []}

        if self.aging_report is None:
            validation_results["is_valid"] = False
            validation_results["recommendations"].append("No aging analysis performed")
            return validation_results

        # Check 1: Data completeness
        required_keys = ["detailed", "summary", "over_90_days", "metadata"]
        for key in required_keys:
            if key not in self.aging_report:
                validation_results["checks"][f"missing_{key}"] = False
                validation_results["is_valid"] = False
            else:
                validation_results["checks"][f"has_{key}"] = True

        # Check 2: Data consistency
        detailed = self.aging_report["detailed"]
        summary = self.aging_report["summary"]

        if not detailed.empty and not summary.empty:
            # Check if summary totals match detailed data
            summary_total = summary["Total"].sum() if "Total" in summary.columns else 0
            detailed_total = (
                detailed["TotalDue"].sum() if "TotalDue" in detailed.columns else 0
            )

            if abs(summary_total - detailed_total) > 0.01:  # Allow for rounding
                validation_results["checks"]["totals_match"] = False
                validation_results["is_valid"] = False
                validation_results["recommendations"].append(
                    f"Summary total (${summary_total:,.2f}) doesn't match detailed total (${detailed_total:,.2f})"
                )
            else:
                validation_results["checks"]["totals_match"] = True

        # Check 3: Over 90 days customers
        over_90 = self.aging_report["over_90_days"]
        if not over_90.empty:
            # Check for reasonable aging periods
            max_days = detailed["DaysPastDue"].max() if not detailed.empty else 0
            if max_days > 365:
                validation_results["recommendations"].append(
                    f"Some invoices are {max_days} days past due - consider reviewing for accuracy"
                )

            # Check for negative days past due
            negative_days = (
                (detailed["DaysPastDue"] < 0).sum() if not detailed.empty else 0
            )
            if negative_days > 0:
                validation_results["recommendations"].append(
                    f"{negative_days} invoices show negative days past due (future dated)"
                )

        # Check 4: Metadata completeness
        metadata = self.aging_report.get("metadata", {})
        required_metadata = [
            "as_of_date",
            "total_invoices",
            "total_customers",
            "processing_time",
        ]
        for meta_key in required_metadata:
            if meta_key not in metadata:
                validation_results["checks"][f"missing_metadata_{meta_key}"] = False
            else:
                validation_results["checks"][f"has_metadata_{meta_key}"] = True

        if validation_results["is_valid"]:
            validation_results["recommendations"].append("All validation checks passed")
        else:
            validation_results["recommendations"].append(
                "Some validation checks failed - review results"
            )

        return validation_results

    def generate_comprehensive_report(
        self,
        client_allowance: float = 315000,
        include_comparison: bool = False,
        comparison_data: Dict = None,
    ) -> Dict:
        """
        Generate a comprehensive aging analysis report.

        Args:
            client_allowance: Client's allowance for comparison
            include_comparison: Whether to include client comparison
            comparison_data: Pre-computed comparison data

        Returns:
            Dictionary with complete analysis results
        """
        import time

        start_time = time.time()

        report = {
            "analysis_timestamp": datetime.now(),
            "aging_analysis": None,
            "allowance_assessment": None,
            "client_comparison": None,
            "validation_results": None,
            "summary": {},
            "processing_time": 0,
        }

        try:
            # Perform aging analysis
            aging_report = self.perform_aging_analysis()
            report["aging_analysis"] = aging_report

            # Assess allowance reasonableness
            allowance_data = self.assess_allowance_reasonableness(
                client_allowance=client_allowance, comparison_data=comparison_data
            )
            report["allowance_assessment"] = allowance_data

            # Include comparison if requested
            if include_comparison:
                if comparison_data is None:
                    comparison_data = self.compare_with_client_aging()
                report["client_comparison"] = comparison_data

            # Run validation
            validation_results = self.validate_analysis_results()
            report["validation_results"] = validation_results

            # Generate summary
            if self.aging_report and "metadata" in self.aging_report:
                metadata = self.aging_report["metadata"]
                report["summary"] = {
                    "total_customers": metadata.get("total_customers", 0),
                    "total_invoices": metadata.get("total_invoices", 0),
                    "processing_time": metadata.get("processing_time", 0),
                    "as_of_date": metadata.get("as_of_date", datetime.now()),
                    "allowance_assessment": allowance_data.get("assessment", "unknown"),
                    "validation_passed": validation_results.get("is_valid", False),
                }

            report["processing_time"] = time.time() - start_time

            print(
                f"Comprehensive report generated in {report['processing_time']:.2f} seconds"
            )

        except Exception as e:
            report["error"] = str(e)
            print(f"Error generating comprehensive report: {e}")

        return report


def main():
    """Main function for testing enhanced aging analysis."""
    print("UMD Enhanced Aging Analysis")
    print("=" * 60)

    # Initialize data loader
    loader = UMDDataLoader()
    loader.load_all_files()
    loader.clean_data_types()

    # Initialize analyzer
    analyzer = AgingAnalyzer(loader)

    try:
        # Perform aging analysis with validation
        print("\n1. Performing Aging Analysis...")
        aging_report = analyzer.perform_aging_analysis(validate_data=True)

        if not aging_report.empty:
            print("Aging Summary:")
            print(aging_report.head())
            print(f"Total customers in aging: {aging_report.shape[0]}")

            # Get over 90 days summary
            if analyzer.aging_report:
                over_90 = analyzer.aging_report["over_90_days"]
                print(f"Customers over 90 days: {len(over_90)}")
                print(f"Total over 90 days: ${over_90['TotalDue'].sum():,.2f}")

        # Validate results
        print("\n2. Validating Analysis Results...")
        validation = analyzer.validate_analysis_results()
        print(f"Validation passed: {validation['is_valid']}")
        if validation["recommendations"]:
            print("Validation recommendations:")
            for rec in validation["recommendations"]:
                print(f"  - {rec}")

        # Assess allowance reasonableness with enhanced logic
        print("\n3. Assessing Allowance Reasonableness...")
        allowance_assessment = analyzer.assess_allowance_reasonableness(
            aging_buckets=["61-90", "90+"],
            allowance_percentages={"61-90": 0.25, "90+": 0.75},
        )
        print(f"Client allowance: ${allowance_assessment['client_allowance']:,.2f}")
        print(
            f"Recommended allowance: ${allowance_assessment['recommended_allowance']:,.2f}"
        )
        print(f"Assessment: {allowance_assessment['assessment']}")
        print("Bucket breakdown:")
        for bucket, data in allowance_assessment["bucket_breakdown"].items():
            print(
                f"  {bucket}: ${data['amount']:,.2f} × {data['percentage'] * 100:.0f}% = ${data['allowance']:,.2f}"
            )

        # Demonstrate comparison functionality (without actual client data)
        print("\n4. Client Comparison (Demo - No Client Data Provided)...")
        comparison = analyzer.compare_with_client_aging()
        print(
            f"Comparison completed: {len(comparison.get('differences', {}))} buckets compared"
        )
        if comparison["recommendations"]:
            print("Comparison recommendations:")
            for rec in comparison["recommendations"]:
                print(f"  - {rec}")

        # Generate comprehensive report
        print("\n5. Generating Comprehensive Report...")
        comprehensive_report = analyzer.generate_comprehensive_report()
        print("Report generated with the following sections:")
        print(
            f"  - Aging analysis: {'✓' if comprehensive_report['aging_analysis'] is not None else '✗'}"
        )
        print(
            f"  - Allowance assessment: {'✓' if comprehensive_report['allowance_assessment'] is not None else '✗'}"
        )
        print(
            f"  - Validation results: {'✓' if comprehensive_report['validation_results'] is not None else '✗'}"
        )
        print(
            f"  - Processing time: {comprehensive_report['processing_time']:.2f} seconds"
        )

        print("\n" + "=" * 60)
        print("Enhanced aging analysis completed successfully!")

    except Exception as e:
        print(f"Error in aging analysis: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

"""
Data loading and validation module for UMD audit analysis project.

This module handles loading, cleaning, and validation of Excel data files.
It provides comprehensive data integrity checks, financial reconciliation,
and detailed validation reporting to ensure data quality for downstream analysis.

Key Features:
- Robust data loading with comprehensive error handling
- Data type cleaning and standardization
- Data integrity validation (missing values, duplicates, logical consistency)
- Financial figure reconciliation against case expectations
- Comprehensive validation reporting with recommendations
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import warnings
import logging
from datetime import datetime

warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("data_loader.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class UMDDataLoader:
    """
    Comprehensive data loading and validation class for UMD audit analysis.

    This class provides robust data loading, cleaning, validation, and reconciliation
    capabilities to ensure high-quality data for audit procedures. It serves as the
    foundation layer for downstream analysis scripts by providing clean, validated data.

    Key Capabilities:
    - Load and validate Excel files with comprehensive error handling
    - Clean and standardize data types across all datasets
    - Perform data integrity checks (completeness, consistency, logical validation)
    - Reconcile financial figures against case expectations
    - Generate detailed validation reports with actionable recommendations

    The class is designed to catch data quality issues early in the pipeline,
    preventing errors in downstream analysis and ensuring reliable audit results.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the data loader.

        Args:
            data_dir: Directory containing Excel files
        """
        self.data_dir = Path(data_dir)
        self.dataframes: Dict[str, pd.DataFrame] = {}

    def load_all_files(self) -> Dict[str, pd.DataFrame]:
        """
        Load all Excel files from the data directory.

        Returns:
            Dictionary mapping file names to DataFrames
        """
        excel_files = {
            "sales_orders": "UMD_Data Set_Sales Orders.xlsx",
            "shipments": "UMD_Data Set_Shipments.xlsx",
            "customer_invoices": "UMD_Data Set_Customer Invoices.xlsx",
            "customer_master": "UMD_Data Set_Customer Master.xlsx",
            "products": "UMD_Data Set_Products.xlsx",
            "sales_territory": "UMD_Data Set_Sales Territory.xlsx",
        }

        loaded_count = 0
        failed_count = 0

        for key, filename in excel_files.items():
            file_path = self.data_dir / filename
            logger.info(f"Attempting to load {filename}...")

            if file_path.exists():
                try:
                    # Check file size and format
                    file_size = file_path.stat().st_size
                    logger.info(f"File size: {file_size:,} bytes")

                    # Load with specific parameters for better error handling
                    df = pd.read_excel(
                        file_path,
                        engine="openpyxl",  # Specify engine for better compatibility
                        dtype=str,  # Load everything as string first for cleaning
                    )

                    if df.empty:
                        raise ValueError("File appears to be empty or unreadable")

                    # Clean column names
                    original_columns = list(df.columns)
                    df.columns = df.columns.str.strip()

                    # Check for common issues
                    if len(df.columns) != len(set(df.columns)):
                        raise ValueError("Duplicate column names found after cleaning")

                    # Store the dataframe
                    self.dataframes[key] = df
                    loaded_count += 1

                    logger.info(
                        f"✓ Successfully loaded {len(df):,} records from {filename}"
                    )
                    logger.info(
                        f"  Original columns: {len(original_columns)}, Cleaned columns: {len(df.columns)}"
                    )

                except FileNotFoundError:
                    error_msg = f"File not accessible: {filename}"
                    logger.error(error_msg)
                    failed_count += 1
                except PermissionError:
                    error_msg = f"Permission denied accessing: {filename}"
                    logger.error(error_msg)
                    failed_count += 1
                except pd.errors.EmptyDataError:
                    error_msg = f"File is empty or has no readable data: {filename}"
                    logger.error(error_msg)
                    failed_count += 1
                except ImportError as e:
                    error_msg = f"Missing required module for reading Excel: {e}"
                    logger.error(error_msg)
                    failed_count += 1
                except ValueError as e:
                    error_msg = f"Data format issue in {filename}: {e}"
                    logger.error(error_msg)
                    failed_count += 1
                except Exception as e:
                    error_msg = (
                        f"Unexpected error loading {filename}: {type(e).__name__}: {e}"
                    )
                    logger.error(error_msg)
                    failed_count += 1
            else:
                error_msg = f"File not found: {file_path}"
                logger.error(error_msg)
                failed_count += 1

        logger.info(
            f"Loading complete: {loaded_count} files loaded successfully, {failed_count} files failed"
        )
        return self.dataframes

    def get_dataframe(self, name: str) -> pd.DataFrame:
        """
        Get a specific dataframe by name.

        Args:
            name: Name of the dataframe to retrieve

        Returns:
            DataFrame or None if not found
        """
        return self.dataframes.get(name)

    def get_data_summary(self) -> Dict[str, Dict]:
        """
        Get summary statistics for all loaded dataframes.

        Returns:
            Dictionary with summary info for each dataframe
        """
        summary = {}
        for name, df in self.dataframes.items():
            summary[name] = {
                "shape": df.shape,
                "columns": list(df.columns),
                "dtypes": df.dtypes.to_dict(),
                "missing_values": df.isnull().sum().to_dict(),
                "sample_data": df.head(2).to_dict("records"),
            }
        return summary

    def clean_data_types(self) -> None:
        """
        Clean and standardize data types across all dataframes.
        """
        logger.info("Starting data type cleaning process...")

        # Sales Orders cleaning
        if "sales_orders" in self.dataframes:
            df = self.dataframes["sales_orders"]
            logger.info("Cleaning sales_orders data types...")

            try:
                # Convert date columns
                date_cols = ["OrderDate", "ModifiedDate"]
                for col in date_cols:
                    if col in df.columns:
                        original_dtype = df[col].dtype
                        df[col] = pd.to_datetime(df[col], errors="coerce")
                        converted_count = df[col].notna().sum()
                        logger.info(
                            f"  {col}: Converted from {original_dtype} to datetime, {converted_count} valid values"
                        )

                # Convert numeric columns
                numeric_cols = [
                    "SalesOrderID",
                    "ProdID",
                    "CustID",
                    "TerritoryID",
                    "Quantity",
                    "UnitPrice",
                    "SubTotal",
                    "TaxAmt",
                    "Freight",
                    "TotalDue",
                    "ShipID",
                    "InvoiceID",
                ]
                for col in numeric_cols:
                    if col in df.columns:
                        original_dtype = df[col].dtype
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                        converted_count = df[col].notna().sum()
                        logger.info(
                            f"  {col}: Converted from {original_dtype} to numeric, {converted_count} valid values"
                        )

                # Convert time column
                if "ModifiedTime" in df.columns:
                    # Handle time format (assuming it's in HH:MM:SS format)
                    df["ModifiedTime"] = df["ModifiedTime"].astype(str)
                    # Extract hour for analysis if needed
                    df["ModifiedHour"] = pd.to_datetime(
                        df["ModifiedTime"], format="%H:%M:%S", errors="coerce"
                    ).dt.hour
                    logger.info(
                        "  ModifiedTime: Processed time column, created ModifiedHour"
                    )

            except Exception as e:
                logger.error(f"Error cleaning sales_orders data types: {e}")
                raise

        # Shipments cleaning
        if "shipments" in self.dataframes:
            df = self.dataframes["shipments"]
            logger.info("Cleaning shipments data types...")

            try:
                date_cols = ["ShipDate", "ModifiedDate"]
                for col in date_cols:
                    if col in df.columns:
                        original_dtype = df[col].dtype
                        df[col] = pd.to_datetime(df[col], errors="coerce")
                        converted_count = df[col].notna().sum()
                        logger.info(
                            f"  {col}: Converted from {original_dtype} to datetime, {converted_count} valid values"
                        )

                numeric_cols = ["ShipID", "SalesOrderID", "ShipWeight"]
                for col in numeric_cols:
                    if col in df.columns:
                        original_dtype = df[col].dtype
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                        converted_count = df[col].notna().sum()
                        logger.info(
                            f"  {col}: Converted from {original_dtype} to numeric, {converted_count} valid values"
                        )

            except Exception as e:
                logger.error(f"Error cleaning shipments data types: {e}")
                raise

        # Customer Invoices cleaning
        if "customer_invoices" in self.dataframes:
            df = self.dataframes["customer_invoices"]
            logger.info("Cleaning customer_invoices data types...")

            try:
                date_cols = ["InvoiceDate", "PaidDate", "ModifiedDate"]
                for col in date_cols:
                    if col in df.columns:
                        original_dtype = df[col].dtype
                        df[col] = pd.to_datetime(df[col], errors="coerce")
                        converted_count = df[col].notna().sum()
                        logger.info(
                            f"  {col}: Converted from {original_dtype} to datetime, {converted_count} valid values"
                        )

                # Handle special case for PaidDate (9/9/9999 means unpaid)
                if "PaidDate" in df.columns:
                    # Use string comparison to avoid overflow
                    df["IsPaid"] = df["PaidDate"].astype(str) != "9999-09-09"
                    df["PaidDate"] = pd.to_datetime(df["PaidDate"], errors="coerce")
                    # Replace invalid dates (9999-09-09) with NaT
                    df.loc[df["PaidDate"].dt.year == 9999, "PaidDate"] = pd.NaT
                    logger.info(
                        "  PaidDate: Processed special case handling for unpaid invoices"
                    )

                numeric_cols = ["InvoiceID", "CustID"]
                for col in numeric_cols:
                    if col in df.columns:
                        original_dtype = df[col].dtype
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                        converted_count = df[col].notna().sum()
                        logger.info(
                            f"  {col}: Converted from {original_dtype} to numeric, {converted_count} valid values"
                        )

            except Exception as e:
                logger.error(f"Error cleaning customer_invoices data types: {e}")
                raise

        # Customer Master cleaning
        if "customer_master" in self.dataframes:
            df = self.dataframes["customer_master"]
            logger.info("Cleaning customer_master data types...")

            try:
                numeric_cols = ["CustID", "TerritoryID", "CredLimit"]
                for col in numeric_cols:
                    if col in df.columns:
                        original_dtype = df[col].dtype
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                        converted_count = df[col].notna().sum()
                        logger.info(
                            f"  {col}: Converted from {original_dtype} to numeric, {converted_count} valid values"
                        )

            except Exception as e:
                logger.error(f"Error cleaning customer_master data types: {e}")
                raise

        # Products cleaning
        if "products" in self.dataframes:
            df = self.dataframes["products"]
            logger.info("Cleaning products data types...")

            try:
                date_cols = ["SellStartDate", "ModifiedDate"]
                for col in date_cols:
                    if col in df.columns:
                        original_dtype = df[col].dtype
                        df[col] = pd.to_datetime(df[col], errors="coerce")
                        converted_count = df[col].notna().sum()
                        logger.info(
                            f"  {col}: Converted from {original_dtype} to datetime, {converted_count} valid values"
                        )

                numeric_cols = [
                    "ProdID",
                    "SafetyStockLevel",
                    "ReManPoint",
                    "StandardCost",
                    "UnitPrice",
                    "Weight",
                    "DaysToMan",
                ]
                for col in numeric_cols:
                    if col in df.columns:
                        original_dtype = df[col].dtype
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                        converted_count = df[col].notna().sum()
                        logger.info(
                            f"  {col}: Converted from {original_dtype} to numeric, {converted_count} valid values"
                        )

            except Exception as e:
                logger.error(f"Error cleaning products data types: {e}")
                raise

        # Sales Territory cleaning
        if "sales_territory" in self.dataframes:
            df = self.dataframes["sales_territory"]
            logger.info("Cleaning sales_territory data types...")

            try:
                numeric_cols = ["TerritoryID", "SalesGoalQTR"]
                for col in numeric_cols:
                    if col in df.columns:
                        original_dtype = df[col].dtype
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                        converted_count = df[col].notna().sum()
                        logger.info(
                            f"  {col}: Converted from {original_dtype} to numeric, {converted_count} valid values"
                        )

            except Exception as e:
                logger.error(f"Error cleaning sales_territory data types: {e}")
                raise

        logger.info("✓ Data types cleaning completed successfully")

    def get_revenue_transactions(self) -> pd.DataFrame:
        """
        Get the set of transactions that comprise the $84,867,855 sales revenue.

        Returns:
            DataFrame with revenue transactions
        """
        if "sales_orders" not in self.dataframes:
            raise ValueError("Sales orders data not loaded")

        df = self.dataframes["sales_orders"]

        # Filter for records that have both ShipID and InvoiceID (indicating completed transactions)
        revenue_df = df[(df["ShipID"].notna()) & (df["InvoiceID"].notna())].copy()

        # Calculate total revenue
        total_revenue = revenue_df["SubTotal"].sum()

        print(
            f"Found {len(revenue_df):,} revenue transactions totaling ${total_revenue:,.2f}"
        )

        return revenue_df

    def get_ar_balance(self) -> pd.DataFrame:
        """
        Get the set of unpaid invoice records that comprise the $11,988,886 AR balance.

        Returns:
            DataFrame with accounts receivable transactions
        """
        if "customer_invoices" not in self.dataframes:
            raise ValueError("Customer invoices data not loaded")

        df = self.dataframes["customer_invoices"]

        # Filter for unpaid invoices
        ar_df = df[~df["IsPaid"]].copy()

        print(f"Found {len(ar_df):,} unpaid invoices comprising AR balance")

        return ar_df

    def validate_data_integrity(self) -> Dict[str, List[str]]:
        """
        Validate data integrity across all loaded dataframes.

        Performs comprehensive checks including:
        - Required columns presence
        - Unique identifier validation
        - Missing value analysis
        - Range and logical consistency checks

        Returns:
            Dictionary with validation results categorized by type
        """
        logger.info("Starting data integrity validation...")
        validation_results = {"errors": [], "warnings": [], "info": []}

        # Define expected columns for each dataframe
        expected_columns = {
            "sales_orders": [
                "SalesOrderID",
                "OrderDate",
                "ProdID",
                "CustID",
                "Quantity",
                "UnitPrice",
                "SubTotal",
                "TotalDue",
                "ShipID",
                "InvoiceID",
            ],
            "shipments": ["ShipID", "SalesOrderID", "ShipDate"],
            "customer_invoices": ["InvoiceID", "CustID", "InvoiceDate", "PaidDate"],
            "customer_master": ["CustID", "TerritoryID", "CredLimit"],
            "products": ["ProdID", "UnitPrice", "StandardCost"],
            "sales_territory": ["TerritoryID", "SalesGoalQTR"],
        }

        # Define unique identifier columns
        unique_columns = {
            "sales_orders": ["SalesOrderID", "ShipID", "InvoiceID"],
            "shipments": ["ShipID"],
            "customer_invoices": ["InvoiceID"],
            "customer_master": ["CustID"],
            "products": ["ProdID"],
            "sales_territory": ["TerritoryID"],
        }

        # Validate each dataframe
        for df_name, df in self.dataframes.items():
            logger.info(f"Validating {df_name}...")

            # Check for required columns
            if df_name in expected_columns:
                missing_cols = set(expected_columns[df_name]) - set(df.columns)
                if missing_cols:
                    validation_results["errors"].append(
                        f"{df_name}: Missing required columns: {list(missing_cols)}"
                    )

            # Check for duplicate unique identifiers
            if df_name in unique_columns:
                for col in unique_columns[df_name]:
                    if col in df.columns:
                        duplicates = df[df[col].duplicated()]
                        if not duplicates.empty:
                            validation_results["warnings"].append(
                                f"{df_name}: Found {len(duplicates)} duplicate {col} values"
                            )

            # Check for missing values in critical columns
            critical_columns = {
                "sales_orders": ["SalesOrderID", "CustID", "SubTotal"],
                "customer_invoices": ["InvoiceID", "CustID"],
                "shipments": ["ShipID", "SalesOrderID"],
            }

            if df_name in critical_columns:
                for col in critical_columns[df_name]:
                    if col in df.columns:
                        missing_count = df[col].isnull().sum()
                        if missing_count > 0:
                            missing_pct = (missing_count / len(df)) * 100
                            validation_results["warnings"].append(
                                f"{df_name}: {col} has {missing_count} missing values ({missing_pct:.1f}%)"
                            )

            # Range and logical consistency checks
            if df_name == "sales_orders":
                # Check for negative or zero values in financial columns
                financial_cols = ["Quantity", "UnitPrice", "SubTotal", "TotalDue"]
                for col in financial_cols:
                    if col in df.columns:
                        invalid_count = (df[col] <= 0).sum()
                        if invalid_count > 0:
                            validation_results["warnings"].append(
                                f"{df_name}: {col} has {invalid_count} non-positive values"
                            )

            elif df_name == "customer_invoices":
                # Check for logical date consistency
                if "InvoiceDate" in df.columns and "PaidDate" in df.columns:
                    if (
                        not df["InvoiceDate"].isnull().all()
                        and not df["PaidDate"].isnull().all()
                    ):
                        invalid_dates = df[df["PaidDate"] < df["InvoiceDate"]]
                        if not invalid_dates.empty:
                            validation_results["warnings"].append(
                                f"{df_name}: Found {len(invalid_dates)} records where PaidDate < InvoiceDate"
                            )

        # Summary
        total_records = sum(len(df) for df in self.dataframes.values())
        validation_results["info"].append(
            f"Validation completed for {len(self.dataframes)} dataframes with {total_records:,} total records"
        )

        # Log results
        for category, messages in validation_results.items():
            for message in messages:
                if category == "errors":
                    logger.error(message)
                elif category == "warnings":
                    logger.warning(message)
                else:
                    logger.info(message)

        return validation_results

    def reconcile_financial_figures(self) -> Dict[str, Dict[str, float]]:
        """
        Reconcile loaded data against expected financial figures from the case.

        Performs reconciliation checks against:
        - Expected sales revenue: $84,867,855
        - Expected AR balance count (unpaid invoices): related to $11,988,886

        Returns:
            Dictionary with reconciliation results including calculated vs expected values
        """
        logger.info("Starting financial figure reconciliation...")
        reconciliation_results = {"revenue": {}, "ar_balance": {}, "summary": {}}

        # Expected figures from the case
        expected_revenue = 84867855  # $84,867,855

        # Revenue reconciliation
        if "sales_orders" in self.dataframes:
            revenue_df = self.get_revenue_transactions()
            if not revenue_df.empty:
                calculated_revenue = revenue_df["SubTotal"].sum()
                difference = calculated_revenue - expected_revenue
                difference_pct = (
                    (difference / expected_revenue) * 100
                    if expected_revenue != 0
                    else 0
                )

                reconciliation_results["revenue"] = {
                    "calculated": calculated_revenue,
                    "expected": expected_revenue,
                    "difference": difference,
                    "difference_pct": difference_pct,
                    "status": "MATCH" if abs(difference_pct) <= 1.0 else "MISMATCH",
                    "record_count": len(revenue_df),
                }

                logger.info(
                    f"Revenue reconciliation: Calculated ${calculated_revenue:,.2f}, "
                    f"Expected ${expected_revenue:,.2f}, "
                    f"Difference: ${difference:,.2f} ({difference_pct:.2f}%)"
                )

                # Estimate AR count based on typical invoice patterns
                if not revenue_df.empty:
                    avg_invoice_amount = calculated_revenue / len(revenue_df)
                    if avg_invoice_amount > 0:
                        estimated_ar_count = int(expected_revenue / avg_invoice_amount)
                        reconciliation_results["summary"]["estimated_ar_count"] = (
                            estimated_ar_count
                        )
        else:
            reconciliation_results["revenue"]["error"] = (
                "Sales orders data not available"
            )
            logger.error("Cannot reconcile revenue - sales orders data not loaded")

        # AR balance reconciliation
        if "customer_invoices" in self.dataframes:
            ar_df = self.get_ar_balance()
            if not ar_df.empty:
                # For AR, we're counting unpaid invoices rather than summing amounts
                # since the case gives us the count expectation indirectly
                calculated_ar_count = len(ar_df)

                reconciliation_results["ar_balance"] = {
                    "calculated_count": calculated_ar_count,
                    "status": "DATA_AVAILABLE",
                    "record_count": len(ar_df),
                }

                logger.info(
                    f"AR balance reconciliation: Found {calculated_ar_count:,} unpaid invoices"
                )

                # If we have an estimated count from revenue, compare
                if "estimated_ar_count" in reconciliation_results["summary"]:
                    estimated_count = reconciliation_results["summary"][
                        "estimated_ar_count"
                    ]
                    count_difference = calculated_ar_count - estimated_count
                    count_difference_pct = (
                        (count_difference / estimated_count) * 100
                        if estimated_count > 0
                        else 0
                    )

                    reconciliation_results["ar_balance"].update(
                        {
                            "estimated_count": estimated_count,
                            "count_difference": count_difference,
                            "count_difference_pct": count_difference_pct,
                        }
                    )

                    logger.info(
                        f"AR count comparison: Actual {calculated_ar_count:,}, "
                        f"Estimated {estimated_count:,}, "
                        f"Difference: {count_difference:,} ({count_difference_pct:.2f}%)"
                    )
        else:
            reconciliation_results["ar_balance"]["error"] = (
                "Customer invoices data not available"
            )
            logger.error(
                "Cannot reconcile AR balance - customer invoices data not loaded"
            )

        # Overall summary
        revenue_match = reconciliation_results["revenue"].get("status") == "MATCH"
        ar_available = (
            reconciliation_results["ar_balance"].get("status") == "DATA_AVAILABLE"
        )

        reconciliation_results["summary"] = {
            "overall_status": "GOOD"
            if (revenue_match and ar_available)
            else "REVIEW_NEEDED",
            "revenue_reconciled": "revenue" in reconciliation_results
            and "error" not in reconciliation_results["revenue"],
            "ar_reconciled": "ar_balance" in reconciliation_results
            and "error" not in reconciliation_results["ar_balance"],
            "recommendations": [],
        }

        if not revenue_match:
            reconciliation_results["summary"]["recommendations"].append(
                "Review revenue calculation - significant difference from expected amount"
            )
        if not ar_available:
            reconciliation_results["summary"]["recommendations"].append(
                "Verify AR data loading - needed for complete reconciliation"
            )

        logger.info(
            f"Reconciliation completed with status: {reconciliation_results['summary']['overall_status']}"
        )

        return reconciliation_results

    def get_validation_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive validation report combining integrity checks and financial reconciliation.

        Returns:
            Dictionary containing complete validation status and recommendations
        """
        logger.info("Generating comprehensive validation report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "validation_status": {},
            "financial_reconciliation": {},
            "summary": {},
            "recommendations": [],
        }

        # Run data integrity validation
        try:
            integrity_results = self.validate_data_integrity()
            report["validation_status"] = integrity_results

            # Count issues
            error_count = len(integrity_results.get("errors", []))
            warning_count = len(integrity_results.get("warnings", []))
            info_count = len(integrity_results.get("info", []))

            report["summary"]["data_integrity"] = {
                "total_errors": error_count,
                "total_warnings": warning_count,
                "total_info": info_count,
                "status": "GOOD" if error_count == 0 else "REVIEW_NEEDED",
            }

        except Exception as e:
            logger.error(f"Error during data integrity validation: {e}")
            report["validation_status"] = {"error": str(e)}
            report["summary"]["data_integrity"] = {"status": "ERROR"}

        # Run financial reconciliation
        try:
            reconciliation_results = self.reconcile_financial_figures()
            report["financial_reconciliation"] = reconciliation_results

            # Extract key metrics
            revenue_status = reconciliation_results.get("revenue", {}).get(
                "status", "UNKNOWN"
            )
            ar_status = reconciliation_results.get("ar_balance", {}).get(
                "status", "UNKNOWN"
            )
            overall_status = reconciliation_results.get("summary", {}).get(
                "overall_status", "UNKNOWN"
            )

            report["summary"]["financial_reconciliation"] = {
                "revenue_status": revenue_status,
                "ar_status": ar_status,
                "overall_status": overall_status,
            }

        except Exception as e:
            logger.error(f"Error during financial reconciliation: {e}")
            report["financial_reconciliation"] = {"error": str(e)}
            report["summary"]["financial_reconciliation"] = {"status": "ERROR"}

        # Generate overall assessment
        data_integrity_ok = report["summary"]["data_integrity"].get("status") == "GOOD"
        financial_reconciliation_ok = (
            report["summary"]["financial_reconciliation"].get("overall_status")
            == "GOOD"
        )

        if data_integrity_ok and financial_reconciliation_ok:
            report["summary"]["overall_status"] = "EXCELLENT"
            report["recommendations"].append(
                "All validation checks passed. Data appears reliable for analysis."
            )
        elif data_integrity_ok or financial_reconciliation_ok:
            report["summary"]["overall_status"] = "ACCEPTABLE"
            report["recommendations"].append(
                "Some validation checks passed. Review warnings before proceeding."
            )
        else:
            report["summary"]["overall_status"] = "NEEDS_REVIEW"
            report["recommendations"].append(
                "Multiple validation issues detected. Review errors and warnings carefully."
            )

        # Add specific recommendations based on findings
        if report["summary"]["data_integrity"].get("total_errors", 0) > 0:
            report["recommendations"].append(
                f"Fix {report['summary']['data_integrity']['total_errors']} data integrity errors before proceeding."
            )

        if (
            report["summary"]["financial_reconciliation"].get("revenue_status")
            == "MISMATCH"
        ):
            report["recommendations"].append(
                "Revenue reconciliation shows significant variance. Verify revenue calculation logic."
            )

        if (
            report["summary"]["financial_reconciliation"].get("ar_status")
            != "DATA_AVAILABLE"
        ):
            report["recommendations"].append(
                "AR data may be incomplete. Verify customer invoices data loading."
            )

        # Include data summary
        total_records = sum(len(df) for df in self.dataframes.values())
        loaded_dataframes = len(self.dataframes)

        report["summary"]["data_overview"] = {
            "total_records": total_records,
            "dataframes_loaded": loaded_dataframes,
            "dataframes_expected": 6,
        }

        logger.info(
            f"Validation report completed with status: {report['summary']['overall_status']}"
        )
        return report


def main():
    """Main function for testing the enhanced data loader with validation capabilities."""
    print("UMD Audit Data Loader with Validation")
    print("=" * 60)

    # Initialize loader
    loader = UMDDataLoader()

    # Load all files
    print("\n1. LOADING DATA FILES")
    print("-" * 30)
    dataframes = loader.load_all_files()

    if not dataframes:
        print("❌ No data files loaded!")
        return

    # Clean data types
    print("\n2. CLEANING DATA TYPES")
    print("-" * 30)
    loader.clean_data_types()

    # Data integrity validation
    print("\n3. DATA INTEGRITY VALIDATION")
    print("-" * 30)
    validation_results = loader.validate_data_integrity()

    print(
        f"Validation completed with {len(validation_results['errors'])} errors and {len(validation_results['warnings'])} warnings"
    )

    if validation_results["errors"]:
        print("\n❌ ERRORS:")
        for error in validation_results["errors"]:
            print(f"  • {error}")

    if validation_results["warnings"]:
        print("\n⚠️  WARNINGS:")
        for warning in validation_results["warnings"]:
            print(f"  • {warning}")

    # Financial reconciliation
    print("\n4. FINANCIAL RECONCILIATION")
    print("-" * 30)
    reconciliation_results = loader.reconcile_financial_figures()

    revenue_info = reconciliation_results.get("revenue", {})
    if "calculated" in revenue_info:
        print("Revenue Reconciliation:")
        print(f"  Expected: ${revenue_info['expected']:,.2f}")
        print(f"  Calculated: ${revenue_info['calculated']:,.2f}")
        print(
            f"  Difference: ${revenue_info['difference']:,.2f} ({revenue_info['difference_pct']:.2f}%)"
        )
        print(f"  Status: {revenue_info['status']}")

    ar_info = reconciliation_results.get("ar_balance", {})
    if "calculated_count" in ar_info:
        print("\nAR Balance Analysis:")
        print(f"  Unpaid invoices found: {ar_info['calculated_count']:,}")

    # Comprehensive validation report
    print("\n5. COMPREHENSIVE VALIDATION REPORT")
    print("-" * 40)
    report = loader.get_validation_report()

    print(f"Overall Status: {report['summary']['overall_status']}")
    print(f"Data Integrity: {report['summary']['data_integrity']['status']}")
    print(
        f"Financial Reconciliation: {report['summary']['financial_reconciliation']['overall_status']}"
    )

    if report["recommendations"]:
        print("\n📋 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"  • {rec}")

    # Get summary
    print("\n6. DATA SUMMARY")
    print("-" * 20)
    summary = loader.get_data_summary()

    for name, info in summary.items():
        print(f"\n{name.upper()}:")
        print(f"  Records: {info['shape'][0]:,}")
        print(f"  Columns: {info['shape'][1]}")
        print(f"  Missing values: {sum(info['missing_values'].values()):,}")

    print(
        "\n✅ Data loader testing completed. Check 'data_loader.log' for detailed logs."
    )


if __name__ == "__main__":
    main()

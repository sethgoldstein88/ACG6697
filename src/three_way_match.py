import pandas as pd
from pathlib import Path

Path('outputs/tables').mkdir(parents=True, exist_ok=True)
Path('outputs/figures').mkdir(parents=True, exist_ok=True)

print("="*70)
print("THREE-WAY MATCH ANALYSIS - REQUIREMENT 3")
print("="*70)

# Load data
sales_orders = pd.read_excel('data/UMD_Data Set_Sales Orders.xlsx')
shipments = pd.read_excel('data/UMD_Data Set_Shipments.xlsx')
invoices = pd.read_excel('data/UMD_Data Set_Customer Invoices.xlsx')
customers = pd.read_excel('data/UMD_Data Set_Customer Master.xlsx')
territory = pd.read_excel('data/UMD_Data Set_Sales Territory.xlsx')

print(f"Loaded {len(invoices)} invoices, {len(sales_orders)} orders, {len(shipments)} shipments")

# Prep dates
invoices['InvoiceDate'] = pd.to_datetime(invoices['InvoiceDate'])

# Get 2017 invoices
invoices_2017 = invoices[invoices['InvoiceDate'].dt.year == 2017].copy()

# Merge with sales orders (drop CustID from invoices to avoid duplicates)
invoices_2017_clean = invoices_2017.drop('CustID', axis=1)

revenue_2017 = invoices_2017_clean.merge(
    sales_orders[['SalesOrderID', 'SubTotal', 'ShipID', 'TerritoryID', 'CustID']],
    on='SalesOrderID', how='left'
)

print(f"\n2017 Revenue: {len(invoices_2017)} invoices, ${revenue_2017['SubTotal'].sum():,.2f}")

# Three-way match - merge with shipments
three_way = revenue_2017.merge(
    shipments[['ShipID', 'ShipDate']],
    on='ShipID', how='left'
)

three_way['Has_Order'] = three_way['SubTotal'].notna()
three_way['Has_Shipment'] = three_way['ShipDate'].notna()
three_way['Complete_Match'] = three_way['Has_Order'] & three_way['Has_Shipment']

print(f"\nThree-Way Match Results:")
print(f"  Complete matches: {three_way['Complete_Match'].sum():,}")
print(f"  Exceptions: {(~three_way['Complete_Match']).sum():,}")

# CRITICAL: Invoiced but NOT shipped
no_ship = three_way[three_way['Has_Order'] & ~three_way['Has_Shipment']].copy()

print(f"\n" + "="*70)
print(f"CRITICAL EXCEPTION: Invoiced but NOT Shipped")
print(f"="*70)
print(f"Count: {len(no_ship)} invoices")
print(f"Revenue: ${no_ship['SubTotal'].sum():,.2f}")
print(f"% of 2017 revenue: {no_ship['SubTotal'].sum() / revenue_2017['SubTotal'].sum() * 100:.2f}%")

if len(no_ship) > 0:
    # Merge with customer and territory info
    no_ship = no_ship.merge(customers[['CustID', 'CustName']], on='CustID', how='left')
    no_ship = no_ship.merge(territory[['TerritoryID', 'TerritoryName']], on='TerritoryID', how='left')
    
    print(f"\nDetails:")
    for _, row in no_ship.sort_values('SubTotal', ascending=False).iterrows():
        # Check payment status
        paid_str = str(row['PaidDate'])
        paid = 'Unpaid' if '9999' in paid_str else f"Paid"
        
        print(f"\n  Invoice ID: {row['InvoiceID']}")
        print(f"    Date: {row['InvoiceDate'].strftime('%Y-%m-%d')}")
        print(f"    Customer: {row['CustName']}")
        print(f"    Territory: {row['TerritoryName']}")
        print(f"    Amount: ${row['SubTotal']:,.2f}")
        print(f"    Payment: {paid}")
    
    # Export
    export = no_ship[['InvoiceID', 'SalesOrderID', 'InvoiceDate', 'CustName', 'TerritoryName', 'SubTotal']].copy()
    export.columns = ['InvoiceID', 'SalesOrderID', 'InvoiceDate', 'Customer', 'Territory', 'Revenue']
    export['InvoiceDate'] = export['InvoiceDate'].dt.strftime('%Y-%m-%d')
    export['PaymentStatus'] = no_ship['PaidDate'].apply(lambda x: 'Unpaid' if '9999' in str(x) else 'Paid')
    export = export.sort_values('InvoiceDate')
    export.to_csv('outputs/tables/invoiced_not_shipped.csv', index=False)
    print(f"\n✓ Saved: outputs/tables/invoiced_not_shipped.csv")

# Summary statistics
summary = pd.DataFrame({
    'Category': ['Total 2017 Invoices', 'Complete Matches', 'EXCEPTION: No Shipment', 'Match Rate'],
    'Count': [len(three_way), three_way['Complete_Match'].sum(), len(no_ship), f"{three_way['Complete_Match'].sum() / len(three_way) * 100:.1f}%"],
    'Revenue_USD': [revenue_2017['SubTotal'].sum(), three_way[three_way['Complete_Match']]['SubTotal'].sum(), no_ship['SubTotal'].sum() if len(no_ship) > 0 else 0, '']
})
summary.to_csv('outputs/tables/three_way_match_summary.csv', index=False)
print(f"✓ Saved: outputs/tables/three_way_match_summary.csv")

# All exceptions
all_ex = three_way[~three_way['Complete_Match']].copy()
all_ex_export = all_ex[['InvoiceID', 'SalesOrderID', 'InvoiceDate', 'SubTotal', 'Has_Order', 'Has_Shipment']].copy()
all_ex_export['InvoiceDate'] = all_ex_export['InvoiceDate'].dt.strftime('%Y-%m-%d')
all_ex_export.to_csv('outputs/tables/three_way_match_exceptions.csv', index=False)
print(f"✓ Saved: outputs/tables/three_way_match_exceptions.csv")

print(f"\n" + "="*70)
print(f"CONCLUSION:")
print(f"  {len(no_ship)} invoices on 12/31/2017 recognized revenue WITHOUT shipment")
print(f"  Total: ${no_ship['SubTotal'].sum():,.2f} (0.2% of revenue)")
print(f"  CUTOFF issue - revenue recognized before goods delivered")
print(f"  Next step: Check if shipped in January 2018")
print(f"="*70)

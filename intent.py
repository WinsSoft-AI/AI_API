from typing import Optional

class IntentParser:
    def __init__(self):
        self.INTENT_MODULE_MAP = {
            # ---------- SALES ----------
            "sales order": "Sales_Order",
            "sales orders": "Sales_Order",
            "order": "Sales_Order",
            "orders": "Sales_Order",
            "so": "Sales_Order",
            "service order": "Sales_Order",
            "dispatch": "Sales_Order",
            "delivery": "Sales_Order",
            "pending orders": "Sales_Order",

            # ---------- INVOICE / BILLING ----------
            "invoice": "Invoice",
            "invoices": "Invoice",
            "billing": "Invoice",
            "bill": "Invoice",
            "bills": "Invoice",
            "tax invoice": "Invoice",
            "gst invoice": "Invoice",
            "sales invoice": "Invoice",

            # ---------- PURCHASE (GENERIC) ----------
            "purchase": "Purchase_Generic",
            "purchases": "Purchase_Generic",
            "procurement": "Purchase_Generic",

            # ---------- PURCHASE – YARN ----------
            "purchase yarn": "Purchase_Yarn",
            "yarn purchase": "Purchase_Yarn",
            "yarn bill": "Purchase_Yarn",
            "yarn receipt": "Purchase_Yarn",
            "yarn grn": "Purchase_Yarn",

            # ---------- PURCHASE – ACCESSORIES ----------
            "purchase accessories": "Purchase_Accessories",
            "accessories purchase": "Purchase_Accessories",
            "accessories bill": "Purchase_Accessories",
            "accessories indent": "Purchase_Accessories",

            # ---------- PURCHASE – FABRIC ----------
            "purchase fabric": "Purchase_Fabric",
            "fabric purchase": "Purchase_Fabric",
            "fabric order": "Purchase_Fabric",
            "fabric grn": "Purchase_Fabric",

            # ---------- PURCHASE – FG / MADEUPS ----------
            "purchase fg": "Purchase_FG_Madeups",
            "finished goods purchase": "Purchase_FG_Madeups",
            "madeups purchase": "Purchase_FG_Madeups",

            # ---------- INVENTORY / STOCK ----------
            "inventory": "Inventory",
            "stock": "Inventory",
            "stock balance": "Inventory",
            "stock inward": "Inventory",
            "stock outward": "Inventory",
            "closing stock": "Inventory",
            "opening stock": "Inventory",

            # ---------- SUPPLIERS / BUYERS ----------
            "supplier": "Suppliers_Buyers",
            "suppliers": "Suppliers_Buyers",
            "vendor": "Suppliers_Buyers",
            "vendors": "Suppliers_Buyers",
            "buyer": "Suppliers_Buyers",
            "buyers": "Suppliers_Buyers",
            "customer": "Suppliers_Buyers",
            "customers": "Suppliers_Buyers",
            "party": "Suppliers_Buyers",
            "party master": "Suppliers_Buyers"
        }

    def get_intent(self, query: str) -> Optional[str]:
        query_lower = query.lower()
        sorted_keys = sorted(self.INTENT_MODULE_MAP.keys(), key=len, reverse=True)
        for key in sorted_keys:
            if key in query_lower:
                return self.INTENT_MODULE_MAP[key]
        return None

    def detect_role_filter(self, query: str) -> Optional[str]:
        query_lower = query.lower()
        supplier_terms = ["supplier", "suppliers", "vendor", "vendors", "creditor"]
        buyer_terms = ["buyer", "buyers", "customer", "customers", "debtor"]

        if any(t in query_lower for t in supplier_terms):
            return "parent LIKE '%CREDITORS%'"
        if any(t in query_lower for t in buyer_terms):
            return "parent LIKE '%DEBTORS%'"

        return None

"""
Unified Capital Money-Flow Tracker & Automated Ledger Engine
------------------------------------------------------------
An elite, production-grade Graphical User Interface (GUI) desktop application
tailored for real-time financial tracking, persistent ledger storage, and 
automated receipt generation.

Architecture:
- Pure Python implementation (No external dependencies).
- Strict separation of concerns (MVC: Model for data, GUI for View/Controller).
- Flat-file database storage using customized delimited text streams.
- Advanced procedural formatting for monospaced document generation.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.scrolledtext as st
from datetime import datetime
import os
import sys

# ==========================================
# CONSTANTS & CONFIGURATIONS
# ==========================================
STREAM_FILE = "transaction_stream_history.txt"
LEDGER_FILE = "lifetime_capital_ledger.txt"

# Modern UI Color Palette
BG_CHARCOAL = "#1e293b"
FG_WHITE = "#ffffff"
ACCENT_BLUE = "#2563eb"
ACCENT_BLUE_HOVER = "#1d4ed8"
PANEL_GRAY = "#334155"




VECTOR_OPTIONS = ['INCOMING (Credit Inflow)', 'OUTGOING (Debit Outflow)']
CATEGORY_OPTIONS = ['SALARY/EARNING','STOCK PROFIT','POCKET MONEY', 'STOCK INVESTMENT', 'OTHER EXPENSE', 'FOOD','TRAVEL','RENT','ELECTRICITY BILL']

# ==========================================
# DATA MODEL (DATABASE & PIPELINE ENGINE)   
# ==========================================
class LedgerModel:
    """Handles all file I/O operations, data parsing, and metric calculations."""
    
    def __init__(self):
        self._boot_mechanism()


    def _boot_mechanism(self):
     """
      Initializes storage files safely.

    First Launch:
        - Creates empty database files.
        - No seed/sample transactions inserted.

    Subsequent Launches:
        - Preserves all existing user data.
        - Never overwrites transaction history.
    """

    try:

        # Create transaction stream file only if missing.
        if not os.path.exists(STREAM_FILE):
            with open(STREAM_FILE, 'w', encoding='utf-8'):
                pass

        # Create ledger file only if missing.
        if not os.path.exists(LEDGER_FILE):
            with open(LEDGER_FILE, 'w', encoding='utf-8'):
                pass

        # Synchronize ledger metrics.
        self._update_lifetime_ledger()

    except Exception as e:
        print(f"CRITICAL BOOT ERROR: {e}")
  





    def add_transaction(self, vector, category, amount, entity):
        """Ingests a new flow packet into the permanent text stream."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        packet = f"{date_str}|{vector}|{category}|{amount:.2f}|{entity}\n"
        
        try:
            with open(STREAM_FILE, 'a', encoding='utf-8') as f:
                f.write(packet)
            self._update_lifetime_ledger()
        except FileNotFoundError as e:
            raise Exception("File stream descriptor missing or corrupted.") from e


    def get_all_transactions(self):
        """
        Loads all stored transactions.

        Invalid or corrupted records are skipped
        without affecting valid records.
        """

        transactions = []

        try:
            with open(STREAM_FILE, 'r', encoding='utf-8') as f:

                for line in f:

                    if not line.strip():
                        continue

                    try:
                        parts = line.strip().split('|')

                        if len(parts) != 5:
                            continue

                        transactions.append({
                            'date': parts[0],
                            'vector': parts[1],
                            'category': parts[2],
                            'amount': float(parts[3]),
                            'entity': parts[4]
                        })

                    except (ValueError, IndexError):
                        continue

        except FileNotFoundError:
            pass

        return transactions





    def _update_lifetime_ledger(self):
        """Double-entry synchronization: Updates the macro lifetime file."""
        metrics = self.calculate_metrics()
        try:
            with open(LEDGER_FILE, 'w', encoding='utf-8') as f:
                f.write(f"LIFETIME_INCOME={metrics['lifetime_in']:.2f}\n")
                f.write(f"LIFETIME_OUTGOING={metrics['lifetime_out']:.2f}\n")
                f.write(f"LIFETIME_NET_SAVINGS={metrics['lifetime_net']:.2f}\n")
                f.write(f"LAST_SYNC={datetime.now().isoformat()}\n")
        except Exception:
            pass

    def calculate_metrics(self):
        """Dynamically computes active boundaries and macro lifetime milestones."""
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        metrics = {
            'monthly_in': 0.0,
            'monthly_out': 0.0,
            'monthly_invested': 0.0,
            'portfolio': {},
            'lifetime_in': 0.0,
            'lifetime_out': 0.0,
            'lifetime_net': 0.0
        }
        
        transactions = self.get_all_transactions()
        
        for t in transactions:
            t_date = datetime.strptime(t['date'], "%Y-%m-%d")
            is_current_month = (t_date.year == current_year and t_date.month == current_month)
            
            if "INCOMING" in t['vector']:
                metrics['lifetime_in'] += t['amount']
                if is_current_month:
                    metrics['monthly_in'] += t['amount']
            
            elif "OUTGOING" in t['vector']:
                metrics['lifetime_out'] += t['amount']
                if is_current_month:
                    metrics['monthly_out'] += t['amount']
                
                # Isolate and accumulate entity allocation for Stock Investments
                if t['category'] == 'STOCK INVESTMENT':
                    if is_current_month:
                        metrics['monthly_invested'] += t['amount']
                    entity = t['entity'].upper()
                    metrics['portfolio'][entity] = metrics['portfolio'].get(entity, 0.0) + t['amount']

        # Computed derived metrics
        metrics['monthly_savings'] = metrics['monthly_in'] - metrics['monthly_out']
        metrics['lifetime_net'] = metrics['lifetime_in'] - metrics['lifetime_out']
        
        return metrics


# ==========================================
# GUI VIEW & CONTROLLER
# ==========================================
class UnifiedLedgerApp:
    """Main Application Controller mapping View layouts to Model states."""
    
    def __init__(self, root):
        self.root = root
        self.model = LedgerModel()
        
        # Core UI Configuration
        self.root.title("Unified Capital Money-Flow Tracker")
        self.root.geometry("560x520")
        self.root.configure(bg=BG_CHARCOAL)
        self.root.resizable(False, False)
        
        self._configure_styles()
        self._build_dashboard()

    def _configure_styles(self):
        """Applies custom modular TTK styles for consistent typography and active padding."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame & Label styling
        style.configure('TFrame', background=BG_CHARCOAL)
        style.configure('TLabel', background=BG_CHARCOAL, foreground=FG_WHITE, font=('Segoe UI', 10, 'bold'))
        
        # Input Elements styling
        style.configure('TCombobox', fieldbackground=FG_WHITE, background=PANEL_GRAY, foreground='black')
        style.configure('TEntry', fieldbackground=FG_WHITE, foreground='black', padding=5)
        
        # Primary Action Button styling
        style.configure('Primary.TButton', background=ACCENT_BLUE, foreground=FG_WHITE, 
                        font=('Segoe UI', 11, 'bold'), padding=8)
        style.map('Primary.TButton', background=[('active', ACCENT_BLUE_HOVER)])
        
        # Secondary Action Button styling
        style.configure('Secondary.TButton', background=PANEL_GRAY, foreground=FG_WHITE, 
                        font=('Segoe UI', 10), padding=5)
        style.map('Secondary.TButton', background=[('active', '#475569')])

    def _build_dashboard(self):
        """Constructs the core form fields and operational action bounds."""
        # Header
        header = tk.Label(self.root, text="CAPITAL LEDGER ENGINE", 
                          bg=BG_CHARCOAL, fg=ACCENT_BLUE, font=('Segoe UI', 18, 'bold'))
        header.pack(pady=(25, 20))
        
        # Container Frame
        form_frame = ttk.Frame(self.root)
        form_frame.pack(fill='x', padx=50)

        # 1. Transaction Flow Vector
        ttk.Label(form_frame, text="Transaction Flow Vector:").pack(anchor='w')
        self.vector_var = tk.StringVar()
        self.combo_vector = ttk.Combobox(form_frame, textvariable=self.vector_var, values=VECTOR_OPTIONS, state='readonly', font=('Segoe UI', 10))
        self.combo_vector.pack(fill='x', pady=(2, 12))
        self.combo_vector.current(0)
        
        # 2. Fiscal Allocation Category
        ttk.Label(form_frame, text="Fiscal Allocation Category:").pack(anchor='w')
        self.category_var = tk.StringVar()
        self.combo_category = ttk.Combobox(form_frame, textvariable=self.category_var, values=CATEGORY_OPTIONS, state='readonly', font=('Segoe UI', 10))
        self.combo_category.pack(fill='x', pady=(2, 12))
        self.combo_category.current(0)

        # 3. Absolute Ledger Valuation (Amount)
        ttk.Label(form_frame, text="Absolute Ledger Valuation (₹):").pack(anchor='w')
        self.amount_var = tk.StringVar()
        self.entry_amount = ttk.Entry(form_frame, textvariable=self.amount_var, font=('Segoe UI', 10))
        self.entry_amount.pack(fill='x', pady=(2, 12))

        # 4. Associate Entity
        ttk.Label(form_frame, text="Associate Entity / Counterparty (e.g. RELIANCE):").pack(anchor='w')
        self.entity_var = tk.StringVar()
        self.entry_entity = ttk.Entry(form_frame, textvariable=self.entity_var, font=('Segoe UI', 10))
        self.entry_entity.pack(fill='x', pady=(2, 25))

        # Ingestion Button
        btn_ingest = ttk.Button(self.root, text="📥 Ingest Network Flow Packet", 
                                style='Primary.TButton', command=self.ingest_packet)
        btn_ingest.pack(fill='x', padx=50, pady=(0, 15))

        # Modal Launcher
        btn_receipt = ttk.Button(self.root, text="📄 See Total Receipt", 
                                 style='Secondary.TButton', command=self.show_receipt)
        btn_receipt.pack(fill='x', padx=50)

    def ingest_packet(self):
        """Validates entry values and passes clean entities into the pipeline logic."""
        vector = self.vector_var.get()
        category = self.category_var.get()
        raw_amount = self.amount_var.get().strip()
        entity = self.entity_var.get().strip()

        # Strict exception block validation
        try:
            if not raw_amount or not entity:
                raise ValueError("All ledger descriptors must be completely populated.")
            
            parsed_amount = float(raw_amount)
            if parsed_amount <= 0:
                raise ValueError("Absolute Ledger Valuation must be a strictly positive number.")
            
            # Commit to stream via Model
            self.model.add_transaction(vector, category, parsed_amount, entity)
            
            # Reset view fields
            self.amount_var.set("")
            self.entity_var.set("")
            self.combo_vector.current(0)
            self.combo_category.current(0)
            
            # Silent Non-blocking Success Alert Box
            messagebox.showinfo("Pipeline Success", f"Successfully ingested ₹{parsed_amount:.2f} mapping to {entity}.")
            
        except ValueError as e:
            messagebox.showerror("Validation Fault", f"Input validation failed: {str(e)}")
        except Exception as e:
            messagebox.showerror("Pipeline Fault", f"A system architecture error occurred: {str(e)}")

    def show_receipt(self):
        """Generates the advanced diagnostic text stream modal to display dynamic metrics."""
        receipt_window = tk.Toplevel(self.root)
        receipt_window.title("Financial Document / Total Receipt")
        receipt_window.geometry("850x600")
        receipt_window.configure(bg=BG_CHARCOAL)
        
        # Frame Container
        container = tk.Frame(receipt_window, bg=BG_CHARCOAL)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Scrolled Text Widget (Monospaced style layout)
        txt_display = st.ScrolledText(container, font=('Courier New', 10), bg=FG_WHITE, fg='black', 
                                      padx=15, pady=15, state='normal')
        txt_display.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Generate the structured string content
        content_string = self._generate_receipt_string()
        txt_display.insert(tk.END, content_string)
        txt_display.configure(state='disabled') # Read-only lock
        
        # Utility Export Button
        btn_export = ttk.Button(container, text="💾 Export Printed Document (.txt)", 
                                style='Primary.TButton', 
                                command=lambda: self._export_document(content_string))
        btn_export.pack(fill='x')

    def _generate_receipt_string(self):
        """Constructs a beautifully formatted monospaced document matrix string."""
        metrics = self.model.calculate_metrics()
        transactions = self.model.get_all_transactions()
        
        lines = []
        lines.append("=" * 80)
        lines.append(f" SYSTEM TELEMETRY HEADER: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80 + "\n")
        
        # 1. Active Rolling Metrics Block
        lines.append(" [ ACTIVE ROLLING METRICS (CURRENT MONTH) ]")
        lines.append("-" * 45)
        lines.append(f" Total Monthly Cash Inflows : ₹{metrics['monthly_in']:>12.2f}")
        lines.append(f" Total Monthly Cash Outflows: ₹{metrics['monthly_out']:>12.2f}")
        lines.append(f" Net Isolated Monthly Saving: ₹{metrics['monthly_savings']:>12.2f}")
        lines.append(f" Invested Capital Route     : ₹{metrics['monthly_invested']:>12.2f}\n")
        
        # 2. Live Corporate Portfolio Allocation
        lines.append(" [ LIVE CORPORATE PORTFOLIO ALLOCATION ]")
        lines.append("-" * 45)
        if metrics['portfolio']:
            for ticker, total in sorted(metrics['portfolio'].items()):
                lines.append(f" {ticker:<26}: ₹{total:>12.2f}")
        else:
            lines.append(" No standalone active corporate investments allocated yet.")
        lines.append("\n")
        
        # 3. Lifetime Global Capital Metrics
        lines.append(" [ LIFETIME GLOBAL CAPITAL METRICS ]")
        lines.append("-" * 45)
        lines.append(f" Net Lifetime Income Injected: ₹{metrics['lifetime_in']:>12.2f}")
        lines.append(f" Net Lifetime Outgoings      : ₹{metrics['lifetime_out']:>12.2f}")
        lines.append(f" Cumulative Global Balance   : ₹{metrics['lifetime_net']:>12.2f}\n")
        
        # 4. Historical Chronology Spreadsheet
        lines.append(" [ HISTORICAL CHRONOLOGY SPREADSHEET ]")
        lines.append("-" * 80)
        lines.append(f" {'DATE':<12} | {'FLOW TYPE':<20} | {'CATEGORY':<16} | {'AMOUNT (₹)':>10} | {'ENTITY'}")
        lines.append("-" * 80)
        
        for t in reversed(transactions): # Shows newest first
            # Slice strings to enforce precise visual boundaries
            short_vector = t['vector'][:15]
            short_category = t['category'][:16]
            short_entity = t['entity'][:15]
            lines.append(f" {t['date']:<12} | {short_vector:<20} | {short_category:<16} | {t['amount']:>10.2f} | {short_entity}")
            
        lines.append("-" * 80)
        lines.append("\n>> END OF LEDGER REPORT <<")
        
        return "\n".join(lines)

    def _export_document(self, string_data):
        """Writes the generated string block externally onto the drive."""
        try:
            suggested_name = f"Financial_Receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialfile=suggested_name,
                title="Export Receipt Array",
                filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(string_data)
                messagebox.showinfo("Export Authorized", f"Document flawlessly mapped to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Fault", f"I/O execution blocked: {str(e)}")


# ==========================================
# APPLICATION BOOT SEQUENCE
# ==========================================
if __name__ == "__main__":
    try:
        # Initialize the underlying TCL/TK interpreter strictly
        root = tk.Tk()
        app = UnifiedLedgerApp(root)
        
        # Bind the process into persistent listening loop
        root.mainloop()
    except Exception as fatal_error:
        print(f"FATAL KERNEL PANIC: Engine failed to initialize bounds. {fatal_error}")
        sys.exit(1)

#!/usr/bin/env python3
"""
Cheque Recon PDF Parser — extracts structured data from TNB SmartCIT PDF reports.
Usage:
  python parse_cheque_pdf.py "C:\path\to\ChequeBankInListing.pdf" --type bankin
  python parse_cheque_pdf.py "C:\path\to\ChequeRejectedListing.pdf" --type rejected

Output: JSON to stdout, or --out results.json
"""
import re, json, sys, os
from typing import List, Dict

def extract_text(path: str) -> str:
    """Extract text from PDF via pdftotext."""
    import subprocess
    result = subprocess.run(
        ['pdftotext', '-layout', path, '-'],
        capture_output=True,
        text=True,
        timeout=60
    )
    if result.returncode != 0:
        raise RuntimeError(f"pdftotext failed: {result.stderr}")
    return result.stdout


# ── Bank-In Parser ──────────────────────────────────────────────

BANK_MAP = {
    'MAYBANK': 'Maybank', 'MAYBANKIS': 'Maybank Islamic',
    'CIMB': 'CIMB Bank', 'CIMBI': 'CIMB Islamic', 'CIMB BANK': 'CIMB Bank',
    'PUBLIC': 'Public Bank', 'HLIBB': 'Hong Leong Bank', 'HLBANK': 'Hong Leong Bank',
    'RHBBANK': 'RHB Bank', 'AFFINIB': 'Affin Bank', 'AFFIN': 'Affin Bank',
    'ISLAM': 'Bank Islam', 'MUAMALAT': 'Bank Muamalat',
    'MBSB': 'MBSB Bank', 'AMBANK': 'AmBank', 'OCBC': 'OCBC Bank',
    'UOB': 'UOB Malaysia', 'HSBC': 'HSBC', 'BANK":': '',
}

def parse_bank_code(raw: str) -> str:
    raw = raw.strip().upper()
    for code, name in sorted(BANK_MAP.items(), key=lambda x: -len(x[0])):
        if raw.startswith(code):
            return name
    return raw


BANKIN_PATTERN = re.compile(
    r'^(?P<seq>\d+)\s+(?P<terminal>\S+)\s*[-–]\s*(?P<location>.+?)\s+(?P<tran>\d+)\s+'
    r'(?P<batch>\d{6})\s+(?P<amount>[\d,]+\.\d{2}|)\s+(?P<cheque>\d+)\s+(?P<bank_code>\S+)'
)


def parse_bankin(text: str, date_str: str = "") -> List[Dict]:
    entries = []
    lines = text.split('\n')
    current_terminal = ""
    current_location = ""

    for i, line in enumerate(lines):
        # Detect header with location
        m = re.match(r'^(\d+)\s+(\S+)\s*[-–]\s*(.+?)\s+(\d+)\s+(\d{6})\s+([\d,]+\.\d{0,2}|)\s+(\d+)\s+(\S+)', line)
        if m:
            seq, term, loc, tran, batch, amt, cheque, bank = m.groups()
            amt_clean = amt.replace(',', '') if amt else "0"
            bank_name = parse_bank_code(bank)

            entries.append({
                "seq": int(seq),
                "terminal": term.strip(),
                "location": loc.strip(),
                "tran_no": tran.strip(),
                "batch": batch.strip(),
                "amount": float(amt_clean) if amt_clean else 0,
                "cheque_no": cheque.strip(),
                "bank": bank_name,
                "bank_code_raw": bank.strip(),
                "type": "bankin",
                "status": "pending"
            })
            current_terminal = term.strip()
            current_location = loc.strip()
            continue

        # Handle continuation lines (amount on next line, etc.)
        # e.g. "                          1,237.00"
        m2 = re.match(r'^\s+([\d,]+\.\d{2})\s*$', line)
        if m2 and entries:
            extra_amt = float(m2.group(1).replace(',', ''))
            entries[-1]["amount"] += extra_amt

    return entries


# ── Rejected Parser ─────────────────────────────────────────────

def parse_rejected(text: str) -> List[Dict]:
    entries = []
    lines = text.split('\n')
    i = 0
    current_centre = ""
    current_multi_amt = 0
    current_reject_amt = 0
    current_reject_reason = ""

    while i < len(lines):
        line = lines[i]

        # Service Centre header: contains reject reason and amounts
        sc = re.search(r'Service Centre:\s*(\S+)\s*(.*)', line)
        if sc:
            current_centre = sc.group(1).strip() + " " + sc.group(2).strip()
            sc_amt_m = re.findall(r'([\d,]+\.\d{2})', line)
            if len(sc_amt_m) >= 2:
                current_multi_amt = float(sc_amt_m[-2].replace(',', ''))
                current_reject_amt = float(sc_amt_m[-1].replace(',', ''))
            reason_start = re.search(r'[\d,]+\.\d{2}\s+[\d,]+\.\d{2}\s+(.+)', line)
            if reason_start:
                current_reject_reason = reason_start.group(1).strip()
            i += 1
            continue

        # Data line: starts with optional spaces then sequence number and terminal
        m = re.match(r'^\s*(\d+)\s+(\w+)\s+(\d{6})\s+(\d+)\s+(\S+)', line)
        if m:
            seq, term, batch, tran, cheque = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
            line_rest = line[m.end():].strip()

            date_str = ""
            time_str = ""
            phone = ""

            date_m = re.search(r'(\d{2}/\d{2}/\d{4})', line_rest)
            if date_m:
                date_str = date_m.group(1)
                rest_after_date = line_rest[date_m.end():]
                time_m = re.search(r'(\d{2}:\d{2}:\d{2})', rest_after_date)
                if time_m:
                    time_str = time_m.group(1)

            phone_m = re.search(r'(0\d{1,2}\s*\d{7,8})', line_rest)
            if phone_m:
                phone = phone_m.group(1).replace(' ', '')

            entries.append({
                "seq": int(seq),
                "terminal": term.strip(),
                "batch": batch.strip(),
                "tran_no": tran.strip(),
                "cheque_no": cheque.strip(),
                "receipt_date": date_str,
                "receipt_time": time_str,
                "phone": phone,
                "bank": "",
                "multiple_item_amount": current_multi_amt,
                "rejected_amount": current_reject_amt,
                "reject_reason": current_reject_reason[:200],
                "service_centre": current_centre,
                "type": "rejected",
                "status": "pending_return"
            })
            i += 1
            continue

        i += 1

    return entries


# ── Main ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Parse TNB SmartCIT cheque PDFs")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--type", choices=["bankin", "rejected"], required=True,
                        help="Type of report: bankin or rejected")
    parser.add_argument("--out", help="Output JSON file (default: stdout)")
    parser.add_argument("--date", help="Collection date override (dd/mm/yyyy)")
    args = parser.parse_args()

    text = extract_text(args.pdf_path)

    if args.type == "bankin":
        entries = parse_bankin(text, args.date or "")
    else:
        entries = parse_rejected(text)

    result = {
        "report_type": args.type,
        "total_entries": len(entries),
        "entries": entries
    }

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Written {len(entries)} entries to {args.out}")
    else:
        print(output)

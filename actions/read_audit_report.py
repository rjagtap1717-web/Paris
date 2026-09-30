import json
from pathlib import Path

def read_audit_report(parameters: dict, player=None, session_memory=None) -> str:
    report_file = Path("logs/audit_report.json")
    
    if not report_file.exists():
        return "No audit report found. The nightly auditor has not run yet."
        
    try:
        with open(report_file, "r", encoding="utf-8") as f:
            report = json.load(f)
            
        findings = report.get("findings", [])
        if not findings:
            return "The nightly audit ran but found 0 issues. The codebase is clean!"
            
        # Tally the buckets
        critical = sum(1 for item in findings if item.get("severity") == "CRITICAL")
        medium = sum(1 for item in findings if item.get("severity") == "MEDIUM")
        low = sum(1 for item in findings if item.get("severity") == "LOW")
        
        auto_fix = sum(1 for item in findings if item.get("resolution_track") == "AUTO_FIXABLE")
        pair_prog = sum(1 for item in findings if item.get("resolution_track") == "PAIR_PROGRAMMING")
        
        # Build the summary
        summary = (
            f"Nightly Audit Summary (Audited {len(report.get('files_audited', []))} files):\n"
            f"- Critical: {critical}\n"
            f"- Medium: {medium}\n"
            f"- Low: {low}\n\n"
            f"Resolution Tracks:\n"
            f"- Auto-Fixable (Antigravity): {auto_fix}\n"
            f"- Pair Programming (Human needed): {pair_prog}\n\n"
        )
        
        # Detail the criticals or auto-fixables if asked, but default to a high-level summary to prevent token bloat
        detail_level = parameters.get("detail", "summary")
        if detail_level == "full":
            summary += "--- DETAILED FINDINGS ---\n"
            for idx, item in enumerate(findings, 1):
                summary += f"\n{idx}. [{item.get('severity')}] [{item.get('resolution_track')}] in {item.get('file')}\n"
                summary += f"   Issue: {item.get('issue')}\n"
                summary += f"   Recommendation: {item.get('ai_recommendation')}\n"
                
        else:
            summary += "(Call this tool again with detail='full' to read the specific recommendations.)"
            
        if player:
            player.write_log("SYS: Read audit report successfully.")
            
        from core.response_limiter import truncate_response
        return truncate_response(summary, max_chars=4000, escape_hint="Call read_audit_report again with detail='summary' if it is too long.")
        
    except Exception as e:
        return f"Error reading the audit report: {e}"

# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "read_audit_report",
    "scope": "local",
    "description": "Reads the overnight AI Audit Report which contains bugs, refactor suggestions, and unused code. Use this tool when giving the user a morning briefing, or when the user asks about system health, testing, or audits.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "detail": {
                "type": "STRING",
                "description": "'summary' (default) for a quick overview of counts, or 'full' to read all detailed issues."
            }
        }
    },
    "handler": read_audit_report,
}

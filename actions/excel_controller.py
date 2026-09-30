import time

try:
    import win32com.client
    import pythoncom
    _WIN32 = True
except ImportError:
    _WIN32 = False

def excel_controller(parameters: dict, response=None, player=None, session_memory=None) -> str:
    if not _WIN32:
        return "win32com is not installed. Cannot natively control Excel."

    action = parameters.get("action", "").lower()
    cell = parameters.get("cell", "")
    value = parameters.get("value", "")
    formatting = parameters.get("formatting", {})
    file_path = parameters.get("file_path", "")
    
    try:
        pythoncom.CoInitialize()
        
        # Connect to existing Excel or launch a new one
        try:
            excel = win32com.client.GetActiveObject("Excel.Application")
        except Exception:
            if action in ["new", "open"]:
                excel = win32com.client.Dispatch("Excel.Application")
                excel.Visible = True
            else:
                return "Microsoft Excel is not currently open on the computer. Please use action 'new' first."
                
        wb = excel.ActiveWorkbook if excel.Workbooks.Count > 0 else None
        
        if action == "new":
            wb = excel.Workbooks.Add()
            excel.Visible = True
            wb.Activate()
            return "Created new Excel workbook. Excel is now open and active."
            
        if not wb:
            return "Microsoft Excel is open, but there is no active workbook. Use action 'new'."
            
        sheet = wb.ActiveSheet
        
        if action == "write_cell":
            if not cell: 
                return "Please provide a 'cell' (e.g. 'A1')."
            rng = sheet.Range(cell)
            rng.Value = value
            
            if formatting:
                if "bold" in formatting: rng.Font.Bold = formatting["bold"]
                if "italic" in formatting: rng.Font.Italic = formatting["italic"]
                if "number_format" in formatting: rng.NumberFormat = formatting["number_format"]
            return f"Wrote value to cell {cell}."
            
        elif action == "read_cell":
            if not cell: 
                return "Please provide a 'cell' (e.g. 'B2')."
            val = sheet.Range(cell).Value
            return f"Cell {cell} contains: {val}"
            
        elif action == "read_range":
            if not cell: 
                return "Please provide a 'cell' range (e.g. 'A1:C10')."
            vals = sheet.Range(cell).Value
            
            if not isinstance(vals, (list, tuple)):
                return f"Range {cell} contains: {vals}"
                
            lines = []
            for row in vals:
                # Handle potential None values safely
                lines.append("\t".join(str(c) if c is not None else "" for c in row))
            
            output = "\n".join(lines)
            if len(output) > 4000:
                output = output[:4000] + "\n[...Truncated...]"
            return f"Range {cell} contains:\n{output}"
            
        elif action == "add_sheet":
            new_sheet = wb.Sheets.Add()
            if value: # use value as sheet name
                new_sheet.Name = value
            return f"Added and activated new sheet '{new_sheet.Name}'."
            
        elif action == "scroll_down":
            excel.ActiveWindow.LargeScroll(Down=1)
            return "Scrolled down one page in Excel."
            
        elif action == "scroll_up":
            excel.ActiveWindow.LargeScroll(Up=1)
            return "Scrolled up one page in Excel."
            
        elif action == "save":
            if file_path:
                wb.SaveAs(file_path)
                return f"Saved workbook to {file_path}"
            else:
                try:
                    wb.Save()
                    return "Saved workbook."
                except Exception:
                    return "Workbook has no existing path. Please provide a path in 'file_path' to save."
                    
        else:
            return f"Unknown action: '{action}'. Try: new, write_cell, read_cell, read_range, add_sheet, scroll_down, scroll_up, save."
            
    except Exception as e:
        return f"Excel control failed: {e}"
    finally:
        pythoncom.CoUninitialize()

# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
# TOOL block removed. Use office_suite.py facade instead.
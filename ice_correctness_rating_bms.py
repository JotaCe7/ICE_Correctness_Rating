import pandas as pd

from utils.utils import get_code, update_dataset_local_path, replace_show_with_savefig, save_script, execute_code
from globals import SHEETS, WORKBOOK_PATH, ID_COLUMN, CODE_COLUMN, FILENAME_COLUMN

def extract_and_save_scripts_from_sheets():
    """
    Process multiple sheets in an Excel workbook, extract code and save scripts.

    This function reads data from specified sheets, extracts code and dataset names,
    and saves Python scripts based on the extracted information.
    """
    for sheet_name in SHEETS:
        sheet = pd.read_excel(WORKBOOK_PATH, sheet_name=sheet_name, keep_default_na=False)
        print(sheet.head(20))
        
        for row_number, id in enumerate(sheet[ID_COLUMN]):
            row = sheet.iloc[row_number]
            code_column, dataset_name = row[CODE_COLUMN], row[FILENAME_COLUMN]
            
            if code_column:
                code = get_code(code_column)
                code = update_dataset_local_path(code, dataset_name)
                code = replace_show_with_savefig(code, id)
                save_script(code, id)
                execute_code(code, save_output=True, id=id)
            else:
                print(f"Skipping row {row_number} with no code.")


if __name__ == "__main__":
    # Call the main processing function when the script is executed
    extract_and_save_scripts_from_sheets()
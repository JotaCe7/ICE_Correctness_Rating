from io import StringIO
import pandas as pd
from contextlib import redirect_stdout, suppress
import sys
import traceback
import os

from globals import DATASETS_PATH, SCRIPTS_PATH, OUPUT_IMAGES_PATH, EXECUTION_OUTPUTS_PATH, EXECUTION_ERRORS_PATH

def get_code(model_a_response: str) -> str:
    """
    Extract code block from a text response.

    This function takes a text response, typically generated by a model,
    and extracts the code block within triple-backticks (```).

    Args:
        model_a_response (str): The text response containing code.

    Returns:
        str: The extracted code block.

    Example:
        response = 'Here is some text...\n```python\nprint("Hello, World!")\n``` More text...'
        code = get_code(response)
        print(code)  # Output: 'print("Hello, World!")'
    """
    code = ""
    is_code = False
    is_first_line = False

    for line in model_a_response.splitlines():
        if '```' not in line and not is_code:
            continue
        elif '```' in line and not is_code:
            is_code = True
            is_first_line = True
            continue
        elif '```' in line and is_code:
            is_code = False
            break
        else:
            code = code + ('' if is_first_line else '\n') + line
            is_first_line = False

    return code


def update_dataset_local_path(code: str, filename: str, datasets_path: str = DATASETS_PATH) -> str:
    """
    Update the dataset file path in the given code to use a local file path.

    Args:
        code (str): The code containing the dataset file path.
        filename (str): The name of the dataset file.
        datasets_path (str, optional): The local datasets path. Defaults to DATASETS_PATH.

    Returns:
        str: The updated code with the local file path.
    """
    # Create the full local path
    path = os.path.join(datasets_path, filename)

    # Iterate through each line in the code
    for line in code.splitlines():
        if '.csv' in line:
            quote_symbol = "'" if "'" in line else '"'
            start = line.find(quote_symbol)
            end = line.rfind(quote_symbol)
            wrong_path = line[start + 1: end]
            if len(wrong_path) > 0:
                # Replace the old dataset path with the new local path
                newline = line.replace(wrong_path, path)
                code = code.replace(line, newline)
                break

    return code


def save_script(code: str, id: str, scripts_path: str = SCRIPTS_PATH):
    """
    Save the provided code as a Python script file with the given ID.

    Args:
        code (str): The Python code to save.
        id (str): The ID to use as the filename (excluding the file extension '.py').
        scripts_path (str, optional): The directory path to save the script. Defaults to SCRIPTS_PATH.
    """
    # Create the full script file path
    script_path = os.path.join(scripts_path, id + '.py')

    # Write the code to the script file
    with open(script_path, 'w') as f:
        f.write(code)


def replace_show_with_savefig(code, id, output_images_path: str = OUPUT_IMAGES_PATH):
    """
    Replace instances of '.show()' with '.savefig()' in code to save images.

    This function takes code as input and replaces instances of '.show()' with '.savefig()' to save
    generated images to the specified output_images_path.

    Args:
        code (str): The code containing '.show()' that needs to be replaced.
        id (str): The ID to use as part of the image filename.
        output_images_path (str, optional): The directory path to save the images. Defaults to OUPUT_IMAGES_PATH.

    Returns:
        str: Code with '.show()' replaced by '.savefig()'.
    """
    if '.show()' in code:
        image_path = os.path.join(output_images_path, id + '.png')
        code = code.replace('.show()', '.savefig("' + image_path + '")')
    return code


def execute_code(code: str, save_output: bool = False, id="", execution_outputs_path: str = EXECUTION_OUTPUTS_PATH, execution_errors_path: str = EXECUTION_ERRORS_PATH):
    """
    Execute Python code and capture its output and errors.

    This function takes Python code as input, executes it, and captures both the standard output and any errors.
    It can optionally save the output and errors to files.

    Args:
        code (str): The Python code to execute.
        save_output (bool, optional): Whether to save the output and errors to files. Defaults to False.
        id (str, optional): An identifier used as part of the output and error filenames. Defaults to an empty string.
        execution_outputs_path (str, optional): The directory path to save the execution outputs. Defaults to EXECUTION_OUTPUTS_PATH.
        execution_errors_path (str, optional): The directory path to save the execution errors. Defaults to EXECUTION_ERRORS_PATH.

    Returns:
        str: The captured output or error message.
    """
    f = StringIO()
    error_found = False
    
    # Prepare file paths for saving output and errors
    if save_output:
        error_path = os.path.join(execution_errors_path, id + '_error.txt')
        output_path = os.path.join(execution_outputs_path, id + '_output.txt')

        # Remove existing error and output files if they exist
        with suppress(FileNotFoundError):
            os.remove(error_path)
        with suppress(FileNotFoundError):
            os.remove(output_path)

    # Redirect standard output to capture it
    with redirect_stdout(f):
        try:
            # Execute the provided Python code
            exec(code)
        except SyntaxError as err:
            # Handle syntax errors
            error_class = err.__class__.__name__
            detail = err.args[0]
            line_number = err.lineno
            error_found = True
        except Exception as err:
            # Handle other exceptions
            error_class = err.__class__.__name__
            detail = err.args[0]
            _, _, tb = sys.exc_info()
            line_number = traceback.extract_tb(tb)[1][1]
            error_found = True
            
    if error_found:
        # Prepare error description
        error_desc = f"{error_class} at line {line_number}: {detail}"
        if save_output:
            # Save error description to a file
            with open(error_path, 'w') as f:
                f.write(error_desc)                
        return error_desc
    else:
        # Capture and process the standard output
        output = f.getvalue()
        if save_output and output:
            # Save the standard output to a file
            with open(output_path, 'w') as f:
                f.write(output)
        return output


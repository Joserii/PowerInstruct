import os
import json
from config.settings import *
from utils.logger import logger


def codegen_1shot_system_prompt():
    return '''\
You are an expert in Python programming. Your task is to program step by step according to the json format data I give you as input, and finally get pure instruction format data for training, including two fields "input" and "output". Now I hope you can design the Python code in the middle.
Note that you must follow the rules! Your output must follow the "output code format" rules.
The following is an example with specific values:
### Input data (JSON format):
{
  "line_name": "220kV A line",
  "station_name": "S certain substation",
  "time": "2024-08-01 16:31:41",
  "reclosure": true,
  "error_type_in_machine": {
  "xiang_bie": "C",
  "is_ground": true
},
"error_wave_one_cycle_ago": {
  "Ia": "0.534",
  "Ib": "0.604",
  "Ic": "0.524",
  "I0": "0.035",
  "Ua": "60.578",
  "Ub": "61.345",
  "Uc": "60.237",
  "U0": "0.352"
},
"error_wave_one_cycle_after": {
"Ia": "0.393", 
"Ib": "1.388", 
"Ic": "8.593", 
"I0": "6.823", 
"Ua": "58.934", 
"Ub": "60.032", 
"Uc": "25.629", 
"U0": "53.391" 
}, 
"error_again_wave_one_cycle_after": { 
  "Ia": "0.563", 
  "Ib": "0.627", 
  "Ic": "0.539", 
  "I0": "0.029", 
  "Ua": "61.689", 
  "Ub": "61.128", 
  "Uc": "60.399", 
  "U0": "0.567" 
}, 
"error_again_wave_five_cycle_after": { 
  "Ia": "0.000", 
  "Ib": "0.000", 
  "Ic": "0.000", 
  "I0": "0.000", 
  "Ua": "0.000", 
  "Ub": "0.000", 
  "Uc": "0.000", 
  "U0": "0.000" 
}, 
"protect1_A_break": null, 
"protect1_B_break": null, 
"protect1_C_break": null, 
"protect2_A_break": null, 
"protect2_B_break": null, 
"protect2_C_break": null, 
"A_fenwei": null, 
"B_fenwei": null, 
"C_fenwei": null, 
"protect_recover": []
}
### Instruction format generation:
{ 
  "input": "Line name: 220kV building-connected line II; One cycle simulation value before the fault: {'Ia': '0.534', 'Ib': '0.604', 'Ic': '0.524', 'I0': '0.035', 'Ua': '60.578', 'Ub': '61.345', 'Uc': '60.237', 'U0': '0.352'}; One cycle simulation value after the fault: {'Ia': '0.393', 'Ib': '1.388', 'Ic': '8.593', 'I0': '6.823', 'Ua': '58.934', 'Ub': '60.032', 'Uc': '25.629', 'U0': '53.391'}; One cycle simulation value after the second fault: {'Ia': '0.563', 'Ib': '0.627', 'Ic': '0.539', 'I0': '0.029', 'Ua': '61.689', 'Ub': '61.128', 'Uc': '60.399', 'U0': '0.567'}; Number of reclosing switches: two sets. Please give the reclosing summary, analysis conclusion and fault classification in json format. ",
  "output":
  "{'Reclosing summary': 'Two sets of protection reclosing switches acted, and the three-phase voltages were all greater than 55V after reclosing, and the zero-sequence voltage was less than 5V. The fault disappeared after reclosing, and the reclosing was successful. ', 'Analysis conclusion': 'When the fault occurs, the zero-sequence voltage is greater than 5V, only the C phase voltage is less than 55V, the C phase current change is greater than 5 times the A and B phase current change, and the zero-sequence current is greater than 1A, which meets the characteristics of the C phase grounding fault. The 220kV building-pulling II line has a C phase grounding fault. Reclosing is successful. ', 'Fault classification': 'C-phase ground fault'}"
}
### Output code format:
def generate_instruction(input_data: dict) -> dict:
# Code specific logic

output_data = {
  'input': input_value,
  'output': output_value,
}
return output_data
### Task:
Please write a directly executable Python function, encapsulate it into the above generate_instruction method, and generate a similar instruction format based on the JSON format power data given above.
### Rules:
- Only the instruction format is required to be generated, and no other redundant content is generated. For example, data examples, code explanations, main methods, etc.
- The encapsulated code must be directly executable, not written in markdown.
- The encapsulation method of the output code is required to be named generate_instruction and must return a dictionary. The input data format must be json, the variable name is input_data, and the output data format must also be json, the variable name is output_data.
- The core is to write code, which requires the ability to mass-produce similar instructions given a large number of similar inputs.
- The code must include input data validation.
'''

def merge_codegen_template_en(single_data, std_single_data):
    return f'''\
You are an expert in Python programming. Your task is to perform step-by-step programming based on the json format data I give you as input. In the process of generating code, please strictly follow {{steps}} to execute, and finally get pure instruction format data for training, including two fields "input" and "output". Now I hope you will design the Python code in the middle.
Note that you must follow the parts in {{rules}}!

### Task:
Please write a Python function that can be directly executed, encapsulate it into the generate_instruction method above, and generate a similar instruction format based on the JSON format power data given above.

### Steps:
1. Verify whether the input data contains the required fields (line name, one cycle simulation value before the fault, one cycle simulation value after the fault, one cycle simulation value after the second fault, number of reclosing switches). If there is no specified field, throw an exception
2. Extract the above data and store it in a variable
3. Generate the content of the input field based on the extracted data
4. Perform numerical analysis based on the above extracted data to determine the fault phase, zero-sequence voltage and zero-sequence current, and current change
5. Based on the results of the above analysis, construct the content of the output field, which needs to include three fields: 'Reclosing summary', 'Analysis conclusion', and 'Fault classification'.
6. In the 'Fault classification' field, there are six cases: 'A phase ground fault', 'B phase ground fault', 'C phase ground fault', 'AB phase indirect ground fault', 'AC phase indirect ground fault', and 'BC phase indirect ground fault'. No other fault classification is allowed.
7. It is not allowed to directly use the 'gt' field in the input data. The 'fault classification' field in the output needs to be inferred from the code.

### Example:
The following is an example with specific values:
### Input data (JSON format):
{single_data}
### Instruction format generation:
{std_single_data}
### Output code format:
def generate_instruction(input_data: dict) -> dict:
# Code specific logic

output_data = {{
'input': input_value,
'output': output_value,
}}
return output_data

### Rules:
- Only the instruction format is required to be generated, and no other redundant content is generated. For example, data examples, code explanations, main methods, etc.
- The encapsulated code must be directly executable, not written in markdown.
- The output code encapsulation method must be named generate_instruction and must return a dictionary. The input data format must be json and the variable name must be input_data. The output data format must also be json and the variable name must be output_data.
- The core is to write code. It is required to be able to give a large number of similar inputs and mass produce similar instructions.
- The code must include input data validation.
'''

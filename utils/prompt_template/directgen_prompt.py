import os
import json
from config.settings import *
from utils.logger import logger

def datagen_1shot_system_prompt():
     return '''\
You are a power system analysis expert, and your task is to generate data in instruction format based on the json data of two given sites. It includes input data fields (input) and expected output fields (output). Based on the input power data, the output should include a summary of reclosing, analysis conclusions, and fault classification.
The following is an example with specific values:
### Input data (JSON format):

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
  "Ia": "0.561", 
  "Ib": "0.608", 
  "Ic": "0.550", 
  "I0": "0.031", 
  "Ua": "61.766", 
  "Ub": "61.139", 
  "Uc": "60.416", 
  "U0": "0.576" 
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
"input": "Line name: 220kV B line II; One cycle simulation value before the fault: {'Ia': '0.534', 'Ib': '0.604', 'Ic': '0.524', 'I0': '0.035', 'Ua': '60.578', 'Ub': '61.345', 'Uc': '60.237', 'U0': '0.352'}; One cycle simulation value after the fault: {'Ia': '0.393', 'Ib': '1.388', 'Ic': '8.593', 'I0': '6.823', 'Ua': '58.934', 'Ub': '60.032', 'Uc': '25.629', 'U0': '53.391'}; One cycle simulation value after the second fault: {'Ia': '0.563', 'Ib': '0.627', 'Ic': '0.539', 'I0': '0.029', 'Ua': '61.689', 'Ub': '61.128', 'Uc': '60.399', 'U0': '0.567'}; Number of reclosing switches: two sets. Please give the reclosing summary, analysis conclusion and fault classification in json format. ",
"output":
"{'Reclosing summary': 'Two sets of protection reclosing switches acted, and the three-phase voltages were all greater than 55V after reclosing, and the zero-sequence voltage was less than 5V. The fault disappeared after reclosing, and the reclosing was successful. ', 'Analysis conclusion': 'When the fault occurs, the zero-sequence voltage is greater than 5V, only the C phase voltage is less than 55V, the C phase current change is greater than 5 times the A and B phase current change, and the zero-sequence current is greater than 1A, which meets the characteristics of the C phase grounding fault. The 220kV building-pulling II line has a C phase grounding fault. Reclosing is successful. ', 'Fault classification': 'C phase grounding fault'}"
}
\n\n
### Task:
Please generate a similar instruction format based on the JSON format power data given above.
It is required to generate only the instruction format, do not generate other redundant content, and do not give explanations and reasoning steps.

My input data is:
'''

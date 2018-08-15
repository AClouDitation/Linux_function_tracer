# Linux Function Tracer
This tool is used to statically analyzing linux functions, 
reporting call paths of a specific group of functions, their Locations and # of SLOC
# USAGE

## main.py
main.py will first find all global functions and store them in *OUTPUTPATH/global_function_list.txt*
then, all driver folders will be searched by **ENTRY_RULE**

**PLESASE MODIFY THESE CONFIGS AT THE BEGINNEING OF *main.py* BEFORE RUNNING**
```python
# DESIRED ENTRY FUNCTION RULE
RULE = "YOUR RULE WITH REGULAR EXPRESSION"

# DIRS
VER = "4.4-rc6"
KERNEL_PATH = "YOUR_KERNEL_PATH/linux-" + VER
BUILD_PATH 	= os.path.join(KERNEL_PATH,"build/")
DRIVER_PATH = os.path.join(KERNEL_PATH,"build/drivers/")
OUTPUT_PATH = "./data_" + VER + "/"
```

## spfunc_tracer.py
spfunc_tracer can trace one specific function, reporting every 
function on its call path, with their location and SLoC

it takes 2 or 3 parameters
* $1:	function name
* $2:	object file path
* $3: ** not required, path name filter,
if there is $3, only functions with path including 
this keyword is counted

## find_ex.py
this script generates all exported symbol in given linux kernel

## find_datatype.py
this script finds all datatypes used in a given kernel

it takes one argument, the version number

please run main.py before running this


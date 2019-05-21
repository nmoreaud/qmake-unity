# No file deletion (you should set this variable to False after having check the path to deleted files...)
SAFE_MODE = True

# Print debug information to help you understand why a some files are not grouped.
# When you're done, please set this variable to False.
LOG_DEBUG = True

# List of namespace names that are allowed appear in a "using namespace XXX" expression in a group
# ex : NAMESPACE_WHITELIST = ["good::namespace"]
NAMESPACE_WHITELIST = []

# we let 1 more to avoid freezes
NB_PROCESSORS = 7 

# Number of files that will be mocced together (MOC_LVL_1 or MOC_LVL_2)
MOC_GROUPSIZE = 50

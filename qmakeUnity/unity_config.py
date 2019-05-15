# No file deletion
SAFE_MODE = True

# Print debug information about which file will be grouped
LOG_DEBUG = True

# List of namespace names that are allowed appear in a "using namespace XXX" expression in a group
NAMESPACE_WHITELIST = ["GoodNamespace"]

# we let 1 more to avoid freezes
NB_PROCESSORS = 7 

# nb files that will be mocced together
MOC_GROUPSIZE = 50

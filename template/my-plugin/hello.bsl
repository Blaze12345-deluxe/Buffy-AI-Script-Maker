VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Prints a friendly greeting using built-in variables."
OUTPUT = false

CLEAR

WRITE "========================================="
WRITE "  Hello from My Plugin"
WRITE "========================================="
WRITE ""
WRITE "  Hello, ${USER}!"
WRITE "  Welcome to the my-plugin package."
WRITE ""
WRITE "  Today is ${DATE}."
WRITE "  The time is ${TIME}."
WRITE ""
WRITE "  Your home directory is: ${HOME}"
WRITE "  Current directory is:   ${PWD}"
WRITE "  Temp directory is:      ${TEMP}"
WRITE ""
WRITE "-----------------------------------------"
WRITE "  System Info"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "uname -a"
OUTPUT = false
WRITE ""
WRITE "========================================="

EXIT

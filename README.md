# ipam
IPAM and widget Web Application for Internal Lab Environment

Created By: Brett Davis
This Web application was created for internal use and does not include authentication in version .01

This was created to run on Ubuntu 24.04 LTS

Requirements.txt will reflect the requirements for Ubuntu 24.04

If using this for another operating system, the requirements and code will change based on which repositories are available for that operating system.

Each Python Widget needs to have the following code included in order for it to be found by the widget manager in the /widgets/ folder:

#pythondef execute():
#    return {"title": "Widget Name", "data": {...}, "status": "success"}
#
#WIDGET_CONFIG = {
#    "display_name": "Display Name",
#    "tab_group": "Overview"  # Tab it appears in
#}

Uncomment the code after including it in the .py file for the widget.

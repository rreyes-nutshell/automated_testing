# oracle/locators.py

# Centralized Oracle UI element selectors
LOCATORS = {
    "User ID": "input[name='userid']",
    "Password": "input[name='password']",
    "Sign In Button": "button#btnActive",
    "Navigator": "a[title='Navigator']",
    "Tools Menu": "text='Tools'",
    "Scheduled Processes": "text='Scheduled Processes'",
    "Tools Menu ID": "#menu-tools",
}

# Optional legacy-style individual exports for old modules
USER_ID_SELECTOR = LOCATORS["User ID"]
PASSWORD_SELECTOR = LOCATORS["Password"]
SIGNIN_BUTTON_SELECTOR = LOCATORS["Sign In Button"]

__all__ = ["LOCATORS", "USER_ID_SELECTOR", "PASSWORD_SELECTOR", "SIGNIN_BUTTON_SELECTOR"]

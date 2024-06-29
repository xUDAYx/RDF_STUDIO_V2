import re

rules = {
    "rules": [
        {
            "description": "No HTML tag should be present",
            "pattern": "<html.*?>"
        },
        {
            "description": "No HEAD tag should be present",
            "pattern": "<head.*?>"
        },
        {
            "description": "No BODY tag should be present",
            "pattern": "<body.*?>"
        },
        {
            "description": "Div tag should be present only inside <td> tag",
            "pattern": "<td.?>.?<div.?>.?</td>"
        },
        {
            "description": "No div tag should be present outside <td> tag",
            "pattern": "<div.?>.?(?!</td>)"
        },
        {
            "description": "Table tag should be present",
            "pattern": "<table.*?>"
        }
    ]
}

def validate_html(content, rules):
    errors = []
    for rule in rules["rules"]:
        if re.search(rule["pattern"], content) is not None:
            if rule["description"] == "Table tag should be present":
                continue
            errors.append(f"Error: {rule['description']}")
        elif rule["description"] == "Table tag should be present":
            errors.append("Error: Table tag should be present")
    return errors

# Example HTML content
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
</head>
<body>
    <table>
        <tr>
            <td><div>Content</div></td>
        </tr>
    </table>
</body>
</html>
"""

# Validate the HTML content
errors = validate_html(html_content, rules)

if errors:
    for error in errors:
        print(error)
else:
    print("Code is OK")

#!/usr/bin/env python3

from typing import List, Dict
import argparse
import csv
import sys
import markdown
import urllib.parse


def read_csv(csv_path: str) -> List[Dict[str, str]]:
    """
    Read contacts from a CSV file and filter for rows with 'email' and 'name' columns.

    Args:
        csv_path (str): Path to the CSV file containing contact information

    Returns:
        list: List of dictionaries, each representing a contact with 'name' and 'email' keys
    """
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader if "email" in row and "name" in row]


def read_message(message_path: str) -> str:
    """
    Read the message template from a text file.

    Args:
        message_path (str): Path to the text file containing the message template

    Returns:
        str: The content of the message file as a string
    """
    with open(message_path, "r", encoding="utf-8") as f:
        return f.read()


def generate_mailto(
    email: str, subject: str, body: str, cc_list: List[str], use_html_body: bool = False
) -> str:
    """
    Generate a mailto URL with the specified parameters.

    Args:
        email (str): Recipient email address
        subject (str): Email subject line
        body (str): Email body content
        cc_list (list): List of CC email addresses
        use_html_body (bool): If True, use 'html-body' parameter instead of 'body'

    Returns:
        str: A properly formatted mailto URL with encoded parameters
    """
    params = {
        "subject": subject,
    }

    # Use html-body key if requested, otherwise use body key
    if use_html_body:
        params["html-body"] = body
    else:
        params["body"] = body

    if cc_list:
        params["cc"] = ",".join(cc_list)
    param_str = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    return f"mailto:{email}?{param_str}"


def main() -> None:
    """
    Main function that handles command-line argument parsing and orchestrates the mail merge
    process.

    Parses command-line arguments, validates required inputs, reads contacts and message template,
    generates personalized mailto links for each contact, and outputs the results as HTML either
    to a file or stdout.

    Exits with code 1 if required arguments are missing.
    """
    parser = argparse.ArgumentParser(
        description="Generate HTML file with mailto: links for mail merge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mailto-mail-merge.py --contacts contacts.csv --message message.txt \
    --subject "Subject Line" --output output.html
  python mailto-mail-merge.py --contacts contacts.csv --message message.txt \
    --subject "Subject Line" --output output.html --cc admin@company.com,manager@company.com
  python mailto-mail-merge.py --contacts contacts.csv --message message.md \
    --subject "Subject Line" --html-body
        """,
    )

    parser.add_argument(
        "--contacts",
        help='Path to CSV file containing contacts with "name" and "email" columns',
    )
    parser.add_argument(
        "--message",
        help="Path to text file containing message template (use {{name}} for personalization)",
    )
    parser.add_argument("--subject", help="Email subject line")
    parser.add_argument(
        "--output",
        help="Path for output HTML file (if not specified, output goes to stdout)",
    )
    parser.add_argument(
        "--cc",
        help="Comma-separated list of CC email addresses",
        default="",
    )
    parser.add_argument(
        "--html-body",
        action="store_true",
        help='Use "html-body" parameter instead of "body" in mailto links (works with '
        + "Thunderbird and some other clients); converts Markdown to HTML if the message file is .md",
    )

    args = parser.parse_args()

    # Check for required arguments and print custom error messages.
    missing_args = []
    if not args.contacts:
        missing_args.append("--contacts")
    if not args.message:
        missing_args.append("--message")
    if not args.subject:
        missing_args.append("--subject")

    if missing_args:
        print(
            f"Error: Missing required arguments: {', '.join(missing_args)}",
            file=sys.stderr,
        )
        print("Use --help for usage information.", file=sys.stderr)
        sys.exit(1)

    # Convert the CC string to list.
    cc_list = (
        [email.strip() for email in args.cc.split(",") if email.strip()]
        if args.cc
        else []
    )

    contacts = read_csv(args.contacts)
    message = read_message(args.message)

    # Convert Markdown to HTML if requested.
    if args.html_body:
        if args.message.endswith(".md"):
            message = markdown.markdown(message).replace(">\n<", "><")

    # Prepare the HTML output with CSS and JavaScript for click tracking.
    html_lines = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<meta charset='utf-8'>",
        "<title>Mail Merge Links</title>",
        "<style>",
        ".clicked { text-decoration: line-through; color: #666; }",
        ".mailto-item { margin: 10px 0; }",
        "</style>",
        "<script>",
        "function markClicked(element) {",
        "  element.classList.add('clicked');",
        "  // Store clicked state in localStorage",
        "  const clickedLinks = JSON.parse(localStorage.getItem('clickedMailtoLinks') || '[]');",
        "  const linkId = element.getAttribute('data-link-id');",
        "  if (!clickedLinks.includes(linkId)) {",
        "    clickedLinks.push(linkId);",
        "    localStorage.setItem('clickedMailtoLinks', JSON.stringify(clickedLinks));",
        "  }",
        "}",
        "",
        "function restoreClickedState() {",
        "  const clickedLinks = JSON.parse(localStorage.getItem('clickedMailtoLinks') || '[]');",
        "  clickedLinks.forEach(linkId => {",
        "    const element = document.querySelector(`[data-link-id='${linkId}']`);",
        "    if (element) {",
        "      element.classList.add('clicked');",
        "    }",
        "  });",
        "}",
        "",
        "window.onload = restoreClickedState;",
        "</script>",
        "</head>",
        "<body>",
        "<h1>Mailto Links</h1>",
        "<ul>",
    ]

    for i, contact in enumerate(contacts):
        name = contact["name"]
        email = contact["email"]

        personalized_message = message
        personalized_message = personalized_message.replace("{{Name}}", name)
        personalized_message = personalized_message.replace("{{name}}", name)

        mailto_link = generate_mailto(
            email, args.subject, personalized_message, cc_list, args.html_body
        )
        
        # Create unique ID for each link
        link_id = f"mailto-{i}-{email.replace('@', '-at-').replace('.', '-dot-')}"
        
        html_lines.append(
            f'<li class="mailto-item" data-link-id="{link_id}" onclick="markClicked(this)">'
            f'{name}: <a href="{mailto_link}">{email}</a></li>'
        )

    html_lines += ["</ul>", "</body>", "</html>"]

    # Output to file or stdout
    html_content = "\n".join(html_lines)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html_content)
    else:
        print(html_content)


if __name__ == "__main__":
    main()
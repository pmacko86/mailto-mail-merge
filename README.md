# Mailto Mail Merge

Generate personalized `mailto:` links for a list of contacts using a message template.

## Features

- Supports CSV contact lists
- Customizable message templates (plain text or HTML)
- Optional CC recipients
- Output as HTML file with clickable mailto links

## Usage

1. **Prepare your contacts CSV file**
    Example (`contacts.csv`):
    ```csv
    name,email
    John Doe,john@example.com
    Jane Smith,jane@example.com
    ```

2. **Create a message template**
    Example (`message.txt`):
    ```
    Hello {{name}},
    This is a personalized message for you.
    ```

3. **Run the script**
    ```bash
    python mailto-mail-merge.py --contacts contacts.csv --message message.txt \
      --subject "Your Subject Here" --output output.html
    ```

4. **View the generated HTML file**

    The output file will contain `mailto:` links for each contact.

5. **Use HTML body (optional)**
    ```bash
    python mailto-mail-merge.py --contacts contacts.csv --message message.txt \
      --subject "Your Subject Here" --output output.html --html-body
    ```

6. **Add CC recipients (optional)**
    ```bash
    python mailto-mail-merge.py --contacts contacts.csv --message message.txt \
      --subject "Your Subject Here" --output output.html --cc "cc@example.com"
    ```

7. **Use a different message format, e.g., Markdown (optional)**
    ```bash
    python mailto-mail-merge.py --contacts contacts.csv --message message.md \
      --subject "Your Subject Here" --output output.html --html-body
    ```

## Creating a Python virtual environment for running the program

1. **Create a virtual environment**
    ```bash
    python3 -m venv venv
    ```

2. **Activate the virtual environment**

    - On macOS/Linux:
      ```bash
      source venv/bin/activate
      ```
    - On Windows:
      ```bash
      venv\Scripts\activate
      ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

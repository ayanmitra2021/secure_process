# Secure Data Masking & Cloud Upload Tool

This tool is a Python-based automation script designed to mask sensitive data within Excel inventory files based on configurable JSON rules and securely upload the result to cloud storage (AWS S3 or Google Cloud Platform).

## 🚀 Features

*   **Rule-Based Masking:** Define masking logic in a JSON file (no code changes required).
*   **Flexible Strategies:** Supports random strings, fake IPs, static values, zeroing numbers, and date overrides.
*   **Conditional Logic:** Apply masking only when specific conditions are met (e.g., *only mask email if Environment == Production*).
*   **Multi-Cloud Support:** Uploads directly to **AWS S3** or **GCP Cloud Storage**.
*   **Excel Integration:** Native reading and writing of `.xlsx` files.

## 📋 Prerequisites

*   Python 3.8+
*   Pip (Python Package Manager)

## 🛠️ Installation

1.  **Clone the repository** (or download the script):
    ```bash
    git clone https://github.com/your-username/your-repo.git
    cd your-repo
    ```

2.  **Install dependencies**:
    Create a `requirements.txt` file (if not present) and run the install command.

    ```bash
    pip install pandas openpyxl boto3 google-cloud-storage faker
    ```

## ⚙️ Configuration

The behavior of the script is controlled entirely by `config.json`.

### Structure

Create a `config.json` file in the root directory:

```json
{
  "files": {
    "input_file": "server_inventory.xlsx",
    "output_file": "masked_inventory.xlsx"
  },
  "cloud": {
    "target": "aws", 
    "bucket_name": "my-backup-bucket",
    "destination_path": "uploads/monthly/",
    "region": "us-east-1",
    "aws_access_key": "YOUR_KEY", 
    "aws_secret_key": "YOUR_SECRET",
    "gcp_key_path": "./gcp-service-account.json"
  },
  "masking_rules": [
    {
      "column": "Server_Name",
      "type": "text",
      "strategy": "random_string"
    },
    {
      "column": "IP_Address",
      "type": "ip",
      "strategy": "fake_ip"
    },
    {
      "column": "Owner_Email",
      "type": "text",
      "strategy": "conditional",
      "condition_col": "Environment",
      "condition_val": "Production",
      "mask_value": "admin@company.com",
      "else_action": "keep"
    }
  ]
}
```

### Supported Masking Strategies

| Strategy | Description | Example Output |
| :--- | :--- | :--- |
| `random_string` | Replaces text with random characters | `xKj9Lz` |
| `fake_ip` | Generates a valid random IPv4 address | `192.168.4.21` |
| `zero` | Sets numeric fields to 0 | `0` |
| `static` | Sets the field to a fixed value defined in config | `REDACTED` |
| `current_date` | Sets date fields to today's date | `2023-10-27` |
| `invert` | Flips boolean values | `False` -> `True` |
| `conditional` | Masks based on another column's value | (See JSON example) |

## 🏃 Usage

The script operates in two modes: `mask` and `upload`.

### 1. Masking Data
Reads the input Excel file, applies rules, and generates the output file.

```bash
python secure_process.py mask --config config.json
```

### 2. Uploading Data
Takes the masked output file and uploads it to the configured cloud provider.

```bash
python secure_process.py upload --config config.json
```

## ☁️ Cloud Setup

### AWS S3
Set `target` to `"aws"`. You can provide keys in the JSON file, or better yet, leave the keys empty in JSON and set environment variables:
*   `AWS_ACCESS_KEY_ID`
*   `AWS_SECRET_ACCESS_KEY`

### Google Cloud (GCP)
Set `target` to `"gcp"`.
1.  Download your Service Account JSON key.
2.  Point to it using `"gcp_key_path"` in the config file.

## ⚠️ Security Note

**Do not commit real API keys or passwords to GitHub.**
If using this in a public repository:
1.  Add `config.json` to your `.gitignore` file.
2.  Use a template config file (e.g., `config.example.json`) with placeholder values.

## 🐛 Troubleshooting

**Error: "Python was not found"**
If you see this error on Windows despite installing Python:
1.  Type "Manage app execution aliases" in the Windows Start menu.
2.  Turn **OFF** the toggles for `python.exe` and `python3.exe`.

## 📜 License

[MIT](https://choosealicense.com/licenses/mit/)
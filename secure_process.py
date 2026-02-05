
import argparse
import json
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime
from faker import Faker

# Cloud Libraries
try:
    import boto3
    from botocore.exceptions import NoCredentialsError
except ImportError:
    pass # Handle in logic if missing

try:
    from google.cloud import storage
except ImportError:
    pass

fake = Faker()

class DataProcessor:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.input_file = self.config['files']['input_file']
        self.output_file = self.config['files']['output_file']

    # --- MASKING LOGIC ---
    def _generate_mask_value(self, rule, current_value, row=None):
        strategy = rule.get('strategy')
        
        # 1. Conditional Logic
        if strategy == 'conditional':
            cond_col = rule.get('condition_col')
            cond_val = rule.get('condition_val')
            
            # Check condition (assuming simple equality for this example)
            if row[cond_col] == cond_val:
                return rule.get('mask_value')
            else:
                return current_value if rule.get('else_action') == 'keep' else 'REDACTED'

        # 2. IP Address
        if strategy == 'fake_ip':
            return fake.ipv4()

        # 3. Text Strategies
        if strategy == 'random_string':
            return fake.lexify(text='??????')
        if strategy == 'static':
            return rule.get('value', 'REDACTED')

        # 4. Number Strategies
        if strategy == 'zero':
            return 0
        if strategy == 'random_int':
            return fake.random_int(min=0, max=100)

        # 5. Date Strategies
        if strategy == 'current_date':
            return datetime.now().strftime("%Y-%m-%d")

        # 6. Boolean Strategies
        if strategy == 'invert':
            return not bool(current_value)

        return "MASKED"

    def mask_data(self):
        print(f"[*] Reading data from {self.input_file}...")
        try:
            df = pd.read_excel(self.input_file)
        except FileNotFoundError:
            print(f"[!] Error: Input file {self.input_file} not found.")
            sys.exit(1)

        rules = self.config['masking_rules']
        
        print("[*] Applying masking rules...")
        
        # We iterate through rules, then apply them to the dataframe
        for rule in rules:
            col = rule['column']
            if col in df.columns:
                print(f"    - Masking column: {col} (Strategy: {rule['strategy']})")
                
                # Apply mask row-by-row to handle conditionals dependent on other columns
                df[col] = df.apply(
                    lambda row: self._generate_mask_value(rule, row[col], row), 
                    axis=1
                )
            else:
                print(f"    [!] Warning: Column '{col}' found in config but not in Excel file.")

        print(f"[*] Saving masked data to {self.output_file}...")
        df.to_excel(self.output_file, index=False)
        print("[+] Masking complete.")

    # --- UPLOAD LOGIC ---
    def upload_data(self):
        cloud_conf = self.config['cloud']
        provider = cloud_conf.get('target', '').lower()
        bucket_name = cloud_conf.get('bucket_name')
        file_path = self.output_file
        dest_path = cloud_conf.get('destination_path', '') + os.path.basename(file_path)

        if not os.path.exists(file_path):
            print(f"[!] Error: File {file_path} does not exist. Run 'mask' first.")
            sys.exit(1)

        print(f"[*] Starting upload to {provider.upper()} Bucket: {bucket_name}...")

        if provider == 'aws':
            self._upload_to_aws(file_path, bucket_name, dest_path, cloud_conf)
        elif provider == 'gcp':
            self._upload_to_gcp(file_path, bucket_name, dest_path, cloud_conf)
        else:
            print(f"[!] Error: Unknown cloud provider '{provider}'. Use 'aws' or 'gcp'.")

    def _upload_to_aws(self, local_file, bucket, s3_file, conf):
        try:
            # Initialize S3 client (Use keys from config or env vars)
            s3 = boto3.client(
                's3',
                aws_access_key_id=conf.get('aws_access_key'),
                aws_secret_access_key=conf.get('aws_secret_key'),
                region_name=conf.get('region', 'us-east-1')
            )
            s3.upload_file(local_file, bucket, s3_file)
            print(f"[+] Upload Successful to S3: s3://{bucket}/{s3_file}")
        except Exception as e:
            print(f"[!] AWS Upload failed: {e}")

    def _upload_to_gcp(self, local_file, bucket_name, gcs_blob_name, conf):
        try:
            # Set credential file path environment variable
            key_path = conf.get('gcp_key_path')
            if key_path:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
            
            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(gcs_blob_name)
            
            blob.upload_from_filename(local_file)
            print(f"[+] Upload Successful to GCP: gs://{bucket_name}/{gcs_blob_name}")
        except Exception as e:
            print(f"[!] GCP Upload failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Excel Data Masking and Cloud Upload Tool")
    parser.add_argument("mode", choices=["mask", "upload"], help="Mode of operation")
    parser.add_argument("--config", default="config.json", help="Path to JSON configuration file")
    
    args = parser.parse_args()
    
    processor = DataProcessor(args.config)
    
    if args.mode == "mask":
        processor.mask_data()
    elif args.mode == "upload":
        processor.upload_data()

if __name__ == "__main__":
    main()
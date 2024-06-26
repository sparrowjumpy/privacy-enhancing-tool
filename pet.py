import pandas as pd
import random
from cryptography.fernet import Fernet
from PIL import Image, ExifTags
import argparse
import os

def generate_pseudonyms(dataframe, column):
    unique_names = dataframe[column].unique()
    pseudonyms = {name: f"User{random.randint(1000, 9999)}" for name in unique_names}
    dataframe[column] = dataframe[column].map(pseudonyms)
    return dataframe

def generate_key():
    return Fernet.generate_key()

def encrypt_message(message, key):
    f = Fernet(key)
    return f.encrypt(message.encode()), key

def decrypt_message(encrypted_message, key):
    f = Fernet(key)
    return f.decrypt(encrypted_message).decode()

def get_metadata(image_path):
    """Retrieve and print metadata of an image."""
    with Image.open(image_path) as img:
        exif_data = img._getexif()
        exif = {ExifTags.TAGS.get(key): val for key, val in exif_data.items()} if exif_data else {}
    return exif

def remove_metadata(image_path, output_path):
    with Image.open(image_path) as img:
        data = img.getdata()
        clean_img = Image.new(img.mode, img.size)
        clean_img.putdata(data)
        clean_img.save(output_path, "JPEG")
    return get_metadata(output_path)

def main():
    parser = argparse.ArgumentParser(description='Privacy Enhancer Tool (PET)')
    parser.add_argument('--anonymize', help='Path to the CSV file for data anonymization', type=str)
    parser.add_argument('--encrypt', help='Text to encrypt', type=str)
    parser.add_argument('--decrypt', help='Encrypted text to decrypt', type=str)
    parser.add_argument('--key', help='Encryption/Decryption key', type=str)
    parser.add_argument('--clean_image', help='Path to the image for metadata cleaning', type=str)
    parser.add_argument('--output_image', help='Path for saving the cleaned image', type=str)

    args = parser.parse_args()

    if args.anonymize:
        df = pd.read_csv(args.anonymize)
        df_anonymized = generate_pseudonyms(df, 'Name')
        print("Anonymized Data:")
        print(df_anonymized)
        df_anonymized.to_csv('anonymized_data.csv', index=False)
        print("Anonymized data saved to 'anonymized_data.csv'.")

    if args.encrypt:
        encrypted, key = encrypt_message(args.encrypt, generate_key())
        print("Encrypted Message:", encrypted.decode())
        print("Encryption Key (save this to decrypt):", key.decode())

    if args.decrypt and args.key:
        decrypted = decrypt_message(args.decrypt.encode(), args.key.encode())
        print("Decrypted Message:", decrypted)

    if args.clean_image and args.output_image:
        original_metadata = get_metadata(args.clean_image)
        print("Original Metadata:")
        print(original_metadata)
        cleaned_metadata = remove_metadata(args.clean_image, args.output_image)
        print(f"Metadata from {args.clean_image} has been cleaned and saved to {args.output_image}")
        print("Cleaned Metadata:")
        print(cleaned_metadata)

if __name__ == "__main__":
    main()

import requests
import csv
from google import genai

# Gemini API key
GEMINI_API_KEY = "AIzaSyC_UYJdaED_LSlHJqzSbk_z6mciNv-LSvM"

# Input CSV file
INPUT_CSV = "NeurIPS_Papers.csv"
# Output CSV file
OUTPUT_CSV = "NeurIPS_Papers_Labeled.csv"

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

def get_pdf_label(pdf_url):
    """Pass the PDF link to Gemini API and get the specific label."""
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Label this PDF: {pdf_url}",
            labels=["Deep Learning", "Computer Vision", "Reinforcement Learning", "NLP", "Optimization"]
        )
        label = response["choices"][0]["text"].strip()
        return label
    except Exception as e:
        print(f"Error labeling PDF {pdf_url}: {e}")
        return "Labeling failed"

def main():
    print("Starting annotator...")

    # Open input CSV file for reading
    with open(INPUT_CSV, mode="r", newline="", encoding="utf-8") as infile:
        csv_reader = csv.reader(infile)
        headers = next(csv_reader)  # Skip header row

        # Open output CSV file for writing
        with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as outfile:
            csv_writer = csv.writer(outfile)
            csv_writer.writerow(["Serial Number", "PDF Link", "Label"])

            for row in csv_reader:
                serial_number = row[0]
                pdf_url = row[3]
                label = get_pdf_label(pdf_url)
                csv_writer.writerow([serial_number, pdf_url, label])

    print("Labeled CSV file created successfully!")

if __name__ == "__main__":
    main()

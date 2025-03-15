import os
import sys
import json
import datetime
import re

def sanitize_filename(title, max_length=50):
    """Remove special characters except spaces, keep capitalization, and truncate filename."""
    title = re.sub(r'[^\w\s-]', '', title).strip()  # Remove special characters
    if len(title) > max_length:
        title = title[:max_length].rsplit(' ', 1)[0]  # Truncate while keeping whole words
    return title

def clean_text(text):
    """Clean body text by removing unwanted characters."""
    text = text.replace("&amp;#x200B;", "").strip()  # Remove zero-width space
    text = text.replace("&amp;amp;#x200B;", "").strip()
    text = text.replace("&amp;", "&")  # Replace HTML-encoded ampersand with "&"
    return text

def convert_json_to_md(json_folder, md_folder, template_path):
    # Ensure output directory exists
    os.makedirs(md_folder, exist_ok=True)

    # Load Markdown template
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Counters for output summary
    total_files = 0
    skipped_existing = 0
    skipped_empty = 0
    converted = 0

    # Process each JSON file in the folder
    for filename in os.listdir(json_folder):
        if filename.endswith(".json"):
            total_files += 1
            json_path = os.path.join(json_folder, filename)

            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            # Extract relevant data from JSON
            try:
                post_data = json_data[0]["data"]["children"][0]["data"]
                title = post_data.get("title", "Untitled")
                title = clean_text(title)
                body = clean_text(post_data.get("selftext", ""))  # Clean body text

                # Skip conversion if body is empty, "[deleted]", or "[removed]"
                if body in ["", "[deleted]", "[removed]"]:
                    print(f"Skipping {filename}: Empty or removed content")
                    skipped_empty += 1
                    continue

                created_utc = post_data.get("created_utc", 0)
                created_date = datetime.datetime.utcfromtimestamp(created_utc)
                created_str = created_date.strftime('%Y-%m-%d')
                year_str = created_date.strftime('%Y')

                clean_title = sanitize_filename(title)
                md_filename = f"{clean_title}.md"
                md_path = os.path.join(md_folder, md_filename)

                # Skip conversion if Markdown file already exists
                if os.path.exists(md_path):
                    print(f"Skipping {md_filename}: File already exists")
                    skipped_existing += 1
                    continue

                replacements = {
                    "{{permalink}}": post_data.get("permalink", ""),
                    "{{subreddit}}": post_data.get("subreddit", ""),
                    "{{created}}": created_str,
                    "{{year}}": year_str,
                    "{{title}}": title,
                    "{{body}}": body,
                }

                # Replace tokens in the template
                md_content = template
                for token, value in replacements.items():
                    md_content = md_content.replace(token, value)

                # Save as Markdown
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)

                print(f"Converted {filename} to {md_filename}")
                converted += 1

            except (KeyError, IndexError):
                print(f"Skipping {filename}: Unexpected JSON format")

    # Final summary output
    print("\nSummary:")
    print(f"📂 Total JSON files processed: {total_files}")
    print(f"✅ Successfully converted: {converted}")
    print(f"⚠️ Skipped (existing files): {skipped_existing}")
    print(f"🚫 Skipped (empty or removed content): {skipped_empty}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python convert_json_to_md.py <json_folder> <md_folder> <template_path>")
        sys.exit(1)

    json_folder = sys.argv[1]
    md_folder = sys.argv[2]
    template_path = sys.argv[3]

    convert_json_to_md(json_folder, md_folder, template_path)

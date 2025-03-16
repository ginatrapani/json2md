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
    text = text.replace("&gt;", ">").strip()
    return text

def find_post_by_id(data, post_id):
    """
    Recursively searches for a post by its ID within a nested JSON structure.

    :param data: The JSON data (list or dictionary).
    :param post_id: The post ID to find.
    :return: The matching post data if found, otherwise None.
    """
    if isinstance(data, dict):
        # If the current dictionary has the 'id' key and matches post_id, return it
        if data.get("id") == post_id:
            return data
        # Otherwise, recursively check all values
        for value in data.values():
            result = find_post_by_id(value, post_id)
            if result:
                return result

    elif isinstance(data, list):
        # Iterate through the list and search recursively
        for item in data:
            result = find_post_by_id(item, post_id)
            if result:
                return result
    return None  # Return None if not found

def convert_json_to_md(json_folder, md_folder, file_template, post_template):
    # Ensure output directory exists
    os.makedirs(md_folder, exist_ok=True)

    # Load Markdown template
    with open(file_template, 'r', encoding='utf-8') as f:
        file_template = f.read()

    # Load Markdown template
    with open(post_template, 'r', encoding='utf-8') as f:
        post_template = f.read()

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
                orig_post_data = json_data[0]["data"]["children"][0]["data"]
                orig_post_title = orig_post_data.get("title", "Untitled")
                orig_post_title = clean_text(orig_post_title)
                orig_post_body = clean_text(orig_post_data.get("selftext", ""))  # Clean body text

                if orig_post_body in ["", "[deleted]", "[removed]"]:
                    orig_post_body = "Original post deleted."

                created_utc = orig_post_data.get("created_utc", 0)
                created_date = datetime.datetime.utcfromtimestamp(created_utc)
                created_str = created_date.strftime('%Y-%m-%d')
                year_str = created_date.strftime('%Y')

                clean_title = sanitize_filename(orig_post_title)
                # The name of the file is the ID of the post to save
                post_to_save = filename.replace(".json", "")
                filename_is_post_id = bool(re.fullmatch(r"[A-Za-z0-9]{7}", post_to_save))
                if ( filename_is_post_id ):
                    md_filename = f"{clean_title}-{post_to_save}.md"
                else:
                    md_filename = f"{clean_title}-OP.md"
                md_path = os.path.join(md_folder, md_filename)

                # Skip conversion if Markdown file already exists
                if os.path.exists(md_path):
                    print(f"Skipping {md_filename}: File already exists")
                    skipped_existing += 1
                    continue

                saved_post_md_content = ""
                saved_post_permalink = ""
                if ( filename_is_post_id ):
                    found_post = find_post_by_id(json_data, post_to_save)
                    if (found_post):
                        # print(f"Post {post_to_save} found")
                        body = clean_text(found_post.get("body", ""))  # Clean body text

                        # Skip if body is empty, "[deleted]", or "[removed]"
                        if body in ["", "[deleted]", "[removed]"]:
                            skipped_empty += 1
                            print(f"Skipping {post_to_save}: Empty or removed post to save")
                            continue

                        created_utc = found_post.get("created_utc", 0)
                        created_date = datetime.datetime.utcfromtimestamp(created_utc)
                        created_str = created_date.strftime('%Y-%m-%d')
                        year_str = created_date.strftime('%Y')

                        # Generate markdown content for the found post
                        saved_post_permalink = "https://reddit.com" + found_post.get("permalink", "")
                        found_post_replacements = {
                            "{{saved_author}}": found_post.get("author", ""),
                            "{{saved_permalink}}": saved_post_permalink,
                            "{{saved_body}}" : body,
                            "{{saved_created_time}}" : created_str
                        }

                        # Replace tokens in the template
                        saved_post_md_content = post_template
                        for token, value in found_post_replacements.items():
                            saved_post_md_content = saved_post_md_content.replace(token, value)
                    else:
                        print(f"Post {post_to_save} not found")

                    # Skip conversion if saved post not found AND OP body is deleted
                    if ( found_post is None ):
                        print(f"Skipping {filename}: Empty or removed content")
                        skipped_empty += 1
                        continue

                replacements = {
                    "{{op_permalink}}": "https://reddit.com" + orig_post_data.get("permalink", ""),
                    "{{saved_permalink}}": saved_post_permalink,
                    "{{subreddit}}": orig_post_data.get("subreddit", ""),
                    "{{post_id}}" : post_to_save,
                    "{{op_created}}": created_str,
                    "{{year}}": year_str,
                    "{{title}}": orig_post_title,
                    "{{op_body}}": orig_post_body,
                    "{{saved_post}}": saved_post_md_content
                }

                # Replace tokens in the template
                md_content = file_template
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
    if len(sys.argv) != 5:
        print("Usage: python json2md.py <json_folder> <md_folder> <file_template_path> <post_template_path>")
        sys.exit(1)

    json_folder = sys.argv[1]
    md_folder = sys.argv[2]
    file_template = sys.argv[3]
    post_template = sys.argv[4]

    convert_json_to_md(json_folder, md_folder, file_template, post_template)

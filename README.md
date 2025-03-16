# JSON to Markdown Converter

This Python script converts a folder of `.json` files into Markdown `.md` files using a specified template.

I built it to convert Reddit post data into Obsidian-friendly Markdown files, but it's easily adaptable for any JSON source data.

## 🛠 Features
- Extracts Reddit post data from JSON and formats it into Markdown.
- Uses a template where `{{token}}` placeholders are replaced with actual values.
- Skips empty or removed posts.
- Avoids overwriting existing Markdown files.
- Cleans up unnecessary characters in post content.
- Truncates filenames to 50 characters while keeping words intact.
- Outputs a summary of processed, skipped, and converted files.
- Can include the original post and a saved or upvoted reply in the output.

## 📌 Usage

### **1️⃣ Install Python**
Ensure Python 3 is installed on your system.

### **2️⃣ Prepare Your Files**
- Place the `.json` files in a folder.
- Create a Markdown template for each file (`template.md`).
- Create a Markdown template for a post inside the file. (`template.post.md`).
- Prepare an output folder for the Markdown files.

### **3️⃣ Run the Script**
Use the following command:

```sh
python json2md.py <json_folder> <md_folder> <file_template> <post_template>
```

### **Example**
```sh
python json2md.py ./json_files ./markdown_output ./template.md ./template.post.md
```

### **4️⃣ Explanation of Parameters**
| Parameter        | Description                                       |
|-----------------|---------------------------------------------------|
| `<json_folder>` | Path to the folder containing JSON files.        |
| `<md_folder>`   | Path to the folder where Markdown files go.      |
| `<file_template>` | Path to the Markdown file template file.         |
| `<post_template>` | Path to the Markdown post template file.         |

## 📝 Markdown Template Format
Your template file (`template.md`) should include placeholders like:

```markdown
---
original post: {{op_permalink}}
saved post: {{saved_permalink}}
subreddit: {{subreddit}}
created: {{op_created}}
---
# {{title}}

{{op_body}}

{{saved_post}}
```

Your post template (`template.post.md`) should include placeholders like:

```markdown
## Saved Comment

{{saved_body}}

[By {{saved_author}} on {{saved_created_time}}]({{saved_permalink}})
```

## 📊 Output Summary
After running, the script prints a summary:

```sh
📂 Total JSON files processed: 100
✅ Successfully converted: 85
⚠️ Skipped (existing files): 10
🚫 Skipped (empty or removed content): 5
```

## 📌 Notes
- If the script encounters unexpected JSON structures, it skips them.
- If `<json_folder>` contains non-JSON files, they are ignored.
- If `<md_folder>` doesn't exist, it will be created.

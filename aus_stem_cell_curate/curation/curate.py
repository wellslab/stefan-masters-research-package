import json
import os
import tempfile
import base64
import io
from pathlib import Path
from openai import OpenAI
from pdf2image import convert_from_bytes
from PIL import Image

def load_config() -> dict:
    """Load configuration from config.json file."""
    config_path = Path(__file__).parent / "config.json"
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Allow environment variable to override config file API key
    if "OPENAI_API_KEY" in os.environ:
        config["openai_api_key"] = os.environ["OPENAI_API_KEY"]
    
    return config


def convert_pdf_to_images(pdf_bytes: bytes, max_pages: int = 10) -> list:
    """
    Convert PDF bytes to a list of base64-encoded images.
    
    Args:
        pdf_bytes: PDF file as bytes
        max_pages: Maximum number of pages to convert (default: 10)
    
    Returns:
        List of base64-encoded image strings
    """
    try:
        # Convert PDF to PIL images
        images = convert_from_bytes(pdf_bytes, first_page=1, last_page=max_pages)
        
        base64_images = []
        for image in images:
            # Convert PIL image to base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            base64_images.append(img_base64)
        
        return base64_images
    
    except Exception as e:
        raise Exception(f"Failed to convert PDF to images: {str(e)}")


def curate_article(article: bytes, config_override: dict = None) -> str:
        
    # Loads configuration for the curation request to the model
    config = load_config()
    
    # Override with custom config if provided
    if config_override:
        config.update(config_override)
    
    api_key = config["openai_api_key"]
    model_name = config["model"]
    temperature = config["temperature"]
    max_tokens = config["max_tokens"]
    processing_method = config.get("processing_method", "vision")  # Default to vision

    # Check processing method and prepare article data accordingly
    if processing_method == "vision":
        # Convert PDF to images for vision processing
        try:
            article_images = convert_pdf_to_images(article)
        except Exception as e:
            return f"Error converting PDF to images: {str(e)}"
    else:
        # For transcription method (to be implemented later)
        return "Transcription method not yet implemented"

    # Gets all the unique cell lines reported in the article
    get_cell_line_names_prompt = """
    You are a knowledgeable and helpful assistant who has academic knowledge in the stem cell research domain.
    You are given an article that describes the generation / derivation of a number of stem cell lines.
    You are to read the article and return a python list of unique stem cell line names mentioned in the article.
    Your output should just be a python list containing the unique names. Do not include any additional commentary.
    
    Example output for three unique stem cell lines: [AIBNi001, AIBNi002, MCRIi001-A]
    
    If there are no cell lines created in the experiment of the article, someone has given you the wrong article, 
    In this case, just return -1.
        
    """
    unique_cell_lines = []
    try:
        client = OpenAI(api_key=api_key)
        
        # Create message content with images
        message_content = [{"type": "text", "text": get_cell_line_names_prompt}]
        
        # Add each page as an image
        for i, img_base64 in enumerate(article_images):
            message_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img_base64}"}
            })
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": message_content}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        result = response.choices[0].message.content
        
        # Parse the result to extract cell line names
        if "-1" in result or "no cell lines" in result.lower():
            return -1
        
        # Extract cell lines from code block or direct list
        import ast
        try:
            # Try to find a Python list in the response
            if "```python" in result:
                # Extract content between ```python and ```
                start = result.find("```python") + 9
                end = result.find("```", start)
                list_str = result[start:end].strip()
            else:
                list_str = result.strip()
            
            # Parse the list
            unique_cell_lines = ast.literal_eval(list_str)
            
            if not isinstance(unique_cell_lines, list):
                return f"Error: Expected list but got {type(unique_cell_lines)}"
                
        except Exception as e:
            return f"Error parsing cell line list: {str(e)}"

    except Exception as e:
        return str(e)
    
    
    # Result objects that user will receive 
    structured_outputs = dict()
    failed_cell_line_names = []
    
    
    
    # Send curation requests for each unique cell line reported in the paper
    for cell_line in unique_cell_lines:
        success = False
        max_retries = 3
        for attempt in range(max_retries):
            
            # Send curation request for the cell line...
            response = curate_line(article, cell_line, config)
            
            # Check if response looks like an error 
            if not response.startswith("Error") and not response.startswith("Exception") and len(response) > 50:
                # Appears to be a successful response
                structured_outputs[cell_line] = response
                success = True
                break
            
            # If this was the last attempt and still failed
            if attempt == max_retries - 1:
                failed_cell_line_names.append(cell_line)


    # Return results with failed cell lines info
    return {
        "curated_data": structured_outputs,
        "failed_cell_lines": failed_cell_line_names,
        "total_cell_lines": len(unique_cell_lines),
        "successful_curations": len(structured_outputs)
    }


def curate_line(article: bytes, cell_line: str, config_override: dict = None) -> str:
    
    # Load config for this function
    config = load_config()
    
    # Override with custom config if provided
    if config_override:
        config.update(config_override)
    
    api_key = config["openai_api_key"]
    model_name = config["model"]
    temperature = config["temperature"]
    max_tokens = config["max_tokens"]
    processing_method = config.get("processing_method", "vision")

    # Check processing method and prepare article data accordingly
    if processing_method == "vision":
        # Convert PDF to images for vision processing
        try:
            article_images = convert_pdf_to_images(article)
        except Exception as e:
            return f"Error converting PDF to images: {str(e)}"
    else:
        # For transcription method (to be implemented later)
        return "Transcription method not yet implemented"
    
    # Load curation instructions from markdown file
    instructions_path = Path(__file__).parent / "curation_instructions.md"
    with open(instructions_path, "r") as f:
        curation_instructions = f.read()
    
    try:
        client = OpenAI(api_key=api_key)
        
        system_prompt = f"""You are a knowledgeable assistant trained to retrieve stem cell line metadata from research literature. 
You are only curating metadata for the cell line with the name {cell_line}. 
Ignore metadata for any other cell line.
You must respond with a JSON string containing the metadata for this cell line. 
Wrap the JSON response in a JSON codeblock. Your output should not have any other commentary.
Here are the detailed curation instructions you must follow:
{curation_instructions}"""
        
        # Create message content with images
        user_content = [{"type": "text", "text": f"Please extract metadata for the cell line '{cell_line}' from this research article:"}]
        
        # Add each page as an image
        for i, img_base64 in enumerate(article_images):
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img_base64}"}
            })
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return str(e)
    
    

    
    
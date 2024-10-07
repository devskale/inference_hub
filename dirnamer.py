import os
import json
import asyncio
import argparse
from fnamer import read_file_content, get_model_provider

async def process_file(file_path, provider, model, mode):
    content = read_file_content(file_path, 1200)  # Read first 1000 characters
    result = await provider.analyze(content, mode)
    return {
        "file_name": os.path.basename(file_path),
        "analysis_mode": mode,
        "provider": provider.__class__.__name__,
        "model": model,
        "result": result
    }

def load_existing_results(results_file):
    if os.path.exists(results_file):
        with open(results_file, "r") as f:
            return json.load(f)
    return {"processed_files": []}

def update_results(existing_results, new_result, provider, model):
    file_name = new_result["file_name"]
    for i, result in enumerate(existing_results["processed_files"]):
        if (result["file_name"] == file_name and 
            result["provider"] == provider.__class__.__name__ and
            result["model"] == model):
            existing_results["processed_files"][i] = new_result
            return
    existing_results["processed_files"].append(new_result)

def find_eligible_files(directory, tag, max_depth=2):
    eligible_files = []
    for root, dirs, files in os.walk(directory):
        depth = root[len(directory):].count(os.sep)
        if depth > max_depth:
            continue
        for file in files:
            if file.endswith(".md") and tag.lower() in file.lower():
                eligible_files.append(os.path.join(root, file))
    return eligible_files

async def process_directory(directory, provider, model_name, mode, tag, nummax=None):
    results_file = os.path.join(directory, "analysis_results.json")
    existing_results = load_existing_results(results_file)
    
    eligible_files = find_eligible_files(directory, tag)
    total_files = min(len(eligible_files), nummax) if nummax else len(eligible_files)

    for index, file_path in enumerate(eligible_files[:total_files], start=1):
        filename = os.path.basename(file_path)
        relative_path = os.path.relpath(file_path, directory)
        
        print(f"\nAnalyzing {index}/{total_files} {relative_path} with {provider.__class__.__name__}({model_name}):")
        
        result = await process_file(file_path, provider, model_name, mode)
        update_results(existing_results, result, provider, model_name)
        print(f"Result: {result['result']}\n")
        # add a wait here to avoid rate limiting
        await asyncio.sleep(2)

    existing_results["total_files"] = len(existing_results["processed_files"])
    existing_results["provider"] = provider.__class__.__name__
    existing_results["model"] = model_name
    existing_results["mode"] = mode
    existing_results["tag"] = tag

    with open(results_file, "w") as f:
        json.dump(existing_results, f, indent=2)

    return existing_results, results_file

async def main():
    parser = argparse.ArgumentParser(description="Process Markdown files in a directory and subdirectories using fnamer.")
    parser.add_argument("directory", help="Directory containing Markdown files")
    parser.add_argument("--provider", choices=['huggingface', 'ollama', 'openai', 'google'], default='ollama', help="Choose the model provider")
    parser.add_argument("--model", help="Specify the model name for the chosen provider")
    parser.add_argument("--mode", choices=['s', 'k'], default='s', help="Analysis mode: 's' for summary, 'k' for classification")
    parser.add_argument("-n", "--nummax", type=int, help="Maximum number of files to process")
    parser.add_argument("-tag", default="llama", help="Tag to filter filenames (default: llama)")
    args = parser.parse_args()

    provider, model_name = await get_model_provider(args.provider, args.model)
    await provider.setup()

    results, results_file = await process_directory(args.directory, provider, model_name, args.mode, args.tag, args.nummax)

    print(f"Analysis complete. Results saved to {results_file}")
    print(f"Total files processed this run: {min(args.nummax, results['total_files']) if args.nummax else results['total_files']}")
    print(f"Tag used for filtering: {args.tag}")

if __name__ == "__main__":
    asyncio.run(main())
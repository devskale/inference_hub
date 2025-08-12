#!/usr/bin/env python3
"""
Kriterien JSON Parser

A tool to parse and analyze criteria from JSON files.
Usage: python kriterien.py -f kriterien.json --pop NUM --tree
"""

import argparse
import json
import sys
from typing import Dict, List, Any, Optional
from collections import defaultdict


def load_kriterien(file_path: str) -> Dict[str, Any]:
    """Load criteria from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{file_path}': {e}")
        sys.exit(1)


def get_unproven_kriterien(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get all criteria that haven't been proven yet (status is null)."""
    unproven = []
    for kriterium in data.get('kriterien', []):
        pruefung = kriterium.get('pruefung', {})
        if pruefung.get('status') is None:
            unproven.append(kriterium)
    return unproven


def display_kriterien_list(kriterien: List[Dict[str, Any]], limit: Optional[int] = None):
    """Display a list of criteria with basic information."""
    if limit is not None:
        kriterien = kriterien[:limit]
    
    if not kriterien:
        print("No unproven criteria found.")
        return
    
    print(f"\nFound {len(kriterien)} unproven criteria:")
    print("=" * 80)
    
    for i, kriterium in enumerate(kriterien, 1):
        print(f"{i:2d}. ID: {kriterium['id']}")
        print(f"    Typ: {kriterium['typ']}")
        print(f"    Kategorie: {kriterium['kategorie']}")
        print(f"    Name: {kriterium['name']}")
        print(f"    Quelle: {kriterium['quelle']}")
        print(f"    Status: Unproven")
        print("-" * 80)


def build_kriterien_tree(data: Dict[str, Any]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """Build a tree structure of criteria organized by typ and kategorie."""
    tree = defaultdict(lambda: defaultdict(list))
    
    for kriterium in data.get('kriterien', []):
        typ = kriterium.get('typ', 'Unknown')
        kategorie = kriterium.get('kategorie', 'Unknown')
        tree[typ][kategorie].append(kriterium)
    
    return dict(tree)


def display_kriterien_tree(data: Dict[str, Any]):
    """Display criteria in a tree structure organized by typ and kategorie."""
    tree = build_kriterien_tree(data)
    
    print("\nKriterien Tree (sorted by Typ and Kategorie):")
    print("=" * 80)
    
    for typ in sorted(tree.keys()):
        print(f"\n📁 Typ: {typ}")
        print("-" * 40)
        
        for kategorie in sorted(tree[typ].keys()):
            kriterien_list = tree[typ][kategorie]
            unproven_count = sum(1 for k in kriterien_list if k.get('pruefung', {}).get('status') is None)
            proven_count = len(kriterien_list) - unproven_count
            
            print(f"  📂 Kategorie: {kategorie}")
            print(f"     Total: {len(kriterien_list)}, Unproven: {unproven_count}, Proven: {proven_count}")
            
            # Show unproven criteria in this category
            unproven_in_cat = [k for k in kriterien_list if k.get('pruefung', {}).get('status') is None]
            if unproven_in_cat:
                print(f"     Unproven criteria:")
                for kriterium in unproven_in_cat:
                    print(f"       • {kriterium['id']}: {kriterium['name']}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description="Parse and analyze criteria from JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python kriterien.py -f kriterien/lampen/kriterienv3simple.json --pop 5
  python kriterien.py -f kriterien/lampen/kriterienv3simple.json --tree
  python kriterien.py -f kriterien/lampen/kriterienv3simple.json --pop 3 --tree
        """
    )
    
    parser.add_argument(
        '-f', '--file',
        required=True,
        help='Path to the JSON criteria file'
    )
    
    parser.add_argument(
        '--pop',
        type=int,
        default=1,
        help='Number of next unproven criteria to show (default: 1)'
    )
    
    parser.add_argument(
        '--tree',
        action='store_true',
        help='Show criteria tree sorted by typ and kategorie'
    )
    
    args = parser.parse_args()
    
    # Load the criteria data
    data = load_kriterien(args.file)
    
    # Get unproven criteria
    unproven_kriterien = get_unproven_kriterien(data)
    
    if args.tree:
        # Show tree view
        display_kriterien_tree(data)
        
        # Also show the requested number of unproven criteria
        if unproven_kriterien:
            print(f"\nNext {args.pop} unproven criteria:")
            display_kriterien_list(unproven_kriterien, args.pop)
        else:
            print("\nNo unproven criteria found.")
    else:
        # Show only the requested number of unproven criteria
        display_kriterien_list(unproven_kriterien, args.pop)
        
        # Show summary
        total_kriterien = len(data.get('kriterien', []))
        proven_count = total_kriterien - len(unproven_kriterien)
        print(f"\nSummary: {total_kriterien} total criteria, {proven_count} proven, {len(unproven_kriterien)} unproven")


if __name__ == "__main__":
    main()
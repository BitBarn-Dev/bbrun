import os
import json
from pathlib import Path
import datetime
import shutil

class ScriptManager:
    def __init__(self):
        self.scripts_dir = Path.home() / '.python_executor' / 'scripts'
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize with default categories
        self.load_categories()

    def add_version(self, filepath, content, metadata):
        """Add a new version to an existing script"""
        if not filepath or not os.path.exists(filepath):
            return False

        try:
            # Load existing data
            with open(filepath, 'r') as f:
                script_data = json.load(f)
            
            versions = script_data.get('versions', [])
            current_metadata = script_data.get('metadata', {})
            
            # Update metadata
            current_metadata.update(metadata)
            current_metadata['last_modified'] = datetime.datetime.now().isoformat()
            current_metadata['current_version'] = len(versions) + 1
            
            # Create new version
            new_version = {
                'content': content,
                'timestamp': datetime.datetime.now().isoformat(),
                'version_number': len(versions) + 1
            }
            
            # Add new version
            versions.append(new_version)
            
            # Save updated data
            script_data = {
                'metadata': current_metadata,
                'versions': versions
            }
            
            with open(filepath, 'w') as f:
                json.dump(script_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error adding version: {e}")
            return False        

    def load_categories(self):
        """Load existing categories from directory structure"""
        self.categories = ['Utility', 'System', 'Network', 'Database', 'Other']
        
        # Add any existing custom categories from directory structure
        for item in self.scripts_dir.iterdir():
            if item.is_dir() and item.name not in self.categories:
                self.categories.append(item.name)

    def script_exists(self, name, category):
        """Check if a script with the given name exists in the specified category"""
        safe_name = self._make_safe_filename(name)
        script_path = self.scripts_dir / category / f"{safe_name}.json"
        return script_path.exists()

    def _make_safe_filename(self, name):
        """Create a safe filename from the given name"""
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        return safe_name if safe_name else 'untitled'

    def add_category(self, category):
        """Add a new category"""
        if category not in self.categories:
            self.categories.append(category)
            (self.scripts_dir / category).mkdir(exist_ok=True)

    def save_script(self, name, content, metadata):
        """
        Save script with versioning support.
        Returns the filepath of the saved script.
        """
        # Create safe filename from name
        safe_name = self._make_safe_filename(name)
            
        # Ensure category exists
        category = metadata.get('category', 'Other')
        category_dir = self.scripts_dir / category
        category_dir.mkdir(exist_ok=True)
        
        # Prepare the script file path
        script_file = category_dir / f"{safe_name}.json"
        
        # Load existing versions if they exist
        versions = []
        if script_file.exists():
            try:
                with open(script_file, 'r') as f:
                    existing_data = json.load(f)
                    versions = existing_data.get('versions', [])
            except json.JSONDecodeError:
                # Handle corrupted file
                versions = []
        
        # Create new version
        new_version = {
            'content': content,
            'timestamp': datetime.datetime.now().isoformat(),
            'version_number': len(versions) + 1
        }
        
        # Add new version to versions list
        versions.append(new_version)
        
        # Update metadata
        metadata.update({
            'name': safe_name,
            'category': category,
            'last_modified': datetime.datetime.now().isoformat(),
            'created': metadata.get('created', datetime.datetime.now().isoformat()),
            'current_version': len(versions)
        })
        
        # Create complete script data
        script_data = {
            'metadata': metadata,
            'versions': versions
        }
        
        # Save to file
        try:
            with open(script_file, 'w') as f:
                json.dump(script_data, f, indent=2)
            return str(script_file)
        except Exception as e:
            print(f"Error saving script: {e}")
            return None

    def load_script(self, filepath, version=None):
        """
        Load a script and optionally a specific version.
        Returns (content, metadata, versions)
        """
        if not os.path.exists(filepath):
            return None, None, None
            
        try:
            with open(filepath, 'r') as f:
                script_data = json.load(f)
        except Exception as e:
            print(f"Error loading script {filepath}: {e}")
            return None, None, None
            
        versions = script_data.get('versions', [])
        metadata = script_data.get('metadata', {})
        
        if version is None:
            version = metadata.get('current_version', len(versions))
        
        if versions and 1 <= version <= len(versions):
            content = versions[version - 1]['content']
        else:
            content = ''
            
        return content, metadata, versions

    def list_scripts(self, category=None):
        """
        List all scripts, optionally filtered by category.
        Returns list of (filepath, metadata) tuples.
        """
        scripts = []
        
        if category:
            categories = [category]
        else:
            categories = self.categories
            
        for cat in categories:
            cat_dir = self.scripts_dir / cat
            if cat_dir.exists():
                for file in cat_dir.glob('*.json'):
                    try:
                        with open(file, 'r') as f:
                            script_data = json.load(f)
                            scripts.append((str(file), script_data['metadata']))
                    except Exception as e:
                        print(f"Error reading script {file}: {e}")
                        continue
                        
        return scripts

    def get_script_versions(self, filepath):
        """Get all versions of a script"""
        if not os.path.exists(filepath):
            return []
            
        try:
            with open(filepath, 'r') as f:
                script_data = json.load(f)
                return script_data.get('versions', [])
        except Exception as e:
            print(f"Error reading versions from {filepath}: {e}")
            return []